"""CLI & Desktop HUD entrypoint for AGY-HUD."""

import argparse
import os
import signal
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.hud_pill import HudPill, fmt_count, fmt_tps
from desktop.telemetry import TelemetryStore


def run_once(store: TelemetryStore) -> int:
    """Print the latest conversation telemetry once and return an exit code."""
    snap = store.read_snapshot()
    if not snap:
        print("No active Antigravity conversations found.")
        return 1

    print("\n" + "=" * 58)
    print("           AGY-HUD TOKEN/S & CONTEXT TELEMETRY")
    print("=" * 58)
    print(f"  Conversation ID : {snap.conversation_id}")
    print(f"  Active Model    : {snap.model_name}")
    print(f"  Recorded Turns  : {snap.turn_count}")
    print("-" * 58)
    if snap.is_buffered:
        print(f"  Gen Speed       : BUF ({snap.stream_sec * 1000:.0f}ms, {snap.output_tokens} tok)")
    else:
        print(f"  Gen Speed       : {fmt_tps(snap.gen_tps)} tok/s ({snap.stream_sec:.2f}s)")
    print(f"  E2E Speed       : {fmt_tps(snap.e2e_tps)} tok/s (TTFT {snap.ttft_sec:.2f}s)")
    print(f"  Session Avg/Peak: {fmt_tps(snap.avg_gen_tps)} / {fmt_tps(snap.peak_gen_tps)} tok/s")
    print("-" * 58)
    print(f"  Cached Context  : {snap.cached_tokens:>10,} tok ({fmt_count(snap.cached_tokens)})")
    print(f"  New Input       : {snap.input_tokens:>10,} tok ({fmt_count(snap.input_tokens)})")
    print(f"  Thought / Output: {snap.output_tokens:>10,} tok (Thk {fmt_count(snap.thinking_tokens)} / Out {fmt_count(snap.visible_tokens)})")
    print("-" * 58)
    print(f"  Total Context   : {snap.context_used:>10,} / {snap.context_limit:,} tok ({snap.usage_pct:.2f}%)")
    print("=" * 58 + "\n")
    return 0


def run_watch(store: TelemetryStore, interval: float = 1.0):
    """Stream telemetry lines whenever new turns land."""
    print("Watching Antigravity telemetry... (Ctrl+C to stop)\n")
    last_turns = -1
    try:
        while True:
            snap = store.read_snapshot()
            if snap and snap.turn_count != last_turns:
                last_turns = snap.turn_count
                gen_str = f"BUF {snap.stream_sec * 1000:.0f}ms" if snap.is_buffered else f"{fmt_tps(snap.gen_tps)} t/s"
                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"{snap.model_name.upper()} | "
                    f"GEN {gen_str} | E2E {fmt_tps(snap.e2e_tps)} t/s | TTFT {snap.ttft_sec:.2f}s | "
                    f"CTX {fmt_count(snap.context_used)}/{fmt_count(snap.context_limit)} ({snap.usage_pct:.1f}%) | "
                    f"#{snap.turn_count}"
                )
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def run_gui(refresh_ms: int = 500, alpha: float = 0.92, lang: str = "en"):
    """Launch the floating Tkinter HUD pill."""
    app = HudPill(store=TelemetryStore(), interval_ms=refresh_ms, topmost=True, alpha=alpha, lang=lang)

    def _on_signal(_sig, _frame):
        try:
            app.root.destroy()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)
    app.run()


def main():
    parser = argparse.ArgumentParser(description="AGY-HUD Token/s & Context Telemetry")
    parser.add_argument("--cli", action="store_true", help="Print snapshot once and exit")
    parser.add_argument("--watch", action="store_true", help="Stream live telemetry lines")
    parser.add_argument("--interval", type=float, default=1.0, help="Watch polling interval in seconds")
    parser.add_argument("--alpha", type=float, default=0.92, help="GUI opacity (0.3 to 1.0)")
    parser.add_argument("--refresh-ms", type=int, default=500, help="GUI refresh interval in ms")
    parser.add_argument("--lang", choices=["en", "zh"], default="en", help="Initial GUI language")

    args = parser.parse_args()
    if args.cli:
        sys.exit(run_once(TelemetryStore()))
    elif args.watch:
        run_watch(TelemetryStore(), interval=args.interval)
    else:
        run_gui(refresh_ms=args.refresh_ms, alpha=args.alpha, lang=args.lang)


if __name__ == "__main__":
    main()

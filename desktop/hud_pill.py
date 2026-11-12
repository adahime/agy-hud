"""Frameless dark-theme Tkinter floating HUD pill for AGY-HUD."""

import tkinter as tk
from typing import Dict, Optional, Tuple
from .telemetry import ConversationSnapshot, TelemetryStore


LANG_PACK: Dict[str, Dict[str, object]] = {
    "en": {
        "connecting": "AGY-HUD: Connecting...",
        "waiting": "AGY-HUD: Waiting...",
        "gen_live": "GEN {sec:.1f}s",
        "buf_pill": "E2E {e2e} · STR {sust} t/s",
        "buf_pill_only": "E2E {e2e} t/s",
        "norm_pill": "{gen} tok/s",
        "row_gen": "Gen TPS:",
        "row_e2e": "E2E (w/ TTFT):",
        "row_session": "Avg / Peak:",
        "row_cached": "Cached Ctx:",
        "row_input": "New Input:",
        "row_output": "Thk / Out:",
        "row_total": "Total Ctx:",
        "val_gen_buf": "BUF {ms:.0f}ms ({tok} tok)",
        "val_gen_ok": "{tps} tok/s ({sec:.2f}s)",
        "val_e2e": "{tps} tok/s (TTFT {ttft:.2f}s)",
        "val_session": "{avg} avg · {peak} peak",
        "val_out_split": "{total:,} (Thk {thk} / Out {vis})",
        "menu_toggle": "Expand / Collapse",
        "menu_topmost": "Always on Top",
        "menu_pin": "Pin Position",
        "menu_lang": "Language",
        "menu_opacity": "Opacity",
        "menu_refresh": "Refresh Rate",
        "menu_exit": "Exit",
        "refresh_opts": [(500, "0.5s (Live)"), (1000, "1s (Fast)"), (2000, "2s (Balanced)"), (5000, "5s (Low)")],
    },
    "zh": {
        "connecting": "AGY-HUD: 连接中...",
        "waiting": "AGY-HUD: 等待对话...",
        "gen_live": "生成中 {sec:.1f}s",
        "buf_pill": "E2E {e2e} · 流 {sust} t/s",
        "buf_pill_only": "E2E {e2e} t/s",
        "norm_pill": "{gen} tok/s",
        "row_gen": "生成速度 (Gen):",
        "row_e2e": "端到端 (含TTFT):",
        "row_session": "会话均速 / 峰值:",
        "row_cached": "缓存上下文:",
        "row_input": "新增输入:",
        "row_output": "思考 / 输出:",
        "row_total": "总上下文窗口:",
        "val_gen_buf": "缓冲 {ms:.0f}ms ({tok} tok)",
        "val_gen_ok": "{tps} tok/s ({sec:.2f}s)",
        "val_e2e": "{tps} tok/s (TTFT {ttft:.2f}s)",
        "val_session": "{avg} 均 · {peak} 峰",
        "val_out_split": "{total:,} (思 {thk} / 出 {vis})",
        "menu_toggle": "展开 / 折叠详情",
        "menu_topmost": "始终置顶 (Always on Top)",
        "menu_pin": "锁定位置 (Pin)",
        "menu_lang": "语言 (Language)",
        "menu_opacity": "透明度 (Opacity)",
        "menu_refresh": "刷新频率 (Refresh)",
        "menu_exit": "关闭 (Exit)",
        "refresh_opts": [(500, "0.5 秒 (实时)"), (1000, "1 秒 (极速)"), (2000, "2 秒 (平衡)"), (5000, "5 秒 (低占用)")],
    },
}


def fmt_count(n: int) -> str:
    """Format large integer token counts with k / M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def fmt_tps(tps: float) -> str:
    """Format token/s speed cleanly."""
    if tps <= 0:
        return "--"
    return f"{tps:.1f}" if tps >= 10 else f"{tps:.2f}"


class HudPill:
    """Floating always-on-top HUD widget backed by TelemetryStore."""

    BG_PILL = "#18181b"
    BG_CARD = "#27272a"
    BORDER = "#3f3f46"
    FG_MAIN = "#f4f4f5"
    FG_MUTED = "#a1a1aa"
    FG_DIM = "#71717a"

    OK = "#22c55e"
    WARN = "#eab308"
    CRIT = "#ef4444"
    ACCENT = "#3b82f6"
    LIVE = "#06b6d4"

    def __init__(
        self,
        store: Optional[TelemetryStore] = None,
        interval_ms: int = 500,
        topmost: bool = True,
        alpha: float = 0.92,
        lang: str = "en",
    ):
        self.store = store or TelemetryStore()
        self.interval_ms = interval_ms
        self.topmost = topmost
        self.alpha = alpha
        self.lang = lang if lang in LANG_PACK else "en"
        self.expanded = False
        self.pinned = False
        self._drag_x = 0
        self._drag_y = 0
        self.current_snapshot: Optional[ConversationSnapshot] = None
        self.row_key_labels: Dict[str, tk.Label] = {}
        self.menu: Optional[tk.Menu] = None

        self.root = tk.Tk()
        self.root.title("AGY-HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", self.topmost)
        self.root.attributes("-alpha", self.alpha)
        self.root.configure(bg=self.BORDER)

        init_x = max(50, self.root.winfo_screenwidth() - 360)
        self.root.geometry(f"+{init_x}+60")

        self._init_widgets()
        self._bind_interactions()
        self._rebuild_menu()
        self._poll_loop()

    def _txt(self, key: str) -> object:
        return LANG_PACK[self.lang][key]

    def _init_widgets(self):
        self.frame_outer = tk.Frame(self.root, bg=self.BORDER, padx=1, pady=1)
        self.frame_outer.pack(fill="both", expand=True)

        self.frame_body = tk.Frame(self.frame_outer, bg=self.BG_PILL)
        self.frame_body.pack(fill="both", expand=True)

        self.header = tk.Frame(self.frame_body, bg=self.BG_PILL, padx=10, pady=6)
        self.header.pack(fill="x")

        self.dot_canvas = tk.Canvas(self.header, width=12, height=12, bg=self.BG_PILL, highlightthickness=0)
        self.dot_canvas.pack(side="left", padx=(0, 6))
        self.dot_id = self.dot_canvas.create_oval(2, 2, 10, 10, fill=self.OK, outline="")

        self.pill_label = tk.Label(
            self.header,
            text=str(self._txt("connecting")),
            font=("Segoe UI", 9, "bold"),
            fg=self.FG_MAIN,
            bg=self.BG_PILL,
        )
        self.pill_label.pack(side="left", padx=2)

        self.chevron = tk.Label(
            self.header,
            text="▾",
            font=("Segoe UI", 10, "bold"),
            fg=self.FG_MUTED,
            bg=self.BG_PILL,
            cursor="hand2",
        )
        self.chevron.pack(side="right", padx=(6, 0))

        self.card = tk.Frame(self.frame_body, bg=self.BG_CARD, padx=12, pady=10)

        self.model_label = tk.Label(
            self.card,
            text="Model: --",
            font=("Segoe UI", 8, "bold"),
            fg=self.ACCENT,
            bg=self.BG_CARD,
            anchor="w",
        )
        self.model_label.pack(fill="x", pady=(0, 2))

        self.conv_label = tk.Label(
            self.card,
            text="ID: --",
            font=("Consolas", 7),
            fg=self.FG_DIM,
            bg=self.BG_CARD,
            anchor="w",
        )
        self.conv_label.pack(fill="x", pady=(0, 6))

        self.bar_canvas = tk.Canvas(self.card, height=8, bg=self.BG_PILL, highlightthickness=0)
        self.bar_canvas.pack(fill="x", pady=(0, 8))
        self.bar_rect = self.bar_canvas.create_rectangle(0, 0, 0, 8, fill=self.OK, outline="")

        self.metrics_box = tk.Frame(self.card, bg=self.BG_CARD)
        self.metrics_box.pack(fill="x")

        self.val_gen = self._make_row("row_gen", "--")
        self.val_e2e = self._make_row("row_e2e", "--")
        self.val_session = self._make_row("row_session", "--")
        self.val_cached = self._make_row("row_cached", "0")
        self.val_input = self._make_row("row_input", "0")
        self.val_output = self._make_row("row_output", "0")
        self.val_total = self._make_row("row_total", "0")

    def _make_row(self, key: str, initial: str) -> tk.Label:
        key_lbl, val_lbl = self._build_pair(self.metrics_box, str(self._txt(key)), initial)
        self.row_key_labels[key] = key_lbl
        return val_lbl

    def _build_pair(self, parent: tk.Widget, left: str, right: str) -> Tuple[tk.Label, tk.Label]:
        row = tk.Frame(parent, bg=self.BG_CARD, pady=1)
        row.pack(fill="x")
        k_lbl = tk.Label(row, text=left, font=("Segoe UI", 8), fg=self.FG_MUTED, bg=self.BG_CARD, anchor="w")
        k_lbl.pack(side="left")
        v_lbl = tk.Label(row, text=right, font=("Segoe UI", 8, "bold"), fg=self.FG_MAIN, bg=self.BG_CARD, anchor="e")
        v_lbl.pack(side="right")
        return k_lbl, v_lbl

    def _bind_interactions(self):
        for w in (self.header, self.pill_label, self.dot_canvas):
            w.bind("<Button-1>", self._drag_begin)
            w.bind("<B1-Motion>", self._drag_move)
        self.chevron.bind("<Button-1>", lambda _e: self.toggle_expand())
        self.pill_label.bind("<Double-Button-1>", lambda _e: self.toggle_expand())
        for w in (self.root, self.frame_outer, self.frame_body, self.header, self.pill_label, self.card):
            w.bind("<Button-3>", self._popup_menu)

    def _drag_begin(self, event):
        if not self.pinned:
            self._drag_x = event.x
            self._drag_y = event.y

    def _drag_move(self, event):
        if not self.pinned:
            nx = self.root.winfo_x() + (event.x - self._drag_x)
            ny = self.root.winfo_y() + (event.y - self._drag_y)
            self.root.geometry(f"+{nx}+{ny}")

    def _rebuild_menu(self):
        if self.menu is not None:
            self.menu.destroy()
        m = tk.Menu(self.root, tearoff=0, bg=self.BG_CARD, fg=self.FG_MAIN, activebackground=self.ACCENT)
        m.add_command(label=str(self._txt("menu_toggle")), command=self.toggle_expand)
        m.add_separator()

        self.var_top = tk.BooleanVar(value=self.topmost)
        m.add_checkbutton(label=str(self._txt("menu_topmost")), variable=self.var_top, command=self._apply_topmost)
        self.var_pin = tk.BooleanVar(value=self.pinned)
        m.add_checkbutton(label=str(self._txt("menu_pin")), variable=self.var_pin, command=self._apply_pin)
        m.add_separator()

        lang_sub = tk.Menu(m, tearoff=0, bg=self.BG_CARD, fg=self.FG_MAIN, activebackground=self.ACCENT)
        self.var_lang = tk.StringVar(value=self.lang)
        lang_sub.add_radiobutton(label="EN (English)", variable=self.var_lang, value="en", command=lambda: self.set_lang("en"))
        lang_sub.add_radiobutton(label="中文 (Chinese)", variable=self.var_lang, value="zh", command=lambda: self.set_lang("zh"))
        m.add_cascade(label=str(self._txt("menu_lang")), menu=lang_sub)

        op_sub = tk.Menu(m, tearoff=0, bg=self.BG_CARD, fg=self.FG_MAIN, activebackground=self.ACCENT)
        for val in (1.0, 0.85, 0.7, 0.5):
            op_sub.add_command(label=f"{int(val * 100)}%", command=lambda v=val: self._apply_alpha(v))
        m.add_cascade(label=str(self._txt("menu_opacity")), menu=op_sub)

        rate_sub = tk.Menu(m, tearoff=0, bg=self.BG_CARD, fg=self.FG_MAIN, activebackground=self.ACCENT)
        for ms, text in self._txt("refresh_opts"):  # type: ignore[misc]
            rate_sub.add_command(label=text, command=lambda v=ms: self._apply_rate(v))
        m.add_cascade(label=str(self._txt("menu_refresh")), menu=rate_sub)
        m.add_separator()

        m.add_command(label=str(self._txt("menu_exit")), command=self.root.destroy)
        self.menu = m

    def _popup_menu(self, event):
        if self.menu is not None:
            self.menu.post(event.x_root, event.y_root)

    def _apply_topmost(self):
        self.topmost = self.var_top.get()
        self.root.attributes("-topmost", self.topmost)

    def _apply_pin(self):
        self.pinned = self.var_pin.get()

    def _apply_alpha(self, alpha: float):
        self.alpha = alpha
        self.root.attributes("-alpha", alpha)

    def _apply_rate(self, ms: int):
        self.interval_ms = ms

    def set_lang(self, lang: str):
        """Switch UI language between 'en' and 'zh' immediately."""
        if lang not in LANG_PACK:
            return
        self.lang = lang
        for key, lbl in self.row_key_labels.items():
            lbl.configure(text=str(self._txt(key)))
        self._rebuild_menu()
        self._render(self.current_snapshot)
        self.root.update_idletasks()

    def toggle_expand(self):
        """Toggle compact pill vs expanded breakdown card."""
        self.expanded = not self.expanded
        if self.expanded:
            self.card.pack(fill="both", expand=True)
            self.chevron.configure(text="▴")
        else:
            self.card.pack_forget()
            self.chevron.configure(text="▾")
        self.root.update_idletasks()

    def _render(self, snap: Optional[ConversationSnapshot]):
        if not snap:
            self.dot_canvas.itemconfig(self.dot_id, fill=self.FG_DIM)
            self.pill_label.configure(text=str(self._txt("waiting")), fg=self.FG_MUTED)
            return

        pct = snap.usage_pct
        ctx_color = self.OK if pct < 50.0 else (self.WARN if pct < 80.0 else self.CRIT)
        dot_color = self.LIVE if snap.is_generating else ctx_color
        self.dot_canvas.itemconfig(self.dot_id, fill=dot_color)

        if snap.is_generating:
            speed = str(self._txt("gen_live")).format(sec=snap.active_elapsed_sec)
        elif snap.is_buffered:
            e2e = fmt_tps(snap.e2e_tps)
            if snap.last_sustained_tps > 0:
                speed = str(self._txt("buf_pill")).format(e2e=e2e, sust=fmt_tps(snap.last_sustained_tps))
            else:
                speed = str(self._txt("buf_pill_only")).format(e2e=e2e)
        else:
            speed = str(self._txt("norm_pill")).format(gen=fmt_tps(snap.gen_tps))

        self.pill_label.configure(
            text=f"{speed} · {fmt_count(snap.context_used)}/{fmt_count(snap.context_limit)} ({pct:.1f}%)",
            fg=self.FG_MAIN,
        )

        self.model_label.configure(text=f"Model: {snap.model_name.upper()} ({snap.turn_count} Turns)")
        short_id = f"{snap.conversation_id[:16]}..." if len(snap.conversation_id) > 16 else snap.conversation_id
        self.conv_label.configure(text=f"ID: {short_id}")

        if snap.is_buffered:
            gen_str = str(self._txt("val_gen_buf")).format(ms=snap.stream_sec * 1000, tok=snap.output_tokens)
            gen_color = self.WARN
        else:
            gen_str = str(self._txt("val_gen_ok")).format(tps=fmt_tps(snap.gen_tps), sec=snap.stream_sec)
            gen_color = self.OK

        self.val_gen.configure(text=gen_str, fg=gen_color)
        self.val_e2e.configure(
            text=str(self._txt("val_e2e")).format(tps=fmt_tps(snap.e2e_tps), ttft=snap.ttft_sec),
            fg=self.FG_MAIN,
        )
        self.val_session.configure(
            text=str(self._txt("val_session")).format(avg=fmt_tps(snap.avg_gen_tps), peak=fmt_tps(snap.peak_gen_tps)),
            fg=self.LIVE,
        )
        self.val_cached.configure(text=f"{snap.cached_tokens:,} ({fmt_count(snap.cached_tokens)})")
        self.val_input.configure(text=f"{snap.input_tokens:,} ({fmt_count(snap.input_tokens)})")

        if snap.thinking_tokens or snap.visible_tokens:
            out_str = str(self._txt("val_out_split")).format(
                total=snap.output_tokens,
                thk=fmt_count(snap.thinking_tokens),
                vis=fmt_count(snap.visible_tokens),
            )
        else:
            out_str = f"{snap.output_tokens:,} ({fmt_count(snap.output_tokens)})"
        self.val_output.configure(text=out_str)
        self.val_total.configure(text=f"{snap.context_used:,} / {snap.context_limit:,}", fg=ctx_color)

        bar_w = self.bar_canvas.winfo_width()
        if bar_w > 1:
            fill_w = min(bar_w, max(2, int(bar_w * (pct / 100.0))))
            self.bar_canvas.coords(self.bar_rect, 0, 0, fill_w, 8)
            self.bar_canvas.itemconfig(self.bar_rect, fill=ctx_color)

    def _poll_loop(self):
        try:
            snap = self.store.read_snapshot()
            self.current_snapshot = snap
            self._render(snap)
        except Exception:
            pass
        self.root.after(self.interval_ms, self._poll_loop)

    def run(self):
        """Enter the Tkinter main event loop."""
        self.root.mainloop()

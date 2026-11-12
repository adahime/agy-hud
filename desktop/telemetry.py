"""Read-only SQLite + WAL and wire-Protobuf telemetry reader for AGY-HUD."""

from dataclasses import dataclass
import glob
import os
import re
import sqlite3
import time
from typing import Dict, Iterator, List, Optional, Tuple


DB_ID_PATTERN = re.compile(r"^[0-9a-f-]{8,}$", re.I)

FALLBACK_CONTEXT_LIMITS: Dict[str, int] = {
    "gemini-3.8-flash-k": 256_000,
    "gemini-3.7-flash": 1_048_576,
    "gemini-3.1-pro": 1_048_576,
    "gemini-2.5-pro": 2_097_152,
    "claude-3-7-sonnet": 200_000,
    "claude-3-5-sonnet": 200_000,
    "gpt-4o": 128_000,
    "default": 256_000,
}


@dataclass
class TurnRecord:
    """Decoded metrics for a single model generation row."""

    model_id: str
    model_display: str
    cached_tokens: int
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    visible_tokens: int
    reported_context: int
    context_limit: int
    ttft_sec: float
    stream_sec: float
    total_sec: float
    gen_tps: float
    e2e_tps: float
    is_buffered: bool

    @property
    def preferred_model(self) -> str:
        """Prefer raw model_id (e.g. gemini-3.8-flash-k) over display name."""
        return self.model_id or self.model_display or "Unknown Model"


@dataclass
class ConversationSnapshot:
    """Aggregated telemetry state for the active Antigravity conversation."""

    conversation_id: str
    db_path: str
    updated_at: float
    model_name: str
    cached_tokens: int
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    visible_tokens: int
    context_used: int
    context_limit: int
    usage_pct: float
    turn_count: int
    ttft_sec: float
    stream_sec: float
    gen_tps: float
    e2e_tps: float
    is_buffered: bool
    last_sustained_tps: float
    avg_gen_tps: float
    avg_e2e_tps: float
    peak_gen_tps: float
    is_generating: bool
    is_tool_running: bool
    active_elapsed_sec: float


def read_varint(buf: bytes, pos: int) -> Tuple[int, int]:
    """Decode an unsigned base-128 varint starting at buf[pos]."""
    val = 0
    shift = 0
    end = len(buf)
    while pos < end:
        byte = buf[pos]
        pos += 1
        val |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return val, pos


def iter_fields(buf: bytes) -> Iterator[Tuple[int, int, object]]:
    """Safely yield (field_number, wire_type, value) pairs from raw protobuf bytes."""
    pos = 0
    end = len(buf)
    while pos < end:
        key, pos = read_varint(buf, pos)
        field_num = key >> 3
        wire_type = key & 0x07
        if wire_type == 0:
            val, pos = read_varint(buf, pos)
            yield field_num, wire_type, val
        elif wire_type == 2:
            size, pos = read_varint(buf, pos)
            if size < 0 or pos + size > end:
                break
            yield field_num, wire_type, buf[pos : pos + size]
            pos += size
        elif wire_type == 1:
            if pos + 8 > end:
                break
            yield field_num, wire_type, buf[pos : pos + 8]
            pos += 8
        elif wire_type == 5:
            if pos + 4 > end:
                break
            yield field_num, wire_type, buf[pos : pos + 4]
            pos += 4
        else:
            break


def read_duration_sec(buf: bytes) -> float:
    """Decode google.protobuf.Duration or Timestamp into seconds."""
    sec = 0
    nanos = 0
    for fnum, wtype, val in iter_fields(buf):
        if wtype != 0:
            continue
        if fnum == 1:
            sec = int(val)  # type: ignore[arg-type]
        elif fnum == 2:
            nanos = int(val)  # type: ignore[arg-type]
    return sec + nanos / 1e9


def _parse_usage_fields(buf: bytes) -> Dict[str, int]:
    counts: Dict[str, int] = {
        "input": 0,
        "output": 0,
        "cached": 0,
        "thinking": 0,
        "visible": 0,
        "fallback_out": 0,
    }
    for fnum, wtype, val in iter_fields(buf):
        if wtype != 0:
            continue
        num = int(val)  # type: ignore[arg-type]
        if fnum == 1:
            counts["fallback_out"] = num
        elif fnum == 2:
            counts["input"] = num
        elif fnum == 3:
            counts["output"] = num
        elif fnum == 5:
            counts["cached"] = num
        elif fnum == 9:
            counts["thinking"] = num
        elif fnum == 10:
            counts["visible"] = num
    return counts


def _parse_context_fields(buf: bytes) -> Tuple[int, int]:
    reported = 0
    limit = 0
    for fnum, wtype, val in iter_fields(buf):
        if fnum == 10 and wtype == 2:
            for cf, cw, cv in iter_fields(val):  # type: ignore[arg-type]
                if cw != 0:
                    continue
                if cf == 1:
                    reported = int(cv)  # type: ignore[arg-type]
                elif cf == 4:
                    limit = int(cv)  # type: ignore[arg-type]
    return reported, limit


def decode_generation_record(blob: bytes) -> Optional[TurnRecord]:
    """Decode a gen_metadata BLOB into a structured TurnRecord."""
    inner = next((val for f, w, val in iter_fields(blob) if f == 1 and w == 2), None)
    if not isinstance(inner, (bytes, bytearray)):
        return None

    model_id = ""
    model_display = ""
    usage: Optional[Dict[str, int]] = None
    legacy_usage: Optional[Dict[str, int]] = None
    reported_ctx = 0
    ctx_limit = 0
    ttft_sec = 0.0
    stream_sec = 0.0

    for fnum, wtype, val in iter_fields(inner):
        if wtype != 2 or not isinstance(val, (bytes, bytearray)):
            continue
        raw = bytes(val)
        if fnum == 19:
            model_id = raw.decode("utf-8", errors="ignore")
        elif fnum == 21:
            model_display = raw.decode("utf-8", errors="ignore")
        elif fnum == 4:
            usage = _parse_usage_fields(raw)
        elif fnum == 9:
            reported_ctx, ctx_limit = _parse_context_fields(raw)
        elif fnum == 11:
            ttft_sec = read_duration_sec(raw)
        elif fnum == 12:
            stream_sec = read_duration_sec(raw)
        elif fnum == 17:
            sub = next((v2 for f2, w2, v2 in iter_fields(raw) if f2 == 2 and w2 == 2), None)
            if isinstance(sub, (bytes, bytearray)):
                legacy_usage = _parse_usage_fields(bytes(sub))

    active_usage = usage if (usage and (usage["cached"] or usage["input"] or usage["output"])) else (legacy_usage or {})
    cached_tokens = active_usage.get("cached", 0)
    input_tokens = active_usage.get("input", 0)
    thinking_tokens = active_usage.get("thinking", 0)
    visible_tokens = active_usage.get("visible", 0)
    output_tokens = active_usage.get("output", 0) or active_usage.get("fallback_out", 0)
    if output_tokens == 0 and (thinking_tokens or visible_tokens):
        output_tokens = thinking_tokens + visible_tokens

    gen_tps = (output_tokens / stream_sec) if stream_sec > 0 else 0.0
    total_sec = ttft_sec + stream_sec
    e2e_tps = (output_tokens / total_sec) if total_sec > 0 else 0.0
    # Single-packet buffered responses finish in milliseconds and inflate gen_tps artificially.
    is_buffered = stream_sec < 0.5 or (stream_sec < 1.0 and gen_tps > 1200.0)

    return TurnRecord(
        model_id=model_id,
        model_display=model_display,
        cached_tokens=cached_tokens,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thinking_tokens=thinking_tokens,
        visible_tokens=visible_tokens,
        reported_context=reported_ctx,
        context_limit=ctx_limit,
        ttft_sec=ttft_sec,
        stream_sec=stream_sec,
        total_sec=total_sec,
        gen_tps=gen_tps,
        e2e_tps=e2e_tps,
        is_buffered=is_buffered,
    )


def _detect_active_step(cursor: sqlite3.Cursor) -> Tuple[bool, bool, float]:
    try:
        row = cursor.execute(
            "SELECT idx, step_type, status, metadata FROM steps ORDER BY idx DESC LIMIT 1;"
        ).fetchone()
    except Exception:
        return False, False, 0.0

    if not row or row[2] == 3:
        return False, False, 0.0

    step_type, meta = row[1], row[3]
    is_gen = step_type == 15
    is_tool = not is_gen
    elapsed = 0.0
    if isinstance(meta, (bytes, bytearray)):
        started_at = 0.0
        for fnum, wtype, val in iter_fields(bytes(meta)):
            if wtype == 2 and fnum in (1, 6) and isinstance(val, (bytes, bytearray)):
                ts = read_duration_sec(bytes(val))
                if fnum == 6 or started_at == 0.0:
                    started_at = ts
        if started_at > 0:
            elapsed = max(0.0, time.time() - started_at)
    return is_gen, is_tool, elapsed


def _resolve_context_limit(turn: TurnRecord) -> int:
    if turn.context_limit > 0:
        return turn.context_limit
    for candidate in (turn.model_id.lower(), turn.model_display.lower()):
        if candidate in FALLBACK_CONTEXT_LIMITS:
            return FALLBACK_CONTEXT_LIMITS[candidate]
    return FALLBACK_CONTEXT_LIMITS["default"]


class TelemetryStore:
    """Read-only scanner for local Antigravity conversation databases."""

    def __init__(self, conversations_dir: Optional[str] = None):
        if conversations_dir:
            self.conversations_dir = conversations_dir
        else:
            self.conversations_dir = os.path.join(
                os.path.expanduser("~"), ".gemini", "antigravity", "conversations"
            )

    @staticmethod
    def _wal_aware_mtime(db_path: str) -> float:
        mtime = os.path.getmtime(db_path)
        wal_path = f"{db_path}-wal"
        if os.path.exists(wal_path):
            mtime = max(mtime, os.path.getmtime(wal_path))
        return mtime

    def find_latest_db(self) -> Optional[str]:
        """Return the most recently modified conversation SQLite file."""
        if not os.path.isdir(self.conversations_dir):
            return None
        candidates = [
            p
            for p in glob.glob(os.path.join(self.conversations_dir, "*.db"))
            if DB_ID_PATTERN.match(os.path.splitext(os.path.basename(p))[0])
        ]
        if not candidates:
            return None
        candidates.sort(key=self._wal_aware_mtime, reverse=True)
        return candidates[0]

    def read_snapshot(self, db_path: Optional[str] = None) -> Optional[ConversationSnapshot]:
        """Read and summarize all recorded model calls from the target SQLite DB."""
        target = db_path or self.find_latest_db()
        if not target or not os.path.exists(target):
            return None

        conv_id = os.path.splitext(os.path.basename(target))[0]
        updated_at = self._wal_aware_mtime(target)

        try:
            conn = sqlite3.connect(f"file:{os.path.abspath(target)}?mode=ro", uri=True, timeout=1.0)
            conn.execute("PRAGMA busy_timeout = 1000;")
            cursor = conn.cursor()
            raw_rows = cursor.execute("SELECT idx, data FROM gen_metadata ORDER BY idx ASC;").fetchall()
            is_gen, is_tool, active_elapsed = _detect_active_step(cursor)
            conn.close()
        except Exception:
            return None

        turns: List[TurnRecord] = []
        for _, blob in raw_rows:
            if blob:
                rec = decode_generation_record(blob)
                if rec:
                    turns.append(rec)

        if not turns:
            return None

        latest = turns[-1]
        total_out = sum(t.output_tokens for t in turns)
        total_stream = sum(t.stream_sec for t in turns)
        total_e2e = sum(t.total_sec for t in turns)
        sustained = [t.gen_tps for t in turns if not t.is_buffered]

        context_used = (
            latest.reported_context
            if latest.reported_context > 0
            else latest.cached_tokens + latest.input_tokens
        )
        context_limit = _resolve_context_limit(latest)
        usage_pct = (context_used / context_limit) * 100.0 if context_limit else 0.0

        return ConversationSnapshot(
            conversation_id=conv_id,
            db_path=target,
            updated_at=updated_at,
            model_name=latest.preferred_model,
            cached_tokens=latest.cached_tokens,
            input_tokens=latest.input_tokens,
            output_tokens=latest.output_tokens,
            thinking_tokens=latest.thinking_tokens,
            visible_tokens=latest.visible_tokens,
            context_used=context_used,
            context_limit=context_limit,
            usage_pct=round(usage_pct, 2),
            turn_count=len(turns),
            ttft_sec=latest.ttft_sec,
            stream_sec=latest.stream_sec,
            gen_tps=latest.gen_tps,
            e2e_tps=latest.e2e_tps,
            is_buffered=latest.is_buffered,
            last_sustained_tps=sustained[-1] if sustained else 0.0,
            avg_gen_tps=(total_out / total_stream) if total_stream > 0 else 0.0,
            avg_e2e_tps=(total_out / total_e2e) if total_e2e > 0 else 0.0,
            peak_gen_tps=max(sustained) if sustained else max(t.e2e_tps for t in turns),
            is_generating=is_gen,
            is_tool_running=is_tool,
            active_elapsed_sec=active_elapsed,
        )

/**
 * AGY-HUD sidecar telemetry server.
 * Reads local Antigravity SQLite + WAL conversation DBs in read-only mode
 * and exposes live TPS, TTFT, token breakdown, and step activity via HTTP.
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { fileURLToPath } from 'node:url';
import { Response, SidecarApp } from 'sidecar_sdk';

const __dirname = dirname(fileURLToPath(import.meta.url));
const UUID_RE = /^[0-9a-f-]{8,}$/i;
const STATIC_ASSETS = {
  '/styles.css': ['styles.css', 'text/css; charset=utf-8'],
  '/app.js': ['app.js', 'application/javascript; charset=utf-8'],
};

const MODEL_LIMIT_FALLBACKS = [
  [/gemini-3\.8-flash-k/i, 256_000],
  [/claude/i, 200_000],
  [/gpt-4o/i, 128_000],
  [/gemini-2\.5-pro/i, 2_097_152],
  [/gemini/i, 1_048_576],
];

function resolveAppDataDir() {
  const execData = process.env.ANTIGRAVITY_EXECUTABLE_DATA_DIR;
  if (execData) {
    for (let d = execData; d !== dirname(d); d = dirname(d)) {
      if (basename(d) === 'sidecar_data') {
        const root = dirname(d);
        if (existsSync(join(root, 'conversations'))) return root;
      }
    }
  }
  const envApp = process.env.ANTIGRAVITY_APP_DATA_DIR;
  if (envApp && existsSync(join(envApp, 'conversations'))) return envApp;
  return join(homedir(), '.gemini', 'antigravity');
}

function statSafe(path) {
  try {
    const s = statSync(path);
    return { mtimeMs: s.mtimeMs, size: s.size };
  } catch {
    return { mtimeMs: 0, size: 0 };
  }
}

function listConversations(dir) {
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return [];
  }
  const items = [];
  for (const name of entries) {
    if (!name.endsWith('.db')) continue;
    const id = name.slice(0, -3);
    if (!UUID_RE.test(id)) continue;
    const dbPath = join(dir, name);
    const dbStat = statSafe(dbPath);
    const walStat = statSafe(`${dbPath}-wal`);
    items.push({
      id,
      dbPath,
      updatedMs: Math.max(dbStat.mtimeMs, walStat.mtimeMs),
      key: `${dbStat.mtimeMs}:${dbStat.size}:${walStat.mtimeMs}:${walStat.size}`,
    });
  }
  items.sort((a, b) => b.updatedMs - a.updatedMs);
  return items;
}

function readVarint(buf, pos) {
  let val = 0n;
  let shift = 0n;
  while (pos < buf.length) {
    const b = buf[pos++];
    val |= BigInt(b & 0x7f) << shift;
    if ((b & 0x80) === 0) break;
    shift += 7n;
  }
  return [val, pos];
}

function iterFields(buf) {
  const fields = [];
  let pos = 0;
  while (pos < buf.length) {
    const [key, p1] = readVarint(buf, pos);
    pos = p1;
    const fnum = Number(key >> 3n);
    const wtype = Number(key & 7n);
    if (wtype === 0) {
      const [v, p2] = readVarint(buf, pos);
      pos = p2;
      fields.push([fnum, wtype, v]);
    } else if (wtype === 2) {
      const [lenBig, p2] = readVarint(buf, pos);
      const len = Number(lenBig);
      pos = p2;
      if (len < 0 || pos + len > buf.length) break;
      fields.push([fnum, wtype, buf.subarray(pos, pos + len)]);
      pos += len;
    } else if (wtype === 1) {
      if (pos + 8 > buf.length) break;
      fields.push([fnum, wtype, buf.subarray(pos, pos + 8)]);
      pos += 8;
    } else if (wtype === 5) {
      if (pos + 4 > buf.length) break;
      fields.push([fnum, wtype, buf.subarray(pos, pos + 4)]);
      pos += 4;
    } else {
      break;
    }
  }
  return fields;
}

function readDurationSec(buf) {
  let sec = 0;
  let nanos = 0;
  for (const [fn, wt, val] of iterFields(buf)) {
    if (wt !== 0) continue;
    if (fn === 1) sec = Number(val);
    else if (fn === 2) nanos = Number(val);
  }
  return sec + nanos / 1e9;
}

function parseUsageSubmsg(buf) {
  const out = { newInput: 0, cachedInput: 0, outputTokens: 0, thinkingTokens: 0, candidateTokens: 0, fallbackOut: 0 };
  for (const [fn, wt, val] of iterFields(buf)) {
    if (wt !== 0) continue;
    const n = Number(val);
    if (fn === 1) out.fallbackOut = n;
    else if (fn === 2) out.newInput = n;
    else if (fn === 3) out.outputTokens = n;
    else if (fn === 5) out.cachedInput = n;
    else if (fn === 9) out.thinkingTokens = n;
    else if (fn === 10) out.candidateTokens = n;
  }
  return out;
}

function resolveLimitFallback(model) {
  for (const [re, limit] of MODEL_LIMIT_FALLBACKS) {
    if (re.test(model || '')) return limit;
  }
  return 256_000;
}

function parseGenRow(idx, raw) {
  const f1 = iterFields(raw).find(([fn, wt]) => fn === 1 && wt === 2);
  if (!f1) return null;

  let modelId = '';
  let modelDisplay = '';
  let primaryUsage = null;
  let legacyUsage = null;
  let ttftSec = 0;
  let genSec = 0;
  let contextReported = 0;
  let contextLimit = 0;
  let lastStepIndex = null;

  for (const [fn, wt, val] of iterFields(f1[2])) {
    if (wt !== 2) continue;
    if (fn === 19) modelId = Buffer.from(val).toString('utf8');
    else if (fn === 21) modelDisplay = Buffer.from(val).toString('utf8');
    else if (fn === 4) primaryUsage = parseUsageSubmsg(val);
    else if (fn === 11) ttftSec = readDurationSec(val);
    else if (fn === 12) genSec = readDurationSec(val);
    else if (fn === 9) {
      for (const [bf, bw, bv] of iterFields(val)) {
        if (bf === 10 && bw === 2) {
          for (const [cf, cw, cv] of iterFields(bv)) {
            if (cw !== 0) continue;
            if (cf === 1) contextReported = Number(cv);
            else if (cf === 4) contextLimit = Number(cv);
          }
        }
      }
    } else if (fn === 17) {
      const f2 = iterFields(val).find(([sf, sw]) => sf === 2 && sw === 2);
      if (f2) legacyUsage = parseUsageSubmsg(f2[2]);
    } else if (fn === 20) {
      let k = '';
      let v = '';
      for (const [kf, kw, kv] of iterFields(val)) {
        if (kw !== 2) continue;
        if (kf === 1) k = Buffer.from(kv).toString('utf8');
        else if (kf === 2) v = Buffer.from(kv).toString('utf8');
      }
      if (k === 'last_step_index' && v !== '') {
        const parsed = Number(v);
        if (Number.isFinite(parsed)) lastStepIndex = parsed;
      }
    }
  }

  const u = (primaryUsage && (primaryUsage.cachedInput || primaryUsage.newInput || primaryUsage.outputTokens))
    ? primaryUsage
    : (legacyUsage || { newInput: 0, cachedInput: 0, outputTokens: 0, thinkingTokens: 0, candidateTokens: 0, fallbackOut: 0 });
  const outputTokens = u.outputTokens || u.fallbackOut || (u.thinkingTokens + u.candidateTokens);
  const model = modelId || modelDisplay || 'Unknown Model';
  const totalContext = contextReported > 0 ? contextReported : u.cachedInput + u.newInput;
  const limit = contextLimit > 0 ? contextLimit : resolveLimitFallback(model);
  const totalSec = ttftSec + genSec;
  const genTps = genSec > 0 ? outputTokens / genSec : 0;
  const e2eTps = totalSec > 0 ? outputTokens / totalSec : 0;
  const isBuffered = genSec < 0.5 || (genSec < 1.0 && genTps > 1200);

  return {
    idx,
    lastStepIndex,
    model,
    modelId,
    modelDisplay,
    newInput: u.newInput,
    cachedInput: u.cachedInput,
    outputTokens,
    thinkingTokens: u.thinkingTokens,
    candidateTokens: u.candidateTokens,
    ttftSec,
    genSec,
    totalSec,
    isBuffered,
    genTps,
    e2eTps,
    totalContext,
    contextLimit: limit,
    contextPct: limit > 0 ? Math.min(100, (totalContext / limit) * 100) : 0,
  };
}

function readStepTimes(metaBuf) {
  let createdAtMs = 0;
  let streamStartMs = 0;
  let completedAtMs = 0;
  for (const [fn, wt, val] of iterFields(metaBuf)) {
    if (wt !== 2) continue;
    if (fn === 1) createdAtMs = readDurationSec(val) * 1000;
    else if (fn === 6) streamStartMs = readDurationSec(val) * 1000;
    else if (fn === 7) completedAtMs = readDurationSec(val) * 1000;
  }
  return { createdAtMs, streamStartMs, completedAtMs };
}

function readTelemetry(dbPath) {
  let db;
  try {
    db = new DatabaseSync(dbPath, { readOnly: true });
    const gmRows = db.prepare('SELECT idx, data FROM gen_metadata ORDER BY idx ASC').all();
    const stepRows = db.prepare('SELECT idx, step_type, status, metadata FROM steps ORDER BY idx ASC').all();

    const plannerTimes = new Map();
    let activeStep = null;
    for (const s of stepRows) {
      const ts = s.metadata ? readStepTimes(s.metadata) : { createdAtMs: 0, streamStartMs: 0, completedAtMs: 0 };
      if (s.step_type === 15) plannerTimes.set(s.idx, ts);
      if (s.status !== 3) {
        activeStep = {
          idx: s.idx,
          stepType: s.step_type,
          status: s.status,
          createdAtMs: ts.createdAtMs,
          streamStartMs: ts.streamStartMs,
        };
      }
    }

    const invocations = [];
    for (const row of gmRows) {
      const parsed = parseGenRow(row.idx, row.data);
      if (!parsed) continue;
      const stepIdx = parsed.lastStepIndex !== null ? parsed.lastStepIndex + 1 : null;
      const times = stepIdx !== null ? plannerTimes.get(stepIdx) : null;
      invocations.push({
        ...parsed,
        timestampMs: times?.completedAtMs || times?.createdAtMs || 0,
      });
    }

    let totalOutput = 0;
    let totalGenSec = 0;
    let totalE2eSec = 0;
    let peakGenTps = 0;
    let latestSustained = null;
    for (const inv of invocations) {
      totalOutput += inv.outputTokens;
      totalGenSec += inv.genSec;
      totalE2eSec += inv.totalSec;
      if (!inv.isBuffered) {
        latestSustained = inv;
        if (inv.genTps > peakGenTps) peakGenTps = inv.genTps;
      }
    }
    if (peakGenTps === 0 && invocations.length) {
      peakGenTps = Math.max(...invocations.map((i) => i.e2eTps));
    }

    return {
      invocations,
      latest: invocations.length ? invocations[invocations.length - 1] : null,
      latestSustained,
      summary: {
        count: invocations.length,
        totalOutput,
        avgGenTps: totalGenSec > 0 ? totalOutput / totalGenSec : 0,
        avgE2eTps: totalE2eSec > 0 ? totalOutput / totalE2eSec : 0,
        peakGenTps,
      },
      activeStep,
    };
  } finally {
    try { db?.close(); } catch { /* ignore */ }
  }
}

const conversationsDir = join(resolveAppDataDir(), 'conversations');
const app = new SidecarApp();

app.page('/', () => readFileSync(join(__dirname, 'index.html'), 'utf-8'));

for (const [route, [file, contentType]] of Object.entries(STATIC_ASSETS)) {
  app.api(route, () => new Response(readFileSync(join(__dirname, file), 'utf-8'), { contentType }), 'GET');
}

app.api('/api/stats', (data) => {
  const mode = data.mode === 'latest' ? 'latest' : 'auto';
  const requestedConv = typeof data.conversationId === 'string' && UUID_RE.test(data.conversationId)
    ? data.conversationId
    : (app.config.conversationId || '');

  const conversations = listConversations(conversationsDir);
  if (!conversations.length) {
    return { found: false, conversations: [], serverTimeMs: Date.now() };
  }

  const target = (mode === 'auto' && requestedConv
    ? conversations.find((c) => c.id === requestedConv)
    : null) || conversations[0];

  const recentList = conversations.slice(0, 15).map((c) => ({ id: c.id, updatedMs: c.updatedMs }));
  const etag = `${mode}|${target.id}|${target.key}|${recentList[0]?.id || ''}`;
  if (data.etag && data.etag === etag) {
    return { unchanged: true, etag, serverTimeMs: Date.now() };
  }

  try {
    return {
      found: true,
      etag,
      mode,
      conversationId: target.id,
      serverTimeMs: Date.now(),
      conversations: recentList,
      ...readTelemetry(target.dbPath),
    };
  } catch (err) {
    return {
      found: false,
      error: err.message,
      conversationId: target.id,
      conversations: recentList,
      serverTimeMs: Date.now(),
    };
  }
}, 'GET');

app.run();

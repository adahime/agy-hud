(() => {
  const POLL_MS = 450;
  const $ = (id) => document.getElementById(id);

  const I18N = {
    en: {
      title: 'AGY-HUD',
      connecting: 'SYNC...',
      waitingModel: 'Waiting for telemetry...',
      optAuto: 'Auto Pane',
      optLatest: 'Latest DB',
      genLabel: 'GEN TPS',
      livePill: 'GEN',
      e2eLabel: 'E2E TPS (w/ TTFT)',
      ctxLabel: 'CTX WINDOW',
      kCache: 'CACHE',
      kIn: 'IN',
      kThk: 'THK',
      kOut: 'OUT',
      avgGen: 'AVG GEN',
      avgE2e: 'AVG E2E',
      peakTps: 'PEAK TPS',
      totOut: 'TOT OUT',
      chartTitle: 'TPS TREND (GEN)',
      noCalls: 'No calls yet',
      histTitle: 'CALL LOG',
      histHint: 'Hover for full row',
      waitStep: 'Waiting for next step...',
      badgeGen: (s) => `GEN ${s}s`,
      badgeTool: 'TOOL',
      badgeLive: 'LIVE',
      badgeIdle: 'IDLE',
      badgeRetry: 'RETRY...',
      noDb: 'No session DB found',
      readErr: (e) => `Read err: ${e}`,
      waitFirstCall: (id) => `Conv ${id}… · waiting for call`,
      modelLine: (m, id, n) => `${m.toUpperCase()} · ${id}… · #${n} turns`,
      chartMeta: (n) => `${n} calls`,
      genSubSust: (sust, ms, tok) => `LAST STR ${sust} · BUF ${ms}ms (${tok} tok)`,
      genSubBuf: (ms, tok) => `BUF ${ms}ms · OUT ${tok} tok`,
      genSubOk: (tok, sec) => `OUT ${tok} · GEN ${sec}`,
      e2eSub: (ttft, tot) => `TTFT ${ttft} · TOT ${tot}`,
      tipBuf: (idx, ms, e2e, tok) => `#${idx} · BUF (${ms}ms) · E2E ${e2e} tok/s · ${tok} tok`,
      tipOk: (idx, gen, e2e, tok) => `#${idx} · GEN ${gen} tok/s (E2E ${e2e}) · ${tok} tok`,
      histDetail: (tm, out, thk, ttft, gen) => `${tm ? tm + ' · ' : ''}OUT ${out} (THK ${thk}) · TTFT ${ttft} · GEN ${gen}`,
      histBuf: (ms) => `BUF ${ms}ms`,
      waitOut: 'Waiting for output...',
    },
    zh: {
      title: 'AGY-HUD',
      connecting: '连接中…',
      waitingModel: '等待模型响应数据…',
      optAuto: '跟随当前对话',
      optLatest: '自动最新活跃',
      genLabel: '生成速度 (Gen TPS)',
      livePill: '生成中',
      e2eLabel: '端到端速度 (含 TTFT)',
      ctxLabel: '上下文窗口',
      kCache: '缓存命中',
      kIn: '新增输入',
      kThk: '思考',
      kOut: '可见/工具',
      avgGen: '会话加权 Gen',
      avgE2e: '会话加权 E2E',
      peakTps: '峰值速度',
      totOut: '累计输出',
      chartTitle: '最近调用速度趋势 (Gen TPS)',
      noCalls: '暂无调用记录',
      histTitle: '逐次调用明细',
      histHint: '悬停查看完整指标',
      waitStep: '等待新对话步骤…',
      badgeGen: (s) => `生成中 ${s}s`,
      badgeTool: '工具执行中',
      badgeLive: '实时监听中',
      badgeIdle: '等待对话',
      badgeRetry: '重连中…',
      noDb: '暂未检测到会话数据库',
      readErr: (e) => `读取失败: ${e}`,
      waitFirstCall: (id) => `会话 ${id}… · 等待首次模型调用`,
      modelLine: (m, id, n) => `${m.toUpperCase()} · 会话 ${id}… · 第 ${n} 次调用`,
      chartMeta: (n) => `${n} 次模型调用`,
      genSubSust: (sust, ms, tok) => `上次流式 ${sust} · 本次单包 ${ms}ms (${tok} tok)`,
      genSubBuf: (ms, tok) => `单包缓冲 ${ms}ms · 输出 ${tok} tok`,
      genSubOk: (tok, sec) => `输出 ${tok} tok · 生成 ${sec}`,
      e2eSub: (ttft, tot) => `TTFT ${ttft} · 总计 ${tot}`,
      tipBuf: (idx, ms, e2e, tok) => `#${idx} · 单包缓冲 (${ms}ms) · E2E ${e2e} tok/s · ${tok} tok`,
      tipOk: (idx, gen, e2e, tok) => `#${idx} · Gen ${gen} tok/s (E2E ${e2e}) · ${tok} tok`,
      histDetail: (tm, out, thk, ttft, gen) => `${tm ? tm + ' · ' : ''}输出 ${out} (思 ${thk}) · TTFT ${ttft} · 生成 ${gen}`,
      histBuf: (ms) => `缓冲 ${ms}ms`,
      waitOut: '等待模型输出…',
    },
  };

  const state = {
    lang: (() => {
      try {
        return localStorage.getItem('agy_hud_lang') === 'zh' ? 'zh' : 'en';
      } catch {
        return 'en';
      }
    })(),
    etag: '',
    mode: 'auto',
    selectedConv: '',
    lastSnap: null,
    timer: null,
  };

  function tr() {
    return I18N[state.lang] || I18N.en;
  }

  function applyStaticI18n() {
    const t = tr();
    document.documentElement.lang = state.lang === 'zh' ? 'zh-CN' : 'en';
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const k = el.getAttribute('data-i18n');
      if (k && typeof t[k] === 'string') el.textContent = t[k];
    });
    $('lang-btn').textContent = state.lang === 'en' ? 'EN / 中' : '中 / EN';
  }

  function syncTheme() {
    const probe = document.createElement('span');
    probe.style.cssText = 'position:absolute;visibility:hidden;color:var(--background, #f7f7f8)';
    document.documentElement.appendChild(probe);
    const c = getComputedStyle(probe).color;
    probe.remove();
    const nums = (c.match(/[\d.]+/g) || []).map(Number);
    if (nums.length < 3) return;
    const scale = c.startsWith('color(') ? 1 : 255;
    const [r, g, b] = nums.slice(0, 3).map((v) => v / scale);
    const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    document.documentElement.dataset.theme = lum < 0.5 ? 'dark' : 'light';
  }
  syncTheme();
  new MutationObserver(syncTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['style'] });

  function fmtNum(n) {
    if (!Number.isFinite(n)) return '--';
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
    return String(Math.round(n));
  }

  function fmtTps(v) {
    if (!Number.isFinite(v) || v <= 0) return '--';
    return v >= 100 ? v.toFixed(1) : v.toFixed(2);
  }

  function fmtSec(s) {
    if (!Number.isFinite(s) || s < 0) return '--';
    return s >= 10 ? `${s.toFixed(1)}s` : `${s.toFixed(2)}s`;
  }

  function fmtClock(ms) {
    return ms ? new Date(ms).toLocaleTimeString(undefined, { hour12: false }) : '';
  }

  function esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  function getPaneConv() {
    const params = new URLSearchParams(location.search);
    return window.sidecar?.conversationId || params.get('conversationId') || '';
  }

  async function fetchStats() {
    const conv = state.mode === 'custom'
      ? state.selectedConv
      : (state.mode === 'auto' ? getPaneConv() : '');
    const apiMode = state.mode === 'latest' ? 'latest' : 'auto';
    const qs = new URLSearchParams({ mode: apiMode });
    if (conv) qs.set('conversationId', conv);
    if (state.etag) qs.set('etag', state.etag);

    const fetcher = window.sidecar?.fetch ? window.sidecar.fetch.bind(window.sidecar) : fetch;
    const res = await fetcher(`/api/stats?${qs.toString()}`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  function syncConversationSelect(conversations, activeId) {
    const t = tr();
    const sel = $('conv-select');
    const keepVal = sel.value;
    const desired = [
      { value: 'auto', label: t.optAuto },
      { value: 'latest', label: t.optLatest },
      ...(conversations || []).map((c) => ({ value: `conv:${c.id}`, label: `${c.id.slice(0, 8)}… (${fmtClock(c.updatedMs)})` })),
    ];
    const sig = `${state.lang}|` + desired.map((o) => `${o.value}=${o.label}`).join('|');
    if (sel.dataset.sig !== sig) {
      sel.innerHTML = desired.map((o) => `<option value="${esc(o.value)}">${esc(o.label)}</option>`).join('');
      sel.dataset.sig = sig;
      if ([...sel.options].some((o) => o.value === keepVal)) sel.value = keepVal;
      else if (state.mode === 'custom' && activeId) sel.value = `conv:${activeId}`;
    }
  }

  function renderChart(invocations) {
    const t = tr();
    const wrap = $('chart-wrap');
    const recent = invocations.slice(-28);
    $('chart-meta').textContent = t.chartMeta(invocations.length);
    if (!recent.length) {
      wrap.innerHTML = `<div class="empty-inline">${esc(t.noCalls)}</div>`;
      return;
    }

    const w = 400;
    const h = 92;
    const padY = 8;
    const plotVal = (r) => (r.isBuffered ? r.e2eTps : r.genTps);
    const maxTps = Math.max(10, ...recent.map(plotVal));
    const slotW = w / recent.length;
    const barW = Math.max(3, Math.min(20, slotW * 0.72));

    const bars = recent.map((r, i) => {
      const barH = Math.max(3, Math.max(0.05, plotVal(r) / maxTps) * (h - padY * 2));
      const x = i * slotW + (slotW - barW) / 2;
      const y = h - padY - barH;
      const cls = i === recent.length - 1 ? 'chart-bar latest' : 'chart-bar';
      const tip = r.isBuffered
        ? t.tipBuf(r.idx + 1, (r.genSec * 1000).toFixed(0), fmtTps(r.e2eTps), r.outputTokens)
        : t.tipOk(r.idx + 1, fmtTps(r.genTps), fmtTps(r.e2eTps), r.outputTokens);
      return `<rect class="${cls}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${barH.toFixed(1)}" rx="2"><title>${esc(tip)}</title></rect>`;
    }).join('');

    wrap.innerHTML = `<svg class="chart-svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">${bars}</svg>`;
  }

  function renderHistory(invocations) {
    const t = tr();
    const el = $('history-list');
    if (!invocations.length) {
      el.innerHTML = `<div class="empty-inline">${esc(t.waitOut)}</div>`;
      return;
    }
    el.innerHTML = [...invocations].reverse().slice(0, 30).map((r, i) => {
      const cls = i === 0 ? 'history-row is-latest' : 'history-row';
      const detail = t.histDetail(fmtClock(r.timestampMs), r.outputTokens, r.thinkingTokens, fmtSec(r.ttftSec), fmtSec(r.genSec));
      const primary = r.isBuffered ? t.histBuf((r.genSec * 1000).toFixed(0)) : `${fmtTps(r.genTps)} tok/s`;
      return `
        <div class="${cls}" title="${esc(detail)}">
          <span class="history-idx">#${r.idx + 1}</span>
          <span class="history-detail">${esc(detail)}</span>
          <span class="history-tps">${primary}</span>
          <span class="history-e2e">E2E ${fmtTps(r.e2eTps)}</span>
        </div>
      `;
    }).join('');
  }

  function updateStatusBadge(snap) {
    const t = tr();
    const badge = $('status-badge');
    const text = $('status-text');
    const livePill = $('live-pill');
    const active = snap.activeStep;

    if (active && active.stepType === 15) {
      badge.className = 'badge live';
      const baseMs = active.streamStartMs || active.createdAtMs || snap.serverTimeMs;
      text.textContent = t.badgeGen(Math.max(0, (Date.now() - baseMs) / 1000).toFixed(1));
      livePill.classList.remove('hidden');
    } else if (active) {
      badge.className = 'badge tool';
      text.textContent = t.badgeTool;
      livePill.classList.add('hidden');
    } else {
      badge.className = 'badge';
      text.textContent = snap.found ? t.badgeLive : t.badgeIdle;
      livePill.classList.add('hidden');
    }
  }

  function render(snap) {
    const t = tr();
    state.lastSnap = snap;
    syncConversationSelect(snap.conversations, snap.conversationId);
    updateStatusBadge(snap);

    if (!snap.found) {
      $('model-line').textContent = snap.error ? t.readErr(snap.error) : t.noDb;
      return;
    }

    const latest = snap.latest;
    if (!latest) {
      $('model-line').textContent = t.waitFirstCall(snap.conversationId.slice(0, 8));
      return;
    }

    $('model-line').textContent = t.modelLine(latest.modelId || latest.model, snap.conversationId.slice(0, 8), snap.summary.count);

    if (latest.isBuffered) {
      const sust = snap.latestSustained;
      $('gen-tps').textContent = sust ? fmtTps(sust.genTps) : fmtTps(latest.e2eTps);
      const ms = (latest.genSec * 1000).toFixed(0);
      $('gen-sub').textContent = sust ? t.genSubSust(fmtTps(sust.genTps), ms, latest.outputTokens) : t.genSubBuf(ms, latest.outputTokens.toLocaleString());
    } else {
      $('gen-tps').textContent = fmtTps(latest.genTps);
      $('gen-sub').textContent = t.genSubOk(latest.outputTokens.toLocaleString(), fmtSec(latest.genSec));
    }

    $('e2e-tps').textContent = fmtTps(latest.e2eTps);
    $('e2e-sub').textContent = t.e2eSub(fmtSec(latest.ttftSec), fmtSec(latest.totalSec));

    const pct = latest.contextPct;
    $('ctx-text').textContent = `${fmtNum(latest.totalContext)} / ${fmtNum(latest.contextLimit)} (${pct.toFixed(1)}%)`;
    const bar = $('ctx-bar');
    bar.style.width = `${Math.min(100, Math.max(1, pct))}%`;
    bar.style.backgroundColor = pct < 50 ? 'var(--hud-ok)' : (pct < 80 ? 'var(--hud-warn)' : 'var(--hud-bad)');

    $('tok-cache').textContent = fmtNum(latest.cachedInput);
    $('tok-input').textContent = fmtNum(latest.newInput);
    $('tok-think').textContent = fmtNum(latest.thinkingTokens);
    $('tok-vis').textContent = fmtNum(latest.candidateTokens);

    $('avg-gen').textContent = `${fmtTps(snap.summary.avgGenTps)} tok/s`;
    $('avg-e2e').textContent = `${fmtTps(snap.summary.avgE2eTps)} tok/s`;
    $('peak-tps').textContent = `${fmtTps(snap.summary.peakGenTps)} tok/s`;
    $('total-out').textContent = `${fmtNum(snap.summary.totalOutput)} tok`;

    renderChart(snap.invocations || []);
    renderHistory(snap.invocations || []);
  }

  async function poll() {
    try {
      const snap = await fetchStats();
      if (snap.etag) state.etag = snap.etag;
      if (!snap.unchanged) render(snap);
      else if (state.lastSnap) updateStatusBadge(state.lastSnap);
    } catch {
      $('status-badge').className = 'badge';
      $('status-text').textContent = tr().badgeRetry;
    } finally {
      state.timer = setTimeout(poll, POLL_MS);
    }
  }

  $('lang-btn').addEventListener('click', () => {
    state.lang = state.lang === 'en' ? 'zh' : 'en';
    try { localStorage.setItem('agy_hud_lang', state.lang); } catch { /* ignore */ }
    applyStaticI18n();
    if (state.lastSnap) render(state.lastSnap);
    else syncConversationSelect([], '');
  });

  $('conv-select').addEventListener('change', (e) => {
    const val = e.target.value;
    state.etag = '';
    if (val === 'auto') {
      state.mode = 'auto';
      state.selectedConv = '';
    } else if (val === 'latest') {
      state.mode = 'latest';
      state.selectedConv = '';
    } else if (val.startsWith('conv:')) {
      state.mode = 'custom';
      state.selectedConv = val.slice(5);
    }
    clearTimeout(state.timer);
    poll();
  });

  applyStaticI18n();
  poll();
})();

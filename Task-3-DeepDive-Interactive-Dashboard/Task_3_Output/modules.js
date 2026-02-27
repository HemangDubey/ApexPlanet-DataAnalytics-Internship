/* ============================================================
   GravityBI — Merged AI Modules (Task 3B)
   CSV Engine + Simulation Lab + H.O.N.E.Y AI
   ============================================================ */

// ══════════════════════════════════════════════════════════
//  MODULE 1: CSV DATA ENGINE (Client-side PapaParse)
// ══════════════════════════════════════════════════════════

const uploadZone = document.getElementById('uploadZone');
const csvFileInput = document.getElementById('csvFileInput');

uploadZone.addEventListener('click', () => csvFileInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', e => {
    e.preventDefault(); uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) processCSV(e.dataTransfer.files[0]);
});
csvFileInput.addEventListener('change', e => { if (e.target.files.length) processCSV(e.target.files[0]); });

function processCSV(file) {
    if (!file.name.endsWith('.csv')) {
        document.getElementById('csvStatus').innerHTML = '<p style="color:#f87171">❌ Only CSV files supported.</p>';
        return;
    }
    document.getElementById('csvStatus').innerHTML = '<p style="color:var(--text-secondary)">⏳ Parsing CSV...</p>';

    Papa.parse(file, {
        header: true, skipEmptyLines: true, dynamicTyping: true,
        complete: function (result) {
            if (result.errors.length > 3) {
                document.getElementById('csvStatus').innerHTML = `<p style="color:#f87171">❌ Parse errors: ${result.errors[0].message}</p>`;
                return;
            }
            const data = result.data;
            const fields = result.meta.fields;
            document.getElementById('csvStatus').innerHTML =
                `<p style="color:#34d399">✅ Loaded <strong>${data.length}</strong> rows × <strong>${fields.length}</strong> columns from <strong>${file.name}</strong></p>`;

            const schema = detectCSVSchema(data, fields);
            const kpis = generateCSVKPIs(data, schema, fields);
            const charts = generateCSVCharts(data, schema, fields);

            renderCSVKPIs(kpis);
            renderCSVCharts(charts);
        },
        error: function (err) {
            document.getElementById('csvStatus').innerHTML = `<p style="color:#f87171">❌ Failed: ${err.message}</p>`;
        }
    });
}

function detectCSVSchema(data, fields) {
    const schema = {};
    fields.forEach(field => {
        const vals = data.map(r => r[field]).filter(v => v != null && v !== '');
        const sample = vals.slice(0, 50);
        const numCount = sample.filter(v => typeof v === 'number' || (!isNaN(Number(v)) && v !== '')).length;
        const dateKeywords = ['date', 'time', 'created', 'updated', 'timestamp', 'day', 'month', 'year'];
        const isDate = dateKeywords.some(k => field.toLowerCase().includes(k)) ||
            sample.filter(v => typeof v === 'string' && !isNaN(new Date(v)) && v.length > 5).length / sample.length > 0.7;

        if (isDate) {
            schema[field] = { type: 'datetime' };
        } else if (numCount / sample.length > 0.8) {
            const nums = vals.map(Number).filter(n => !isNaN(n));
            nums.sort((a, b) => a - b);
            const sum = nums.reduce((a, b) => a + b, 0);
            schema[field] = { type: 'numerical', stats: { min: nums[0], max: nums[nums.length - 1], mean: sum / nums.length, sum, count: nums.length } };
        } else {
            const unique = [...new Set(vals.map(String))];
            schema[field] = { type: 'categorical', uniqueCount: unique.length, topValues: getTopN(vals, 10) };
        }
    });
    return schema;
}

function getTopN(vals, n) {
    const freq = {};
    vals.forEach(v => { freq[v] = (freq[v] || 0) + 1; });
    return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, n).map(([v, c]) => ({ value: v, count: c }));
}

function generateCSVKPIs(data, schema, fields) {
    const kpis = [];
    const numCols = Object.entries(schema).filter(([_, v]) => v.type === 'numerical');
    const catCols = Object.entries(schema).filter(([_, v]) => v.type === 'categorical');
    const kpiColors = ['#34d399', '#38bdf8', '#a78bfa', '#fb923c', '#f472b6', '#f87171', '#22d3ee', '#facc15'];
    let ci = 0;

    kpis.push({ label: 'Total Records', value: data.length.toLocaleString(), icon: '📊', color: kpiColors[ci++ % 8] });

    const revCol = findCol(numCols, ['revenue', 'total', 'amount', 'sales', 'price', 'value', 'income']);
    if (revCol) {
        const s = schema[revCol].stats;
        kpis.push({ label: `Total ${fmtLabel(revCol)}`, value: '$' + fmtNum(s.sum), icon: '💰', color: kpiColors[ci++ % 8] });
        kpis.push({ label: `Avg ${fmtLabel(revCol)}`, value: '$' + fmtNum(s.mean), icon: '📈', color: kpiColors[ci++ % 8] });
    }
    const qCol = findCol(numCols, ['quantity', 'qty', 'units', 'count']);
    if (qCol) kpis.push({ label: `Total ${fmtLabel(qCol)}`, value: fmtNum(schema[qCol].stats.sum), icon: '📦', color: kpiColors[ci++ % 8] });
    const idCol = findCol(catCols, ['customer', 'user', 'client', 'id', 'account']);
    if (idCol) kpis.push({ label: `Unique ${fmtLabel(idCol)}`, value: schema[idCol].uniqueCount, icon: '👥', color: kpiColors[ci++ % 8] });
    const catCol = findCol(catCols, ['category', 'type', 'segment', 'group', 'class']);
    if (catCol) kpis.push({ label: fmtLabel(catCol), value: schema[catCol].uniqueCount, icon: '🏷️', color: kpiColors[ci++ % 8] });
    const geoCol = findCol(catCols, ['country', 'region', 'state', 'city', 'location']);
    if (geoCol) kpis.push({ label: fmtLabel(geoCol), value: schema[geoCol].uniqueCount, icon: '🌍', color: kpiColors[ci++ % 8] });

    return kpis;
}

function generateCSVCharts(data, schema, fields) {
    const charts = [];
    const numCols = Object.entries(schema).filter(([_, v]) => v.type === 'numerical');
    const catCols = Object.entries(schema).filter(([_, v]) => v.type === 'categorical');
    const revCol = findCol(numCols, ['revenue', 'total', 'amount', 'sales', 'value', 'income', 'price']);

    // Categorical breakdowns
    catCols.slice(0, 4).forEach(([col, meta]) => {
        if (meta.uniqueCount <= 25 && revCol) {
            const agg = aggregateBy(data, col, revCol);
            charts.push({ title: `${fmtLabel(revCol)} by ${fmtLabel(col)}`, data: agg.slice(0, 12), type: 'horizontal', prefix: '$' });
        }
    });

    // Distributions
    numCols.slice(0, 2).forEach(([col]) => {
        const dist = buildDist(data, col);
        if (dist.length) charts.push({ title: `${fmtLabel(col)} Distribution`, data: dist, type: 'vertical', prefix: '' });
    });

    return charts;
}

function renderCSVKPIs(kpis) {
    const el = document.getElementById('csvKPIs');
    el.innerHTML = `<h3 style="font-size:16px;font-weight:700;margin-bottom:12px">Auto-Detected KPIs</h3>
    <div class="kpi-grid">${kpis.map(k => `<div class="kpi-card" style="--kpi-color:${k.color}">
      <div class="kpi-icon">${k.icon}</div>
      <div class="kpi-value" style="color:${k.color}">${k.value}</div>
      <div class="kpi-label">${k.label}</div>
    </div>`).join('')}</div>`;
}

function renderCSVCharts(charts) {
    const el = document.getElementById('csvCharts');
    if (!charts.length) { el.innerHTML = ''; return; }
    el.innerHTML = `<h3 style="font-size:16px;font-weight:700;margin-bottom:12px">Auto-Generated Charts</h3>
    <div class="chart-row two-col" style="flex-wrap:wrap">${charts.map(c => `<div class="chart-card" style="min-width:45%">
      <div class="chart-header"><h3>${c.title}</h3></div>
      <div class="chart-body">${htmlBarChart_m(c.data, c.type === 'horizontal', c.prefix)}</div>
    </div>`).join('')}</div>`;
}

function htmlBarChart_m(data, horiz, prefix) {
    const COLORS_M = ['#38bdf8', '#f472b6', '#34d399', '#a78bfa', '#fb923c', '#f87171', '#facc15', '#22d3ee', '#818cf8', '#4ade80', '#e879f9', '#67e8f9'];
    const max = Math.max(...data.map(d => Math.abs(Number(d.value) || 0)));
    if (!max) return '<p style="color:var(--text-muted)">No data</p>';
    let html = `<div class="html-bar-chart ${horiz ? 'horizontal' : 'vertical'}">`;
    data.forEach((d, i) => {
        const pct = (Math.abs(Number(d.value)) / max) * 100;
        const c = COLORS_M[i % COLORS_M.length];
        if (horiz) html += `<div class="bar-row"><span class="bar-label" title="${d.label}">${(d.label || '').substring(0, 28)}</span><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${c}"></div></div><span class="bar-val">${prefix}${fmtNum(d.value)}</span></div>`;
        else html += `<div class="bar-col"><div class="bar-vtrack"><div class="bar-vfill" style="height:${pct}%;background:${c}"></div></div><span class="bar-val">${fmtNum(d.value)}</span><span class="bar-vlabel">${(d.label || '').substring(0, 8)}</span></div>`;
    });
    return html + '</div>';
}

function findCol(cols, kws) { for (const k of kws) { const m = cols.find(([n]) => n.toLowerCase().includes(k)); if (m) return m[0]; } return null; }
function fmtLabel(s) { return s.replace(/([A-Z])/g, ' $1').replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim(); }
function fmtNum(v) { const n = Number(v); if (isNaN(n)) return String(v); if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1) + 'M'; if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K'; return n % 1 === 0 ? n.toLocaleString() : n.toFixed(2); }
function aggregateBy(data, g, v) { const a = {}; data.forEach(r => { const k = String(r[g] || '?'); a[k] = (a[k] || 0) + (Number(r[v]) || 0); }); return Object.entries(a).map(([l, val]) => ({ label: l, value: Math.round(val * 100) / 100 })).sort((a, b) => b.value - a.value); }
function buildDist(data, col) { const vals = data.map(r => Number(r[col])).filter(v => !isNaN(v)); if (vals.length < 5) return []; vals.sort((a, b) => a - b); const mn = vals[0], mx = vals[vals.length - 1], rng = mx - mn; if (!rng) return []; const bins = Math.min(12, Math.max(5, Math.ceil(Math.sqrt(vals.length)))), bw = rng / bins, h = Array(bins).fill(0), lb = []; for (let i = 0; i < bins; i++) { lb.push(Math.round(mn + i * bw) + '-' + Math.round(mn + (i + 1) * bw)); } vals.forEach(v => { let idx = Math.floor((v - mn) / bw); if (idx >= bins) idx = bins - 1; h[idx]++; }); return lb.map((l, i) => ({ label: l, value: h[i] })); }

// ══════════════════════════════════════════════════════════
//  MODULE 2: SIMULATION LAB
// ══════════════════════════════════════════════════════════

['Price', 'Growth', 'Churn', 'Conv'].forEach(name => {
    const slider = document.getElementById(`sim${name}`);
    const display = document.getElementById(`sim${name}Val`);
    if (slider && display) slider.addEventListener('input', () => { display.textContent = slider.value + '%'; });
});

document.getElementById('runSimBtn').addEventListener('click', async function () {
    const btn = this;
    btn.textContent = '⏳ Running...'; btn.disabled = true;

    // Get base revenue from loaded dashboard data
    let baseRev = 0;
    if (typeof DATA !== 'undefined' && DATA && DATA.kpis) {
        const rk = DATA.kpis.total_revenue || Object.values(DATA.kpis).find(k => k.label && k.label.toLowerCase().includes('revenue'));
        if (rk) baseRev = typeof rk === 'object' ? (rk.raw || parseFloat(rk.formatted?.replace(/[^0-9.-]/g, '')) || 0) : Number(rk);
    }

    try {
        const params = {
            priceChange: Number(document.getElementById('simPrice').value),
            growthRate: Number(document.getElementById('simGrowth').value),
            churnRate: Number(document.getElementById('simChurn').value),
            conversionChange: Number(document.getElementById('simConv').value),
            months: 12, baseRevenue: baseRev
        };

        const res = await fetch('/api/simulate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) });
        const result = await res.json();
        if (result.error) throw new Error(result.error);
        renderSimResults(result);
    } catch (e) {
        document.getElementById('simResults').innerHTML = `<div class="sim-placeholder"><p style="color:#f87171">❌ ${e.message}</p></div>`;
    } finally { btn.textContent = '🚀 Run Simulation'; btn.disabled = false; }
});

function renderSimResults(r) {
    const el = document.getElementById('simResults');
    const pos = r.impact.percentChange >= 0;
    let h = `<div class="sim-impact"><div class="sim-impact-val ${pos ? 'positive' : 'negative'}">${pos ? '+' : ''}${r.impact.percentChange}%</div>
    <div class="sim-impact-label">${pos ? '+' : ''}${r.impact.percentChange}% revenue impact ($${fmtNum(r.impact.delta)})</div></div>`;
    h += `<div class="sim-comparison"><div class="sim-box"><div class="sim-box-label">Baseline (12 mo)</div><div class="sim-box-val" style="color:#38bdf8">$${fmtNum(r.baseline.total)}</div></div>
    <div class="sim-box"><div class="sim-box-label">Projected (12 mo)</div><div class="sim-box-val" style="color:${pos ? '#34d399' : '#f87171'}">$${fmtNum(r.projected.total)}</div></div></div>`;
    h += '<h4 style="font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:8px">Monthly Revenue Projection</h4>';
    const mx = Math.max(...r.baseline.monthly.map(m => m.revenue), ...r.projected.monthly.map(m => m.revenue));
    r.projected.monthly.forEach((m, i) => {
        const bR = r.baseline.monthly[i].revenue, bP = (bR / mx) * 100, pP = (m.revenue / mx) * 100;
        h += `<div class="sim-month-row"><span class="sim-month-label">M${m.month}</span><div class="sim-month-bars"><div class="sim-bar baseline" style="width:${bP}%"></div><div class="sim-bar projected" style="width:${pP}%"></div></div><span class="sim-month-val" style="color:${m.revenue >= bR ? '#34d399' : '#f87171'}">$${fmtNum(m.revenue)}</span></div>`;
    });
    r.insights.forEach(ins => { h += `<div class="sim-insight-item">${ins}</div>`; });
    el.innerHTML = h;
}

// ══════════════════════════════════════════════════════════
//  MODULE 3: H.O.N.E.Y AI CHATBOT
// ══════════════════════════════════════════════════════════

let honeyOpen = false;
document.getElementById('honeyToggle').addEventListener('click', () => { honeyOpen = !honeyOpen; document.getElementById('honeyPanel').classList.toggle('open', honeyOpen); if (honeyOpen) document.getElementById('honeyInput').focus(); });
document.getElementById('honeyClose').addEventListener('click', () => { honeyOpen = false; document.getElementById('honeyPanel').classList.remove('open'); });
document.getElementById('honeyInput').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendHoney(); } });
document.getElementById('honeySend').addEventListener('click', sendHoney);

async function sendHoney() {
    const input = document.getElementById('honeyInput');
    const msg = input.value.trim();
    if (!msg) return;

    appendHoney('user', msg);
    input.value = ''; input.disabled = true;
    const tid = showHoneyTyping();

    // Build context from loaded dashboard data
    let context = '';
    if (typeof DATA !== 'undefined' && DATA) {
        const kpiList = DATA.kpis ? Object.entries(DATA.kpis).map(([k, v]) => `${v.label}: ${v.formatted}`).join(', ') : '';
        context = `DATASET CONTEXT:\n- Rows: ${DATA.metadata?.total_transactions || '?'} | Period: ${DATA.metadata?.date_range?.start || '?'} to ${DATA.metadata?.date_range?.end || '?'}\n- KPIs: ${kpiList}`;
    }

    try {
        const res = await fetch('/api/ai/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg, context }) });
        const data = await res.json();
        removeHoneyTyping(tid);
        appendHoney('assistant', formatMD(data.response || data.error || 'No response'));
    } catch (e) {
        removeHoneyTyping(tid);
        appendHoney('assistant', '⚠️ AI service unavailable. Is the server running with `node server.js`?');
    } finally { input.disabled = false; input.focus(); }
}

function appendHoney(role, html) {
    const c = document.getElementById('honeyMsgs');
    const d = document.createElement('div');
    d.className = `hmsg ${role}`;
    d.innerHTML = `<div class="hmsg-content">${html}</div>`;
    c.appendChild(d); c.scrollTop = c.scrollHeight;
}

function showHoneyTyping() {
    const c = document.getElementById('honeyMsgs');
    const d = document.createElement('div'); d.className = 'hmsg assistant'; d.id = 'honey-typing';
    d.innerHTML = '<div class="honey-typing"><span></span><span></span><span></span></div>';
    c.appendChild(d); c.scrollTop = c.scrollHeight; return 'honey-typing';
}
function removeHoneyTyping(id) { const el = document.getElementById(id); if (el) el.remove(); }

function formatMD(t) {
    if (!t) return '';
    return t.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/^- (.+)/gm, '• $1')
        .replace(/\n/g, '<br>');
}

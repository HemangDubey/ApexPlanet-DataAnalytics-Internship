// ── GravityBI — Main Application Controller ──

const API = '';
const COLORS = ['#38bdf8', '#f472b6', '#34d399', '#a78bfa', '#fb923c', '#f87171', '#facc15', '#22d3ee', '#818cf8', '#4ade80', '#e879f9', '#67e8f9', '#fbbf24', '#c084fc', '#6ee7b7'];
let APP_STATE = { dataset: null, kpis: [], charts: [], section: 'dashboard' };

// ── Navigation ──
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const sec = item.dataset.section;
        navigateTo(sec);
    });
});

function navigateTo(sec) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`[data-section="${sec}"]`);
    if (navItem) navItem.classList.add('active');
    document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section-${sec}`).classList.add('active');
    const titles = { dashboard: 'Dashboard', simulation: '🧪 Simulation Lab', upload: '📁 Upload Data' };
    document.getElementById('pageTitle').textContent = titles[sec] || 'Dashboard';
    APP_STATE.section = sec;
    if (sec === 'upload') loadDatasetList();
    if (window.innerWidth < 900) document.getElementById('sidebar').classList.remove('open');
}

document.getElementById('menuToggle').addEventListener('click', () =>
    document.getElementById('sidebar').classList.toggle('open'));

// ── API Helpers ──
async function apiGet(url) {
    const res = await fetch(API + url);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
}
async function apiPost(url, data) {
    const res = await fetch(API + url, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
}

// ── Format Helpers ──
function fmt(v, prefix = '') {
    if (v == null) return '-';
    const n = Number(v);
    if (isNaN(n)) return String(v);
    if (Math.abs(n) >= 1e6) return prefix + (n / 1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return prefix + (n / 1e3).toFixed(1) + 'K';
    return prefix + n.toFixed(n % 1 === 0 ? 0 : 2);
}

// ── HTML Bar Builder ──
function htmlBarChart(data, options = {}) {
    const { horizontal = false, prefix = '', color = null } = options;
    const max = Math.max(...data.map(d => Math.abs(Number(d.value) || 0)));
    if (!max) return '<div class="loading-placeholder">No data to display</div>';
    let html = `<div class="html-bar-chart ${horizontal ? 'horizontal' : 'vertical'}">`;
    data.forEach((d, i) => {
        const pct = (Math.abs(Number(d.value)) / max) * 100;
        const c = color || COLORS[i % COLORS.length];
        const delay = i * 40;
        const valStr = `<span class="bar-val">${fmt(d.value, prefix)}</span>`;
        if (horizontal) {
            html += `<div class="bar-row" style="animation-delay:${delay}ms">
        <span class="bar-label" title="${d.label}">${(d.label || '').substring(0, 28)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${c};animation-delay:${delay}ms"></div></div>
        ${valStr}
      </div>`;
        } else {
            html += `<div class="bar-col" style="animation-delay:${delay}ms">
        <div class="bar-vtrack"><div class="bar-vfill" style="height:${pct}%;background:${c};animation-delay:${delay}ms"></div></div>
        ${valStr}
        <span class="bar-vlabel">${(d.label || '').substring(0, 8)}</span>
      </div>`;
        }
    });
    html += '</div>';
    return html;
}

// ── Boot ──
async function initApp() {
    try {
        const summary = await apiGet('/api/data/summary');
        APP_STATE.dataset = summary;
        APP_STATE.kpis = summary.kpis || [];
        document.getElementById('datasetBadge').textContent = `📊 ${summary.name} (${summary.row_count} rows)`;
        document.getElementById('datasetMeta').textContent = `${summary.name}`;
        renderKPIs(summary.kpis);

        const chartData = await apiGet('/api/data/charts');
        APP_STATE.charts = chartData.charts || [];
        renderCharts(chartData.charts);
    } catch (e) {
        console.error('Init error:', e);
        document.getElementById('kpiGrid').innerHTML = `<div class="loading-placeholder">⚠️ Failed to load data: ${e.message}</div>`;
    }
}

// ── Upload Zone ──
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('dragover'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', e => {
    e.preventDefault(); uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleUpload(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => { if (e.target.files.length) handleUpload(e.target.files[0]); });

async function handleUpload(file) {
    if (!file.name.endsWith('.csv')) {
        document.getElementById('uploadStatus').innerHTML = '<p style="color:#f87171">❌ Only CSV files are supported.</p>';
        return;
    }
    const status = document.getElementById('uploadStatus');
    status.innerHTML = '<div class="upload-progress"><div class="upload-progress-bar"><div class="upload-progress-fill" style="width:60%"></div></div><p style="margin-top:8px;color:var(--text-secondary)">Processing...</p></div>';

    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch(API + '/api/data/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        status.innerHTML = `<p style="color:#34d399">✅ Uploaded successfully! ${data.row_count} rows, ${data.col_count} columns detected.</p>`;
        APP_STATE.dataset = data;
        APP_STATE.kpis = data.kpis;
        APP_STATE.charts = data.charts;
        document.getElementById('datasetBadge').textContent = `📊 ${data.name} (${data.row_count} rows)`;
        renderKPIs(data.kpis);
        renderCharts(data.charts);
        loadDatasetList();
    } catch (e) {
        status.innerHTML = `<p style="color:#f87171">❌ Upload failed: ${e.message}</p>`;
    }
}

async function loadDatasetList() {
    try {
        const { datasets } = await apiGet('/api/data/datasets');
        const el = document.getElementById('datasetList');
        el.innerHTML = datasets.map(d => `
      <div class="dataset-item ${d.is_active ? 'active' : ''}">
        <div class="dataset-item-info">
          <div class="dataset-item-name">${d.is_active ? '● ' : ''}${d.name}</div>
          <div class="dataset-item-meta">${d.row_count} rows × ${d.col_count} cols • ${d.created_at}</div>
        </div>
        ${d.is_active ? '<span style="color:var(--accent);font-size:11px;font-weight:700">ACTIVE</span>' :
                `<button class="btn-sm" onclick="switchDataset(${d.id})">Activate</button>`}
      </div>
    `).join('');
    } catch (e) { console.error('Failed to load datasets:', e); }
}

async function switchDataset(id) {
    try {
        await apiPost('/api/data/switch', { id });
        await initApp();
        loadDatasetList();
    } catch (e) { alert('Failed to switch dataset: ' + e.message); }
}

// ── Init on Load ──
document.addEventListener('DOMContentLoaded', initApp);

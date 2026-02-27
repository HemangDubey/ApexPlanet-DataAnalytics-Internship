/* ============================================================
   GravityBI Dashboard — Application Logic v3
   HTML-rendered bars for reliability, Chart.js for lines/pies
   ============================================================ */

let DATA = null;
let renderedSections = {};

async function loadData() {
    try {
        const res = await fetch('dashboard_data.json');
        DATA = await res.json();
        initDashboard();
    } catch (e) {
        document.getElementById('mainContent').innerHTML =
            `<div style="padding:60px;text-align:center;color:#f87171">
        <h2>Failed to load data</h2>
        <p style="color:#8899b4;margin-top:8px">Ensure dashboard_data.json is in the same folder.</p>
      </div>`;
    }
}

function initDashboard() {
    setupNav();
    setDateRange();
    renderKPIs();
    renderSecondaryMetrics();
    renderOverviewCharts();
    renderedSections['overview'] = true;
}

function setupNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            const sec = item.dataset.section;
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
            document.getElementById(`section-${sec}`).classList.add('active');
            const titles = {
                overview: 'Dashboard Overview', eda: 'Advanced EDA', cohort: 'Cohort & RFM Segmentation',
                sql: 'SQL Business Intelligence', insights: 'Strategic Insights', 'kpi-detail': 'KPI Reference'
            };
            document.getElementById('pageTitle').textContent = titles[sec] || 'Dashboard';
            if (window.innerWidth < 900) document.getElementById('sidebar').classList.remove('open');
            requestAnimationFrame(() => renderSectionIfNeeded(sec));
        });
    });
    document.getElementById('menuToggle').addEventListener('click', () =>
        document.getElementById('sidebar').classList.toggle('open'));
}

function renderSectionIfNeeded(sec) {
    if (renderedSections[sec]) return;
    renderedSections[sec] = true;
    switch (sec) {
        case 'eda': renderEDA(); break;
        case 'cohort': renderCohort(); renderRFM(); break;
        case 'sql': renderSQL(); break;
        case 'insights': renderInsights(); break;
        case 'kpi-detail': renderKPIDetail(); break;
    }
}

function setDateRange() {
    if (!DATA.metadata) return;
    const s = new Date(DATA.metadata.date_range.start).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
    const e = new Date(DATA.metadata.date_range.end).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
    document.getElementById('dateRange').textContent = `${s} — ${e}`;
}

// ── Utilities ──
const COLORS = ['#38bdf8', '#f472b6', '#34d399', '#a78bfa', '#fb923c', '#f87171', '#facc15', '#22d3ee', '#818cf8', '#4ade80', '#e879f9', '#67e8f9', '#fbbf24', '#c084fc', '#6ee7b7'];
Chart.defaults.color = '#8899b4';
Chart.defaults.borderColor = 'rgba(56,189,248,0.06)';
Chart.defaults.font.family = "'Inter',sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(18,27,46,0.95)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(56,189,248,0.3)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.scale.grid = { color: 'rgba(56,189,248,0.04)' };

function num(v) { return v == null ? 0 : typeof v === 'number' ? v : parseFloat(v) || 0; }
function fmt(v, prefix = '') {
    if (v == null) return '-'; const n = num(v);
    if (Math.abs(n) >= 1e6) return prefix + (n / 1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return prefix + (n / 1e3).toFixed(1) + 'K';
    return prefix + n.toFixed(n % 1 === 0 ? 0 : 2);
}

// ── HTML Bar Chart Builder ──
function htmlBarChart(container, data, options = {}) {
    const { horizontal = false, color = '#38bdf8', showLabels = true, showValues = true,
        prefix = '', maxVal = null, barHeight = 28, animDelay = 0 } = options;
    const max = maxVal || Math.max(...data.map(d => num(d.value)));
    if (!max) return;

    let html = `<div class="html-bar-chart ${horizontal ? 'horizontal' : 'vertical'}">`;
    data.forEach((d, i) => {
        const pct = (num(d.value) / max) * 100;
        const c = d.color || COLORS[i % COLORS.length];
        const delay = animDelay + i * 50;
        const valStr = showValues ? `<span class="bar-val">${fmt(d.value, prefix)}</span>` : '';
        if (horizontal) {
            html += `<div class="bar-row" style="animation-delay:${delay}ms">
        ${showLabels ? `<span class="bar-label" title="${d.label}">${(d.label || '').substring(0, 30)}</span>` : ''}
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${c};animation-delay:${delay}ms"></div></div>
        ${valStr}
      </div>`;
        } else {
            html += `<div class="bar-col" style="animation-delay:${delay}ms">
        <div class="bar-vtrack"><div class="bar-vfill" style="height:${pct}%;background:${c};animation-delay:${delay}ms"></div></div>
        ${valStr}
        ${showLabels ? `<span class="bar-vlabel">${d.label || ''}</span>` : ''}
      </div>`;
        }
    });
    html += '</div>';
    if (typeof container === 'string') document.getElementById(container).innerHTML = html;
    else container.innerHTML = html;
}

// ── KPIs ──
function renderKPIs() {
    const kpis = DATA.kpis;
    const colors = ['#34d399', '#38bdf8', '#a78bfa', '#fb923c', '#f472b6', '#f87171', '#22d3ee', '#facc15'];
    const grid = document.getElementById('kpiGrid');
    let html = '', i = 0;
    for (const [key, kpi] of Object.entries(kpis)) {
        const c = colors[i % colors.length];
        html += `<div class="kpi-card" style="--kpi-color:${c}">
      <span class="kpi-badge ${kpi.type}">${kpi.type}</span>
      <div class="kpi-icon">${kpi.icon || ''}</div>
      <div class="kpi-value" style="color:${c}">${kpi.formatted}</div>
      <div class="kpi-label">${kpi.label}</div>
    </div>`;
        i++;
    }
    grid.innerHTML = html;
}

function renderSecondaryMetrics() {
    const sm = DATA.secondary_metrics;
    const el = document.getElementById('secondaryMetrics');
    let html = '';
    for (const [k, m] of Object.entries(sm)) {
        html += `<div class="sec-metric">
      <div class="sec-icon">${m.icon || ''}</div>
      <div class="sec-val">${m.formatted}</div>
      <div class="sec-lbl">${m.label}</div>
    </div>`;
    }
    el.innerHTML = html;
}

// ══════════════════════════════════════════════════════════
//  OVERVIEW CHARTS
// ══════════════════════════════════════════════════════════
let trendChart = null;

function renderOverviewCharts() {
    renderTrendChart('revenue');
    renderCountryBars();
    renderWeekdayBars();
    renderProductBars();
    renderHourlyBars();
}

function renderTrendChart(metric) {
    const d = DATA.monthly_trend; if (!d || !d.length) return;
    const labels = d.map(r => r.month_label);
    const values = d.map(r => num(r[metric]));
    if (trendChart) trendChart.destroy();
    trendChart = new Chart(document.getElementById('chartRevenueTrend'), {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: metric.charAt(0).toUpperCase() + metric.slice(1),
                data: values, fill: true,
                backgroundColor: 'rgba(56,189,248,0.08)', borderColor: '#38bdf8', borderWidth: 2.5,
                pointBackgroundColor: '#38bdf8', pointRadius: 4, pointHoverRadius: 7, tension: 0.35,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { ticks: { callback: v => fmt(v, metric === 'revenue' ? '£' : '') } } },
            plugins: { legend: { position: 'top' } }
        }
    });
}

function toggleTrendMetric(m, btn) {
    document.querySelectorAll('#revenueTrendCard .chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    renderTrendChart(m);
}

function renderCountryBars() {
    const d = (DATA.revenue_by_country || []).slice(0, 10);
    if (!d.length) return;
    const container = document.getElementById('chartCountry').parentElement;
    htmlBarChart(container, d.map((r, i) => ({
        label: r.country, value: r.revenue, color: COLORS[i % COLORS.length]
    })), { horizontal: true, prefix: '£', barHeight: 26 });
}

function renderWeekdayBars() {
    const d = DATA.weekday_pattern; if (!d || !d.length) return;
    const container = document.getElementById('chartWeekday').parentElement;
    htmlBarChart(container, d.map((r, i) => ({
        label: r.day, value: r.revenue, color: COLORS[i % COLORS.length]
    })), { horizontal: false, prefix: '£' });
}

function renderProductBars() {
    const d = (DATA.top_products || []).slice(0, 15);
    if (!d.length) return;
    const container = document.getElementById('chartProducts').parentElement;
    htmlBarChart(container, d.map((r, i) => ({
        label: r.description || '', value: r.revenue, color: COLORS[i % COLORS.length]
    })), { horizontal: true, prefix: '£', barHeight: 22 });
}

function renderHourlyBars() {
    const d = DATA.hourly_pattern; if (!d || !d.length) return;
    const container = document.getElementById('chartHourly').parentElement;
    htmlBarChart(container, d.map((r, i) => ({
        label: r.hour + ':00', value: r.revenue, color: `rgba(56,189,248,${0.3 + 0.7 * (num(r.revenue) / Math.max(...d.map(x => num(x.revenue))))})`
    })), { horizontal: false, prefix: '£' });
}

// ══════════════════════════════════════════════════════════
//  EDA SECTION
// ══════════════════════════════════════════════════════════
function renderEDA() {
    renderStatsGrid();
    renderDistBars();
    renderCustFreqBars();
    renderCorrelationHeatmap();
    renderParetoChart();
}

function renderStatsGrid() {
    const stats = DATA.univariate_stats; if (!stats) return;
    const grid = document.getElementById('statsGrid');
    let html = '';
    for (const [col, s] of Object.entries(stats)) {
        const pre = (col === 'revenue' || col === 'price') ? '£' : '';
        const fields = [
            ['Mean', fmt(s.mean, pre)], ['Median', fmt(s.median, pre)],
            ['Std Dev', fmt(s.std)], ['Skewness', num(s.skewness).toFixed(2)],
            ['Kurtosis', num(s.kurtosis).toFixed(2)], ['IQR', fmt(s.iqr, pre)],
            ['P25', fmt(s.p25, pre)], ['P75', fmt(s.p75, pre)],
            ['P95', fmt(s.p95, pre)], ['P99', fmt(s.p99, pre)],
        ];
        html += `<div class="stat-block"><h4>${col}</h4>${fields.map(([l, v]) =>
            `<div class="stat-row"><span class="stat-label">${l}</span><span class="stat-value">${v}</span></div>`
        ).join('')}</div>`;
    }
    grid.innerHTML = html;
}

function renderDistBars() {
    const rd = DATA.revenue_distribution;
    if (rd && rd.counts && rd.counts.length) {
        const container = document.getElementById('chartRevDist').parentElement;
        htmlBarChart(container, rd.counts.map((c, i) => ({
            label: '£' + Math.round(rd.edges[i]) + '-' + Math.round(rd.edges[i + 1]),
            value: c, color: 'rgba(56,189,248,0.6)'
        })), { horizontal: false, prefix: '', showLabels: true });
    }
    const qd = DATA.quantity_distribution;
    if (qd && qd.counts && qd.counts.length) {
        const container = document.getElementById('chartQtyDist').parentElement;
        htmlBarChart(container, qd.counts.map((c, i) => ({
            label: Math.round(qd.edges[i]) + '-' + Math.round(qd.edges[i + 1]),
            value: c, color: 'rgba(52,211,153,0.6)'
        })), { horizontal: false, prefix: '', showLabels: true });
    }
}

function renderCustFreqBars() {
    const cf = DATA.customer_frequency;
    if (!cf || !cf.customers || !cf.customers.length) return;
    const container = document.getElementById('chartCustFreq').parentElement;
    htmlBarChart(container, cf.orders.map((o, i) => ({
        label: o + ' orders', value: cf.customers[i], color: 'rgba(167,139,250,0.6)'
    })), { horizontal: false, prefix: '' });
}

function renderCorrelationHeatmap() {
    const cm = DATA.correlation_matrix;
    if (!cm || !cm.values) return;
    const container = document.getElementById('chartCorrelation').parentElement;
    const cols = cm.columns, vals = cm.values;
    let html = '<div style="display:flex;justify-content:center;align-items:center;height:100%;padding:16px">';
    html += '<table style="border-collapse:separate;border-spacing:3px;margin:auto">';
    html += '<tr><td></td>';
    cols.forEach(c => { html += `<td style="padding:8px 12px;font-size:11px;font-weight:600;color:#8899b4;text-align:center">${c}</td>`; });
    html += '</tr>';
    for (let i = 0; i < cols.length; i++) {
        html += `<tr><td style="padding:8px 12px;font-size:11px;font-weight:600;color:#8899b4;text-align:right">${cols[i]}</td>`;
        for (let j = 0; j < cols.length; j++) {
            const v = vals[i][j], abs = Math.abs(v);
            let bg, txt;
            if (v > 0.5) { bg = `rgba(52,211,153,${0.3 + abs * 0.5})`; txt = '#fff'; }
            else if (v > 0.1) { bg = `rgba(56,189,248,${0.2 + abs * 0.4})`; txt = '#e8edf5'; }
            else if (v < -0.1) { bg = `rgba(248,113,113,${0.2 + abs * 0.5})`; txt = '#e8edf5'; }
            else { bg = 'rgba(255,255,255,0.04)'; txt = '#8899b4'; }
            html += `<td style="padding:10px 14px;text-align:center;font-family:'JetBrains Mono',monospace;
        font-size:13px;font-weight:700;background:${bg};color:${txt};border-radius:6px;min-width:70px">${v != null ? v.toFixed(2) : '-'}</td>`;
        }
        html += '</tr>';
    }
    html += '</table></div>';
    container.innerHTML = html;
}

function renderParetoChart() {
    const p = DATA.pareto; if (!p) return;
    document.getElementById('paretoInsight').textContent = p.insight || '';
    new Chart(document.getElementById('chartPareto'), {
        type: 'line',
        data: {
            labels: p.customer_pct.map(v => v.toFixed(0) + '%'),
            datasets: [{
                label: 'Cumulative Revenue %', data: p.revenue_pct,
                borderColor: '#fb923c', backgroundColor: 'rgba(251,146,60,0.12)', fill: true,
                pointRadius: 0, borderWidth: 2.5, tension: 0.3
            }, {
                label: '80% Line', data: p.customer_pct.map(() => 80),
                borderColor: 'rgba(248,113,113,0.4)', borderDash: [6, 4], borderWidth: 1.5,
                pointRadius: 0, fill: false,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: { ticks: { maxTicksLimit: 10 }, title: { display: true, text: '% of Customers', color: '#8899b4' } },
                y: { ticks: { callback: v => v + '%' }, title: { display: true, text: '% of Revenue', color: '#8899b4' }, max: 105 }
            },
            plugins: { legend: { display: true, position: 'top' } }
        }
    });
}

// ══════════════════════════════════════════════════════════
//  COHORT & RFM
// ══════════════════════════════════════════════════════════
function renderCohort() {
    const ch = DATA.cohort_retention; if (!ch) return;
    const container = document.getElementById('cohortHeatmap');
    let html = '<table class="heatmap-table"><thead><tr><th>Cohort</th><th>Size</th>';
    ch.periods.forEach(p => { html += `<th>M${p}</th>`; }); html += '</tr></thead><tbody>';
    ch.cohorts.forEach((cohort, i) => {
        html += `<tr><td class="cohort-label">${cohort}</td><td style="color:#8899b4">${ch.cohort_sizes[i]?.toFixed(0) || '-'}</td>`;
        ch.values[i].forEach(v => {
            const pct = v != null ? v : 0;
            const hue = pct > 50 ? 152 : pct > 25 ? 45 : 0;
            const light = Math.min(50, 12 + pct * 0.4);
            const txtColor = pct > 30 ? '#fff' : '#8899b4';
            html += `<td style="background:hsl(${hue},65%,${light}%);color:${txtColor}">${pct > 0 ? pct.toFixed(0) + '%' : '-'}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderRFM() {
    const segs = DATA.rfm_segments; if (!segs || !segs.length) return;
    // Doughnut — works fine
    new Chart(document.getElementById('chartRFMPie'), {
        type: 'doughnut',
        data: {
            labels: segs.map(s => s.segment),
            datasets: [{
                data: segs.map(s => num(s.count)),
                backgroundColor: COLORS.slice(0, segs.length).map(c => c + 'cc'),
                borderColor: '#121b2e', borderWidth: 2, hoverOffset: 8
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '55%',
            plugins: { legend: { position: 'right', labels: { font: { size: 11 }, padding: 8, color: '#c9d1d9' } } }
        }
    });

    // Revenue bars — HTML
    const revContainer = document.getElementById('chartRFMRevenue').parentElement;
    htmlBarChart(revContainer, segs.map((s, i) => ({
        label: s.segment, value: s.total_revenue, color: COLORS[i % COLORS.length]
    })), { horizontal: true, prefix: '£', barHeight: 26 });

    // Table
    const el = document.getElementById('rfmTable');
    const segColors = {
        'VIP / Champions': '#34d399', 'Loyal Customers': '#38bdf8', 'At Risk': '#fb923c',
        "Can't Lose Them": '#f87171', 'Dormant / Lost': '#64748b', 'New Customers': '#a78bfa',
        'Potential Loyalists': '#22d3ee', 'Need Attention': '#facc15'
    };
    let html = `<table class="data-table"><thead><tr>
    <th>Segment</th><th>Customers</th><th>% Cust</th><th>% Rev</th><th>Avg Recency</th>
    <th>Avg Freq</th><th>Avg Monetary</th><th>Total Revenue</th><th>Recommended Action</th>
  </tr></thead><tbody>`;
    segs.forEach(s => {
        const dot = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${segColors[s.segment] || '#8899b4'};margin-right:6px"></span>`;
        html += `<tr>
      <td>${dot}<strong>${s.segment}</strong></td>
      <td>${fmt(s.count)}</td><td>${num(s.pct_customers).toFixed(1)}%</td><td>${num(s.pct_revenue).toFixed(1)}%</td>
      <td>${num(s.avg_recency).toFixed(0)}d</td><td>${num(s.avg_frequency).toFixed(1)}</td>
      <td>£${fmt(s.avg_monetary)}</td><td>£${fmt(s.total_revenue)}</td>
      <td class="action-cell">${s.action || '-'}</td>
    </tr>`;
    });
    html += '</tbody></table>';
    el.innerHTML = html;
}

// ══════════════════════════════════════════════════════════
//  SQL
// ══════════════════════════════════════════════════════════
function renderSQL() {
    const queries = DATA.sql_queries; if (!queries || !queries.length) return;
    document.getElementById('sqlTabs').innerHTML = queries.map((q, i) =>
        `<button class="sql-tab ${i === 0 ? 'active' : ''}" onclick="showSQL(${i})" id="sqlTab${i}">Q${q.id}: ${q.title}</button>`
    ).join('');
    showSQL(0);
}
function showSQL(idx) {
    const q = DATA.sql_queries[idx];
    document.querySelectorAll('.sql-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`sqlTab${idx}`).classList.add('active');
    document.getElementById('sqlCode').innerHTML = `<h4>SQL Query</h4><pre>${escapeHtml(q.sql)}</pre>`;
    let rh = `<h4>Result (${q.row_count} rows)</h4>`;
    if (q.data && q.data.length) {
        rh += '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
        q.columns.forEach(c => { rh += `<th>${c}</th>`; });
        rh += '</tr></thead><tbody>';
        q.data.forEach(row => {
            rh += '<tr>'; q.columns.forEach(c => {
                let val = row[c]; if (typeof val === 'number') val = val.toLocaleString();
                rh += `<td>${val != null ? val : '-'}</td>`;
            }); rh += '</tr>';
        });
        rh += '</tbody></table></div>';
    } else { rh += '<p style="color:#5a6d8a">No results</p>'; }
    document.getElementById('sqlResult').innerHTML = rh;
}
function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

// ══════════════════════════════════════════════════════════
//  INSIGHTS
// ══════════════════════════════════════════════════════════
function renderInsights() {
    const bi = DATA.business_insights; if (!bi) return;
    document.getElementById('strategicInsights').innerHTML = (bi.strategic_insights || []).map(i => `
    <div class="insight-card">
      <div class="insight-num">INSIGHT #${i.id}</div>
      <div class="insight-cat">${i.category}</div>
      <div class="insight-text">${i.insight}</div>
      <div class="insight-rec">&#8594; ${i.recommendation}</div>
      <div class="insight-meta">
        <span class="insight-tag tag-${i.impact?.toLowerCase()}">${i.impact} Impact</span>
        <span class="insight-tag tag-${i.priority === 'Critical' ? 'critical' : i.priority?.toLowerCase()}">${i.priority}</span>
      </div>
    </div>`).join('');
    document.getElementById('revenueOpps').innerHTML = (bi.revenue_opportunities || []).map(o => `
    <div class="opp-card"><div class="opp-title">${o.id}. ${o.strategy}</div><div class="opp-desc">${o.description}</div><div class="opp-impact">${o.estimated_impact}</div></div>`).join('');
    document.getElementById('costOpts').innerHTML = (bi.cost_optimizations || []).map(o => `
    <div class="opp-card"><div class="opp-title">${o.id}. ${o.area}</div><div class="opp-desc">${o.description}</div></div>`).join('');
    document.getElementById('riskAreas').innerHTML = (bi.risk_areas || []).map(r => `
    <div class="risk-card"><span class="risk-icon">&#9888;</span><span>${r.risk}</span></div>`).join('');
}

// ══════════════════════════════════════════════════════════
//  KPI DETAIL
// ══════════════════════════════════════════════════════════
function renderKPIDetail() {
    const ref = DATA.indicator_reference;
    if (ref) {
        document.getElementById('indicatorLegend').innerHTML = `
      <div class="legend-item"><h4 style="color:#34d399">Leading Indicators</h4>
        <p>${ref.leading_indicators.definition}</p>
        <p style="margin-top:4px"><strong>Examples:</strong> ${ref.leading_indicators.examples.join(', ')}</p></div>
      <div class="legend-item"><h4 style="color:#38bdf8">Lagging Indicators</h4>
        <p>${ref.lagging_indicators.definition}</p>
        <p style="margin-top:4px"><strong>Examples:</strong> ${ref.lagging_indicators.examples.join(', ')}</p></div>
      <div class="legend-item"><h4 style="color:#f472b6">Vanity vs Actionable</h4>
        <p><strong>Vanity:</strong> ${ref.vanity_vs_actionable.vanity}</p>
        <p><strong>Actionable:</strong> ${ref.vanity_vs_actionable.actionable}</p></div>`;
    }
    const kpis = DATA.kpis, grid = document.getElementById('kpiDetailGrid');
    let html = '';
    for (const [key, kpi] of Object.entries(kpis)) {
        html += `<div class="kpi-detail-card">
      <div class="kpi-detail-left">
        <h4>${kpi.icon || ''} ${kpi.label} <span class="kpi-badge ${kpi.type}" style="position:static;font-size:9px">${kpi.type}</span></h4>
        <div class="kpi-detail-row"><strong>Value:</strong> ${kpi.formatted}</div>
        <div class="kpi-detail-row"><strong>Formula:</strong> ${kpi.formula}</div>
        <div class="kpi-detail-row"><strong>Category:</strong> ${kpi.category}</div>
      </div>
      <div class="kpi-detail-right">
        <div class="kpi-sql">${escapeHtml(kpi.sql || '')}</div>
        <div class="kpi-interp">${kpi.interpretation || ''}</div>
      </div>
    </div>`;
    }
    grid.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', loadData);

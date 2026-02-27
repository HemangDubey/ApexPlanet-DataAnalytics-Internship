/* ============================================================
   GravityBI Dashboard — Application Logic
   ============================================================ */

let DATA = null;
let charts = {};

// ── Load Data ──
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
        <pre style="color:#5a6d8a;margin-top:12px;font-size:12px">${e.message}</pre>
      </div>`;
    }
}

// ── Init ──
function initDashboard() {
    setupNav();
    setDateRange();
    renderKPIs();
    renderSecondaryMetrics();
    renderOverviewCharts();
    renderEDA();
    renderCohort();
    renderRFM();
    renderSQL();
    renderInsights();
    renderKPIDetail();
}

// ── Navigation ──
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
        });
    });
    document.getElementById('menuToggle').addEventListener('click', () =>
        document.getElementById('sidebar').classList.toggle('open'));
}

function setDateRange() {
    if (!DATA.metadata) return;
    const s = new Date(DATA.metadata.date_range.start).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
    const e = new Date(DATA.metadata.date_range.end).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
    document.getElementById('dateRange').textContent = `${s} — ${e}`;
}

// ── Chart Defaults ──
const COLORS = ['#38bdf8', '#f472b6', '#34d399', '#a78bfa', '#fb923c', '#f87171', '#facc15', '#22d3ee', '#818cf8', '#4ade80'];
Chart.defaults.color = '#8899b4';
Chart.defaults.borderColor = 'rgba(56,189,248,0.06)';
Chart.defaults.font.family = "'Inter',sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;
Chart.defaults.plugins.tooltip.backgroundColor = '#121b2e';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(56,189,248,0.2)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.scale.grid = { color: 'rgba(56,189,248,0.04)' };

function num(v) { return v == null ? 0 : typeof v === 'number' ? v : parseFloat(v) || 0; }
function fmt(v, prefix = '') {
    if (v == null) return '-';
    const n = num(v);
    if (Math.abs(n) >= 1e6) return prefix + (n / 1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return prefix + (n / 1e3).toFixed(1) + 'K';
    return prefix + n.toFixed(n % 1 === 0 ? 0 : 2);
}

// ── KPIs ──
function renderKPIs() {
    const kpis = DATA.kpis;
    const colors = ['#34d399', '#38bdf8', '#a78bfa', '#fb923c', '#f472b6', '#f87171', '#22d3ee', '#facc15'];
    const grid = document.getElementById('kpiGrid');
    let html = '';
    let i = 0;
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

// ── Overview Charts ──
let trendChart = null;
function renderOverviewCharts() {
    renderTrendChart('revenue');
    renderCountryChart();
    renderWeekdayChart();
    renderProductsChart();
    renderHourlyChart();
}

function renderTrendChart(metric) {
    const d = DATA.monthly_trend;
    if (!d || !d.length) return;
    const labels = d.map(r => r.month_label);
    const values = d.map(r => num(r[metric]));
    const growth = d.map(r => r.mom_growth);
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
            }, metric === 'revenue' ? {
                label: 'MoM Growth %', data: growth, type: 'bar',
                backgroundColor: growth.map(v => v != null && v < 0 ? 'rgba(248,113,113,0.4)' : 'rgba(52,211,153,0.3)'),
                borderColor: growth.map(v => v != null && v < 0 ? '#f87171' : '#34d399'),
                borderWidth: 1, yAxisID: 'y1', barPercentage: 0.5,
            } : null].filter(Boolean)
        },
        options: {
            responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
            scales: {
                y: { ticks: { callback: v => fmt(v, metric === 'revenue' ? '£' : '') } },
                y1: metric === 'revenue' ? { position: 'right', ticks: { callback: v => v + '%' }, grid: { display: false } } : undefined
            },
            plugins: { legend: { position: 'top' } }
        }
    });
}

function toggleTrendMetric(m, btn) {
    document.querySelectorAll('#revenueTrendCard .chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    renderTrendChart(m);
}

function renderCountryChart() {
    const d = (DATA.revenue_by_country || []).slice(0, 10);
    if (!d.length) return;
    new Chart(document.getElementById('chartCountry'), {
        type: 'bar',
        data: {
            labels: d.map(r => r.country),
            datasets: [{
                label: 'Revenue (GBP)', data: d.map(r => num(r.revenue)),
                backgroundColor: COLORS.map(c => c + '90'), borderColor: COLORS, borderWidth: 1, borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            scales: { x: { ticks: { callback: v => fmt(v, '£') } } },
            plugins: { legend: { display: false } }
        }
    });
}

function renderWeekdayChart() {
    const d = DATA.weekday_pattern;
    if (!d || !d.length) return;
    new Chart(document.getElementById('chartWeekday'), {
        type: 'bar',
        data: {
            labels: d.map(r => r.day),
            datasets: [
                { label: 'Revenue', data: d.map(r => num(r.revenue)), backgroundColor: '#38bdf8aa', borderColor: '#38bdf8', borderWidth: 1, borderRadius: 6, yAxisID: 'y' },
                { label: 'Orders', data: d.map(r => num(r.orders)), type: 'line', borderColor: '#f472b6', backgroundColor: 'transparent', pointRadius: 4, yAxisID: 'y1', tension: 0.3 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { ticks: { callback: v => fmt(v, '£') } },
                y1: { position: 'right', grid: { display: false }, ticks: { callback: v => fmt(v) } }
            }
        }
    });
}

function renderProductsChart() {
    const d = (DATA.top_products || []).slice(0, 15);
    if (!d.length) return;
    new Chart(document.getElementById('chartProducts'), {
        type: 'bar',
        data: {
            labels: d.map(r => (r.description || '').substring(0, 35)),
            datasets: [{
                label: 'Revenue', data: d.map(r => num(r.revenue)),
                backgroundColor: COLORS.concat(COLORS).map(c => c + '90'), borderColor: COLORS.concat(COLORS), borderWidth: 1, borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            scales: { x: { ticks: { callback: v => fmt(v, '£') } } },
            plugins: { legend: { display: false } }
        }
    });
}

function renderHourlyChart() {
    const d = DATA.hourly_pattern;
    if (!d || !d.length) return;
    new Chart(document.getElementById('chartHourly'), {
        type: 'bar',
        data: {
            labels: d.map(r => r.hour + ':00'),
            datasets: [
                { label: 'Revenue', data: d.map(r => num(r.revenue)), backgroundColor: '#38bdf860', borderColor: '#38bdf8', borderWidth: 1, borderRadius: 4, yAxisID: 'y' },
                { label: 'Orders', data: d.map(r => num(r.orders)), type: 'line', borderColor: '#fb923c', pointBackgroundColor: '#fb923c', pointRadius: 3, yAxisID: 'y1', tension: 0.3 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { ticks: { callback: v => fmt(v, '£') } },
                y1: { position: 'right', grid: { display: false } }
            }
        }
    });
}

// ── EDA Section ──
function renderEDA() {
    renderStatsGrid();
    renderDistributionCharts();
    renderCustFreqChart();
    renderCorrelationChart();
    renderParetoChart();
}

function renderStatsGrid() {
    const stats = DATA.univariate_stats;
    if (!stats) return;
    const grid = document.getElementById('statsGrid');
    let html = '';
    for (const [col, s] of Object.entries(stats)) {
        const fields = [
            ['Mean', fmt(s.mean, col === 'revenue' || col === 'price' ? '£' : '')],
            ['Median', fmt(s.median, col === 'revenue' || col === 'price' ? '£' : '')],
            ['Std Dev', fmt(s.std)], ['Skewness', num(s.skewness).toFixed(2)],
            ['IQR', fmt(s.iqr)], ['P95', fmt(s.p95, col === 'revenue' || col === 'price' ? '£' : '')],
        ];
        html += `<div class="stat-block"><h4>${col}</h4>${fields.map(([l, v]) =>
            `<div class="stat-row"><span class="stat-label">${l}</span><span class="stat-value">${v}</span></div>`
        ).join('')}</div>`;
    }
    grid.innerHTML = html;
}

function renderDistributionCharts() {
    const rd = DATA.revenue_distribution;
    if (rd) {
        new Chart(document.getElementById('chartRevDist'), {
            type: 'bar',
            data: {
                labels: rd.edges.slice(0, -1).map(v => fmt(v, '£')),
                datasets: [{ data: rd.counts, backgroundColor: '#38bdf860', borderColor: '#38bdf8', borderWidth: 1, borderRadius: 2 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
                scales: { x: { ticks: { maxTicksLimit: 10 } }, y: { ticks: { callback: v => fmt(v) } } }
            }
        });
    }
    const qd = DATA.quantity_distribution;
    if (qd) {
        new Chart(document.getElementById('chartQtyDist'), {
            type: 'bar',
            data: {
                labels: qd.edges.slice(0, -1).map(v => Math.round(v)),
                datasets: [{ data: qd.counts, backgroundColor: '#34d39960', borderColor: '#34d399', borderWidth: 1, borderRadius: 2 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
                scales: { x: { ticks: { maxTicksLimit: 10 } }, y: { ticks: { callback: v => fmt(v) } } }
            }
        });
    }
}

function renderCustFreqChart() {
    const cf = DATA.customer_frequency;
    if (!cf) return;
    new Chart(document.getElementById('chartCustFreq'), {
        type: 'bar',
        data: {
            labels: cf.orders.map(v => v + ' orders'),
            datasets: [{
                label: 'Customers', data: cf.customers,
                backgroundColor: '#a78bfa60', borderColor: '#a78bfa', borderWidth: 1, borderRadius: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { y: { ticks: { callback: v => fmt(v) } } }
        }
    });
}

function renderCorrelationChart() {
    const cm = DATA.correlation_matrix;
    if (!cm) return;
    const canvas = document.getElementById('chartCorrelation');
    const ctx = canvas.getContext('2d');
    const cols = cm.columns;
    const vals = cm.values;
    const size = cols.length;
    const cellSize = Math.min(60, (canvas.parentElement.clientWidth - 80) / size);

    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 280;
    const ox = 80, oy = 40;

    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            const v = vals[i][j];
            const r = Math.round(130 + (v > 0 ? 0 : Math.abs(v) * 120));
            const g = Math.round(130 + (v > 0 ? v * 100 : 0));
            const b = Math.round(200 + (v > 0 ? v * 55 : -Math.abs(v) * 80));
            ctx.fillStyle = `rgb(${Math.min(255, r)},${Math.min(255, g)},${Math.min(255, b)})`;
            ctx.fillRect(ox + j * cellSize, oy + i * cellSize, cellSize - 2, cellSize - 2);
            ctx.fillStyle = '#e8edf5';
            ctx.font = '11px JetBrains Mono';
            ctx.textAlign = 'center';
            ctx.fillText(v != null ? v.toFixed(2) : '-', ox + j * cellSize + cellSize / 2, oy + i * cellSize + cellSize / 2 + 4);
        }
    }
    ctx.fillStyle = '#8899b4';
    ctx.font = '11px Inter';
    cols.forEach((c, i) => {
        ctx.textAlign = 'right';
        ctx.fillText(c, ox - 6, oy + i * cellSize + cellSize / 2 + 4);
        ctx.textAlign = 'center';
        ctx.fillText(c, ox + i * cellSize + cellSize / 2, oy - 8);
    });
}

function renderParetoChart() {
    const p = DATA.pareto;
    if (!p) return;
    document.getElementById('paretoInsight').textContent = p.insight || '';
    new Chart(document.getElementById('chartPareto'), {
        type: 'line',
        data: {
            labels: p.customer_pct.map(v => v.toFixed(0) + '%'),
            datasets: [{
                label: 'Cumulative Revenue %', data: p.revenue_pct,
                borderColor: '#fb923c', backgroundColor: 'rgba(251,146,60,0.1)', fill: true,
                pointRadius: 0, borderWidth: 2.5, tension: 0.3
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: { ticks: { maxTicksLimit: 10 }, title: { display: true, text: '% of Customers' } },
                y: { ticks: { callback: v => v + '%' }, title: { display: true, text: '% of Revenue' } }
            },
            plugins: {
                annotation: undefined,
                legend: { display: false }
            }
        }
    });
}

// ── Cohort ──
function renderCohort() {
    const ch = DATA.cohort_retention;
    if (!ch) return;
    const container = document.getElementById('cohortHeatmap');
    let html = '<table class="heatmap-table"><thead><tr><th>Cohort</th><th>Size</th>';
    ch.periods.forEach(p => { html += `<th>M${p}</th>`; });
    html += '</tr></thead><tbody>';
    ch.cohorts.forEach((cohort, i) => {
        html += `<tr><td class="cohort-label">${cohort}</td><td style="color:#8899b4">${ch.cohort_sizes[i]?.toFixed(0) || '-'}</td>`;
        ch.values[i].forEach((v, j) => {
            const pct = v != null ? v : 0;
            const hue = pct > 50 ? 160 : pct > 25 ? 45 : 0;
            const sat = 70;
            const light = 15 + pct * 0.35;
            const txtColor = pct > 30 ? '#fff' : '#8899b4';
            html += `<td style="background:hsl(${hue},${sat}%,${light}%);color:${txtColor}">${pct > 0 ? pct.toFixed(0) + '%' : '-'}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

// ── RFM ──
function renderRFM() {
    const segs = DATA.rfm_segments;
    if (!segs || !segs.length) return;

    // Pie chart
    new Chart(document.getElementById('chartRFMPie'), {
        type: 'doughnut',
        data: {
            labels: segs.map(s => s.segment),
            datasets: [{
                data: segs.map(s => num(s.count)),
                backgroundColor: COLORS.slice(0, segs.length).map(c => c + 'cc'),
                borderColor: '#121b2e', borderWidth: 2
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '55%',
            plugins: { legend: { position: 'right', labels: { font: { size: 11 }, padding: 8 } } }
        }
    });

    // Revenue bar
    new Chart(document.getElementById('chartRFMRevenue'), {
        type: 'bar',
        data: {
            labels: segs.map(s => s.segment),
            datasets: [
                {
                    label: 'Revenue', data: segs.map(s => num(s.total_revenue)),
                    backgroundColor: COLORS.slice(0, segs.length).map(c => c + '80'),
                    borderColor: COLORS.slice(0, segs.length), borderWidth: 1, borderRadius: 6
                }
            ]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            scales: { x: { ticks: { callback: v => fmt(v, '£') } } },
            plugins: { legend: { display: false } }
        }
    });

    // Table
    const el = document.getElementById('rfmTable');
    let html = `<table class="data-table"><thead><tr>
    <th>Segment</th><th>Customers</th><th>% Customers</th><th>Avg Recency</th>
    <th>Avg Frequency</th><th>Avg Monetary</th><th>Total Revenue</th><th>Recommended Action</th>
  </tr></thead><tbody>`;
    segs.forEach(s => {
        html += `<tr>
      <td><strong>${s.segment}</strong></td>
      <td>${fmt(s.count)}</td><td>${num(s.pct_customers).toFixed(1)}%</td>
      <td>${num(s.avg_recency).toFixed(0)}d</td><td>${num(s.avg_frequency).toFixed(1)}</td>
      <td>£${fmt(s.avg_monetary)}</td><td>£${fmt(s.total_revenue)}</td>
      <td class="action-cell">${s.action || '-'}</td>
    </tr>`;
    });
    html += '</tbody></table>';
    el.innerHTML = html;
}

// ── SQL ──
function renderSQL() {
    const queries = DATA.sql_queries;
    if (!queries || !queries.length) return;
    const tabs = document.getElementById('sqlTabs');
    tabs.innerHTML = queries.map((q, i) =>
        `<button class="sql-tab ${i === 0 ? 'active' : ''}" onclick="showSQL(${i})" id="sqlTab${i}">Q${q.id}: ${q.title}</button>`
    ).join('');
    showSQL(0);
}

function showSQL(idx) {
    const q = DATA.sql_queries[idx];
    document.querySelectorAll('.sql-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`sqlTab${idx}`).classList.add('active');

    document.getElementById('sqlCode').innerHTML = `<h4>SQL Query</h4><pre>${escapeHtml(q.sql)}</pre>`;

    let resultHtml = `<h4>Result (${q.row_count} rows)</h4>`;
    if (q.data && q.data.length) {
        resultHtml += '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
        q.columns.forEach(c => { resultHtml += `<th>${c}</th>`; });
        resultHtml += '</tr></thead><tbody>';
        q.data.forEach(row => {
            resultHtml += '<tr>';
            q.columns.forEach(c => { resultHtml += `<td>${row[c] != null ? row[c] : '-'}</td>`; });
            resultHtml += '</tr>';
        });
        resultHtml += '</tbody></table></div>';
    } else {
        resultHtml += '<p style="color:#5a6d8a">No results</p>';
    }
    document.getElementById('sqlResult').innerHTML = resultHtml;
}

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Insights ──
function renderInsights() {
    const bi = DATA.business_insights;
    if (!bi) return;

    // Strategic
    const si = document.getElementById('strategicInsights');
    si.innerHTML = (bi.strategic_insights || []).map(i => `
    <div class="insight-card">
      <div class="insight-num">INSIGHT #${i.id}</div>
      <div class="insight-cat">${i.category}</div>
      <div class="insight-text">${i.insight}</div>
      <div class="insight-rec">→ ${i.recommendation}</div>
      <div class="insight-meta">
        <span class="insight-tag tag-${i.impact?.toLowerCase()}">${i.impact} Impact</span>
        <span class="insight-tag tag-${i.priority === 'Critical' ? 'critical' : i.priority?.toLowerCase()}">${i.priority}</span>
      </div>
    </div>`).join('');

    // Revenue Opps
    const ro = document.getElementById('revenueOpps');
    ro.innerHTML = (bi.revenue_opportunities || []).map(o => `
    <div class="opp-card">
      <div class="opp-title">${o.id}. ${o.strategy}</div>
      <div class="opp-desc">${o.description}</div>
      <div class="opp-impact">${o.estimated_impact}</div>
    </div>`).join('');

    // Cost Opts
    const co = document.getElementById('costOpts');
    co.innerHTML = (bi.cost_optimizations || []).map(o => `
    <div class="opp-card">
      <div class="opp-title">${o.id}. ${o.area}</div>
      <div class="opp-desc">${o.description}</div>
    </div>`).join('');

    // Risks
    const ra = document.getElementById('riskAreas');
    ra.innerHTML = (bi.risk_areas || []).map(r => `
    <div class="risk-card">
      <span class="risk-icon">⚠</span>
      <span>${r.risk}</span>
    </div>`).join('');
}

// ── KPI Detail ──
function renderKPIDetail() {
    const ref = DATA.indicator_reference;
    if (ref) {
        document.getElementById('indicatorLegend').innerHTML = `
      <div class="legend-item">
        <h4 style="color:#34d399">Leading Indicators</h4>
        <p>${ref.leading_indicators.definition}</p>
        <p style="margin-top:4px"><strong>Examples:</strong> ${ref.leading_indicators.examples.join(', ')}</p>
      </div>
      <div class="legend-item">
        <h4 style="color:#38bdf8">Lagging Indicators</h4>
        <p>${ref.lagging_indicators.definition}</p>
        <p style="margin-top:4px"><strong>Examples:</strong> ${ref.lagging_indicators.examples.join(', ')}</p>
      </div>
      <div class="legend-item">
        <h4 style="color:#f472b6">Vanity vs Actionable</h4>
        <p><strong>Vanity:</strong> ${ref.vanity_vs_actionable.vanity}</p>
        <p><strong>Actionable:</strong> ${ref.vanity_vs_actionable.actionable}</p>
      </div>`;
    }

    const kpis = DATA.kpis;
    const grid = document.getElementById('kpiDetailGrid');
    let html = '';
    for (const [key, kpi] of Object.entries(kpis)) {
        html += `
    <div class="kpi-detail-card">
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

// ── Boot ──
document.addEventListener('DOMContentLoaded', loadData);

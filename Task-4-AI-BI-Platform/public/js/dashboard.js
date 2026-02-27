// ── Dashboard Renderer ──

function renderKPIs(kpis) {
    const grid = document.getElementById('kpiGrid');
    if (!kpis || !kpis.length) { grid.innerHTML = '<div class="loading-placeholder">No KPIs detected</div>'; return; }
    const kpiColors = { financial: '#34d399', volume: '#38bdf8', customer: '#a78bfa', dimension: '#fb923c', time: '#f472b6' };
    grid.innerHTML = kpis.map(k => {
        const c = kpiColors[k.category] || '#38bdf8';
        return `<div class="kpi-card" style="--kpi-color:${c}">
      <span class="kpi-cat">${k.category || ''}</span>
      <div class="kpi-icon">${k.icon || '📊'}</div>
      <div class="kpi-value" style="color:${c}">${k.formatted}</div>
      <div class="kpi-label">${k.label}</div>
    </div>`;
    }).join('');
}

function renderCharts(charts) {
    const container = document.getElementById('chartsContainer');
    if (!charts || !charts.length) { container.innerHTML = '<div class="loading-placeholder">No charts generated</div>'; return; }
    let html = '<div class="charts-grid">';
    charts.forEach((chart, idx) => {
        const isWide = chart.type === 'line' || (chart.data && chart.data.length > 12);
        html += `<div class="chart-card ${isWide ? 'wide' : ''}">
      <div class="chart-header"><h3>${chart.title}</h3></div>
      <div class="chart-body" id="chart_${idx}"></div>
    </div>`;
    });
    html += '</div>';
    container.innerHTML = html;
    // Render each chart
    charts.forEach((chart, idx) => {
        const el = document.getElementById(`chart_${idx}`);
        if (!el) return;
        switch (chart.type) {
            case 'horizontal_bar':
                el.innerHTML = htmlBarChart(chart.data, { horizontal: true, prefix: chart.prefix || '' });
                break;
            case 'vertical_bar':
                el.innerHTML = htmlBarChart(chart.data, { horizontal: false, prefix: chart.prefix || '' });
                break;
            case 'line':
                renderLineChart(el, chart);
                break;
            default:
                el.innerHTML = htmlBarChart(chart.data, { horizontal: chart.data.length > 8, prefix: chart.prefix || '' });
        }
    });
}

function renderLineChart(container, chart) {
    // Pure SVG line chart
    const data = chart.data || [];
    if (!data.length) { container.innerHTML = '<div class="loading-placeholder">No data</div>'; return; }
    const w = container.clientWidth || 600;
    const h = 220;
    const pad = { t: 20, r: 20, b: 40, l: 60 };
    const pw = w - pad.l - pad.r;
    const ph = h - pad.t - pad.b;
    const maxV = Math.max(...data.map(d => Number(d.value) || 0));
    const minV = Math.min(...data.map(d => Number(d.value) || 0));
    const range = maxV - minV || 1;

    const points = data.map((d, i) => ({
        x: pad.l + (i / (data.length - 1 || 1)) * pw,
        y: pad.t + ph - ((Number(d.value) - minV) / range) * ph,
        label: d.label, value: d.value
    }));

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
    const areaD = `${pathD} L${points[points.length - 1].x},${pad.t + ph} L${points[0].x},${pad.t + ph} Z`;

    let svg = `<svg width="100%" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible">`;
    // Grid
    for (let i = 0; i <= 4; i++) {
        const y = pad.t + (ph / 4) * i;
        const val = maxV - (range / 4) * i;
        svg += `<line x1="${pad.l}" y1="${y}" x2="${w - pad.r}" y2="${y}" stroke="rgba(56,189,248,0.06)" stroke-width="1"/>`;
        svg += `<text x="${pad.l - 8}" y="${y + 4}" fill="#5a6d8a" font-size="10" text-anchor="end" font-family="JetBrains Mono">${fmt(val, chart.prefix || '')}</text>`;
    }
    // Area
    svg += `<path d="${areaD}" fill="rgba(56,189,248,0.08)"/>`;
    // Line
    svg += `<path d="${pathD}" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
    // Dots
    points.forEach((p, i) => {
        svg += `<circle cx="${p.x}" cy="${p.y}" r="4" fill="#38bdf8" stroke="#0a0f1a" stroke-width="2"/>`;
        if (data.length <= 12) {
            svg += `<text x="${p.x}" y="${pad.t + ph + 16}" fill="#5a6d8a" font-size="9" text-anchor="middle" font-family="Inter">${p.label}</text>`;
        }
    });
    svg += '</svg>';
    container.innerHTML = svg;
}

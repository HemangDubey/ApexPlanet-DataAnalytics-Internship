// ── Simulation Lab UI ──

// Wire up sliders
['Price', 'Growth', 'Churn', 'Conv'].forEach(name => {
    const slider = document.getElementById(`sim${name}`);
    const display = document.getElementById(`${name.toLowerCase()}Val`);
    if (slider && display) {
        slider.addEventListener('input', () => { display.textContent = slider.value + '%'; });
    }
});

async function runSimulation() {
    const btn = document.getElementById('runSimBtn');
    btn.textContent = '⏳ Running...';
    btn.disabled = true;

    try {
        const params = {
            priceChange: Number(document.getElementById('simPrice').value),
            growthRate: Number(document.getElementById('simGrowth').value),
            churnRate: Number(document.getElementById('simChurn').value),
            conversionChange: Number(document.getElementById('simConv').value),
            months: 12,
        };

        const result = await apiPost('/api/simulate', params);
        renderSimResults(result);
    } catch (e) {
        document.getElementById('simResults').innerHTML = `<div class="sim-placeholder"><p style="color:#f87171">❌ Simulation failed: ${e.message}</p></div>`;
    } finally {
        btn.textContent = '🚀 Run Simulation';
        btn.disabled = false;
    }
}

function renderSimResults(result) {
    const el = document.getElementById('simResults');
    const impact = result.impact;
    const isPositive = impact.percentChange >= 0;

    let html = '';

    // Impact header
    html += `<div class="sim-impact">
    <div class="sim-impact-val ${isPositive ? 'positive' : 'negative'}">${isPositive ? '+' : ''}${impact.percentChange}%</div>
    <div class="sim-impact-label">${impact.summary}</div>
  </div>`;

    // Before vs After comparison
    html += `<div class="sim-comparison">
    <div class="sim-box">
      <div class="sim-box-label">Baseline (12 months)</div>
      <div class="sim-box-val" style="color:#38bdf8">$${fmt(result.baseline.total)}</div>
    </div>
    <div class="sim-box">
      <div class="sim-box-label">Projected (12 months)</div>
      <div class="sim-box-val" style="color:${isPositive ? '#34d399' : '#f87171'}">$${fmt(result.projected.total)}</div>
    </div>
  </div>`;

    // Monthly projection
    html += '<div class="sim-projection"><h4>Monthly Revenue Projection</h4>';
    const maxRev = Math.max(
        ...result.baseline.monthly.map(m => m.revenue),
        ...result.projected.monthly.map(m => m.revenue)
    );

    result.projected.monthly.forEach((m, i) => {
        const baseRev = result.baseline.monthly[i].revenue;
        const basePct = (baseRev / maxRev) * 100;
        const projPct = (m.revenue / maxRev) * 100;
        html += `<div class="sim-month-row">
      <span class="sim-month-label">M${m.month}</span>
      <div class="sim-month-bars">
        <div class="sim-bar baseline" style="width:${basePct}%"></div>
        <div class="sim-bar projected" style="width:${projPct}%"></div>
      </div>
      <span class="sim-month-val" style="color:${m.revenue >= baseRev ? '#34d399' : '#f87171'}">$${fmt(m.revenue)}</span>
    </div>`;
    });
    html += '</div>';

    // Insights
    html += '<div class="sim-insights">';
    result.insights.forEach(insight => {
        html += `<div class="sim-insight">${insight}</div>`;
    });
    html += '</div>';

    el.innerHTML = html;
}

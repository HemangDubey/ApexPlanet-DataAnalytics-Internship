// ── Business Simulation Engine ──
// Formulas:
//   Base Monthly Revenue = Total Revenue / months in data
//   Projected Revenue = BaseRevenue × PriceMultiplier × (1 + GrowthRate)^month × (1 - ChurnRate)^month × ConversionMultiplier
//   Impact % = ((Projected Total - Baseline Total) / Baseline Total) × 100

function runSimulation(params, datasetKpis) {
    const {
        priceChange = 0,       // % change: -20 to +50
        growthRate = 5,        // % monthly growth: -10 to +30
        churnRate = 3,         // % monthly churn: 0 to 15
        conversionChange = 0,  // % change in conversion: -20 to +50
        months = 12,
    } = params;

    // Find base revenue from dataset KPIs
    const revKpi = datasetKpis.find(k => k.id === 'total_revenue');
    const recKpi = datasetKpis.find(k => k.id === 'total_records');
    const custKpi = datasetKpis.find(k => k.id === 'unique_customers');

    const totalRevenue = revKpi ? revKpi.value : 10000;
    const totalOrders = recKpi ? recKpi.value : 100;
    const totalCustomers = custKpi ? custKpi.value : 50;

    // Estimate monthly baseline
    const baseMonthlyRevenue = totalRevenue / Math.max(1, Math.ceil(totalOrders / 10));
    const baseMonthlyOrders = Math.ceil(totalOrders / 6);
    const baseMonthlyCustomers = Math.ceil(totalCustomers / 6);

    const priceMult = 1 + (priceChange / 100);
    const convMult = 1 + (conversionChange / 100);
    const growthMult = growthRate / 100;
    const churnMult = churnRate / 100;

    const baseline = [];
    const projected = [];
    let baselineTotal = 0;
    let projectedTotal = 0;

    for (let m = 1; m <= months; m++) {
        // Baseline: flat with no changes
        const baseRev = baseMonthlyRevenue;
        baseline.push({
            month: m,
            label: `Month ${m}`,
            revenue: round(baseRev),
            orders: baseMonthlyOrders,
            customers: baseMonthlyCustomers,
        });
        baselineTotal += baseRev;

        // Projected: apply all multipliers
        const growthFactor = Math.pow(1 + growthMult, m - 1);
        const retentionFactor = Math.pow(1 - churnMult, m - 1);
        const projRev = baseMonthlyRevenue * priceMult * growthFactor * retentionFactor * convMult;
        const projOrders = Math.round(baseMonthlyOrders * growthFactor * retentionFactor * convMult);
        const projCustomers = Math.round(baseMonthlyCustomers * growthFactor * retentionFactor);
        projected.push({
            month: m,
            label: `Month ${m}`,
            revenue: round(projRev),
            orders: Math.max(0, projOrders),
            customers: Math.max(0, projCustomers),
        });
        projectedTotal += projRev;
    }

    const impactPct = baselineTotal > 0 ? round(((projectedTotal - baselineTotal) / baselineTotal) * 100) : 0;
    const revenueDelta = round(projectedTotal - baselineTotal);

    return {
        params: { priceChange, growthRate, churnRate, conversionChange, months },
        baseline: { monthly: baseline, total: round(baselineTotal) },
        projected: { monthly: projected, total: round(projectedTotal) },
        impact: {
            percentChange: impactPct,
            revenueDelta,
            direction: impactPct >= 0 ? 'positive' : 'negative',
            summary: `${impactPct >= 0 ? '+' : ''}${impactPct}% revenue impact ($${formatNum(revenueDelta)})`,
        },
        insights: generateSimInsights(params, impactPct, projectedTotal, baselineTotal),
    };
}

function generateSimInsights(params, impact, projected, baseline) {
    const insights = [];
    if (params.priceChange > 10) insights.push('⚠️ Price increase >10% may reduce demand elasticity');
    if (params.priceChange < -10) insights.push('💡 Aggressive pricing may boost volume but compress margins');
    if (params.churnRate > 8) insights.push('🔴 High churn rate — invest in retention programs');
    if (params.growthRate > 15) insights.push('🚀 High growth target — ensure supply chain can scale');
    if (impact > 50) insights.push('✅ Strong positive trajectory — consider reinvesting profits');
    if (impact < -20) insights.push('⚠️ Significant revenue decline projected — review strategy');
    if (params.conversionChange > 20) insights.push('📈 Conversion improvement of >20% requires significant funnel optimization');
    if (insights.length === 0) insights.push('📊 Moderate scenario — projections within normal variance');
    return insights;
}

function round(v) { return Math.round(v * 100) / 100; }
function formatNum(v) {
    if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(1) + 'K';
    return v.toFixed(2);
}

module.exports = { runSimulation };

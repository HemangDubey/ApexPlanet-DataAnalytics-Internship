// ── Chart Engine: Auto-map columns to chart types ──

function generateCharts(data, schema) {
    const charts = [];
    const numCols = Object.entries(schema).filter(([_, v]) => v.type === 'numerical');
    const catCols = Object.entries(schema).filter(([_, v]) => v.type === 'categorical');
    const dateCols = Object.entries(schema).filter(([_, v]) => v.type === 'datetime');

    const revenueCol = findCol(numCols, ['revenue', 'total', 'amount', 'sales', 'value', 'income', 'price']);
    const qtyCol = findCol(numCols, ['quantity', 'qty', 'units', 'count']);

    // 1. Categorical breakdown (top categories by revenue)
    catCols.forEach(([col, meta]) => {
        if (meta.uniqueCount <= 30 && revenueCol) {
            const agg = aggregateBy(data, col, revenueCol);
            charts.push({
                id: `bar_${col}`, type: 'horizontal_bar', title: `${formatLabel(revenueCol)} by ${formatLabel(col)}`,
                data: agg.slice(0, 12), xLabel: formatLabel(revenueCol), yLabel: formatLabel(col), prefix: '$'
            });
        }
    });

    // 2. Time series (if date column + numeric column exist)
    if (dateCols.length > 0 && revenueCol) {
        const dateCol = dateCols[0][0];
        const timeSeries = buildTimeSeries(data, dateCol, revenueCol);
        if (timeSeries.length > 1) {
            charts.push({
                id: `trend_${revenueCol}`, type: 'line', title: `${formatLabel(revenueCol)} Over Time`,
                data: timeSeries, xLabel: 'Period', yLabel: formatLabel(revenueCol), prefix: '$'
            });
        }
    }

    // 3. Distribution of numeric columns
    numCols.slice(0, 3).forEach(([col, meta]) => {
        if (meta.stats && meta.stats.count > 5) {
            const dist = buildDistribution(data, col);
            charts.push({
                id: `dist_${col}`, type: 'vertical_bar', title: `${formatLabel(col)} Distribution`,
                data: dist, xLabel: formatLabel(col), yLabel: 'Count', prefix: ''
            });
        }
    });

    // 4. Top N items (if product/item column exists)
    const itemCol = findCol(catCols, ['product', 'item', 'name', 'sku', 'description']);
    if (itemCol && revenueCol) {
        const agg = aggregateBy(data, itemCol, revenueCol);
        charts.push({
            id: `top_items`, type: 'horizontal_bar', title: `Top Products by ${formatLabel(revenueCol)}`,
            data: agg.slice(0, 15), xLabel: formatLabel(revenueCol), yLabel: formatLabel(itemCol), prefix: '$'
        });
    }

    return charts;
}

function findCol(cols, keywords) {
    for (const kw of keywords) {
        const match = cols.find(([name]) => name.toLowerCase().includes(kw));
        if (match) return match[0];
    }
    return null;
}

function aggregateBy(data, groupCol, valueCol) {
    const agg = {};
    data.forEach(r => {
        const key = String(r[groupCol] || 'Unknown');
        agg[key] = (agg[key] || 0) + (Number(r[valueCol]) || 0);
    });
    return Object.entries(agg)
        .map(([label, value]) => ({ label, value: Math.round(value * 100) / 100 }))
        .sort((a, b) => b.value - a.value);
}

function buildTimeSeries(data, dateCol, valueCol) {
    const monthly = {};
    data.forEach(r => {
        const d = new Date(r[dateCol]);
        if (isNaN(d)) return;
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        monthly[key] = (monthly[key] || 0) + (Number(r[valueCol]) || 0);
    });
    return Object.entries(monthly)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([label, value]) => ({ label, value: Math.round(value * 100) / 100 }));
}

function buildDistribution(data, col) {
    const vals = data.map(r => Number(r[col])).filter(v => !isNaN(v));
    if (vals.length < 5) return [];
    vals.sort((a, b) => a - b);
    const min = vals[0], max = vals[vals.length - 1];
    const range = max - min;
    if (range === 0) return [{ label: String(min), value: vals.length }];
    const bins = Math.min(15, Math.max(5, Math.ceil(Math.sqrt(vals.length))));
    const binWidth = range / bins;
    const histogram = Array(bins).fill(0);
    const labels = [];
    for (let i = 0; i < bins; i++) {
        const lo = min + i * binWidth;
        const hi = lo + binWidth;
        labels.push(`${Math.round(lo)}-${Math.round(hi)}`);
    }
    vals.forEach(v => {
        let idx = Math.floor((v - min) / binWidth);
        if (idx >= bins) idx = bins - 1;
        histogram[idx]++;
    });
    return labels.map((label, i) => ({ label, value: histogram[i] }));
}

function formatLabel(col) {
    return col.replace(/([A-Z])/g, ' $1').replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim();
}

module.exports = { generateCharts };

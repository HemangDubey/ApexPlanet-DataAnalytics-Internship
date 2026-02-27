// ── KPI Engine: Auto-detect and calculate KPIs from schema ──

function generateKPIs(data, schema) {
    const kpis = [];
    const numCols = Object.entries(schema).filter(([_, v]) => v.type === 'numerical');
    const catCols = Object.entries(schema).filter(([_, v]) => v.type === 'categorical');
    const dateCols = Object.entries(schema).filter(([_, v]) => v.type === 'datetime');

    // 1. Row count
    kpis.push({ id: 'total_records', label: 'Total Records', value: data.length, formatted: data.length.toLocaleString(), icon: '📊', category: 'volume' });

    // 2. Auto-detect revenue/amount/total column
    const revenueCol = findColumn(numCols, ['revenue', 'total', 'amount', 'sales', 'price', 'value', 'income']);
    if (revenueCol) {
        const stats = schema[revenueCol].stats;
        kpis.push({ id: 'total_revenue', label: `Total ${formatLabel(revenueCol)}`, value: stats.sum, formatted: formatCurrency(stats.sum), icon: '💰', category: 'financial' });
        kpis.push({ id: 'avg_revenue', label: `Avg ${formatLabel(revenueCol)}`, value: stats.mean, formatted: formatCurrency(stats.mean), icon: '📈', category: 'financial' });
        kpis.push({ id: 'max_revenue', label: `Max ${formatLabel(revenueCol)}`, value: stats.max, formatted: formatCurrency(stats.max), icon: '🏆', category: 'financial' });
    }

    // 3. Auto-detect quantity column
    const qtyCol = findColumn(numCols, ['quantity', 'qty', 'units', 'count', 'items', 'volume']);
    if (qtyCol) {
        const stats = schema[qtyCol].stats;
        kpis.push({ id: 'total_quantity', label: `Total ${formatLabel(qtyCol)}`, value: stats.sum, formatted: stats.sum.toLocaleString(), icon: '📦', category: 'volume' });
        kpis.push({ id: 'avg_quantity', label: `Avg ${formatLabel(qtyCol)}`, value: stats.mean, formatted: stats.mean.toFixed(1), icon: '📉', category: 'volume' });
    }

    // 4. Unique customers/IDs
    const idCol = findColumn(catCols, ['customer', 'user', 'client', 'account', 'member', 'id']);
    if (idCol) {
        kpis.push({ id: 'unique_customers', label: `Unique ${formatLabel(idCol)}s`, value: schema[idCol].uniqueCount, formatted: schema[idCol].uniqueCount.toLocaleString(), icon: '👥', category: 'customer' });
    }

    // 5. Unique categories
    const catCol = findColumn(catCols, ['category', 'type', 'segment', 'group', 'class', 'department']);
    if (catCol) {
        kpis.push({ id: 'categories', label: `${formatLabel(catCol)}`, value: schema[catCol].uniqueCount, formatted: schema[catCol].uniqueCount.toLocaleString(), icon: '🏷️', category: 'dimension' });
    }

    // 6. Countries/regions
    const geoCol = findColumn(catCols, ['country', 'region', 'state', 'city', 'location', 'area']);
    if (geoCol) {
        kpis.push({ id: 'regions', label: `${formatLabel(geoCol)}`, value: schema[geoCol].uniqueCount, formatted: schema[geoCol].uniqueCount.toLocaleString(), icon: '🌍', category: 'dimension' });
    }

    // 7. AOV if both revenue and customer exist
    if (revenueCol && idCol) {
        const aov = schema[revenueCol].stats.sum / schema[idCol].uniqueCount;
        kpis.push({ id: 'aov', label: 'Avg per Customer', value: Math.round(aov * 100) / 100, formatted: formatCurrency(aov), icon: '🎯', category: 'financial' });
    }

    // 8. Date range
    if (dateCols.length > 0) {
        const dateField = dateCols[0][0];
        const dates = data.map(r => new Date(r[dateField])).filter(d => !isNaN(d));
        if (dates.length) {
            const min = new Date(Math.min(...dates));
            const max = new Date(Math.max(...dates));
            kpis.push({ id: 'date_range', label: 'Data Period', value: `${min.toLocaleDateString()} - ${max.toLocaleDateString()}`, formatted: `${min.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' })} — ${max.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' })}`, icon: '📅', category: 'time' });
        }
    }

    return kpis;
}

function findColumn(cols, keywords) {
    for (const kw of keywords) {
        const match = cols.find(([name]) => name.toLowerCase().includes(kw));
        if (match) return match[0];
    }
    return null;
}

function formatLabel(col) {
    return col.replace(/([A-Z])/g, ' $1').replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim();
}

function formatCurrency(v) {
    if (v == null) return '-';
    if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K';
    return '$' + v.toFixed(2);
}

module.exports = { generateKPIs };

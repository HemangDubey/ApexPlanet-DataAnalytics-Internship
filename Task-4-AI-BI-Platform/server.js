// ── GravityBI Platform — Express Server ──
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { parseCSV, detectSchema, validateCSV } = require('./services/csvEngine');
const { generateKPIs } = require('./services/kpiEngine');
const { saveDataset, getActiveDataset } = require('./db/database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.use('/api/data', require('./routes/data'));
app.use('/api/simulate', require('./routes/simulation'));
app.use('/api/ai', require('./routes/ai'));

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', version: '1.0.0', timestamp: new Date().toISOString() });
});

// Load default dataset if none exists
function loadDefaultDataset() {
    const active = getActiveDataset();
    if (active) {
        console.log(`  Active dataset: ${active.name} (${active.row_count} rows)`);
        return;
    }
    const csvPath = path.join(__dirname, 'data', 'default_retail.csv');
    try {
        const { data, fields } = parseCSV(csvPath, true);
        const validation = validateCSV(data, fields);
        if (!validation.valid) {
            console.error('  Default dataset validation failed:', validation.issues);
            return;
        }
        const schema = detectSchema(data, fields);
        const kpis = generateKPIs(data, schema);
        saveDataset({
            name: 'Default Retail Dataset',
            filename: 'default_retail.csv',
            row_count: data.length,
            col_count: fields.length,
            schema_info: schema,
            kpis,
            raw_data: data,
        });
        console.log(`  Loaded default dataset: ${data.length} rows, ${fields.length} columns`);
    } catch (e) {
        console.error('  Failed to load default dataset:', e.message);
    }
}

// SPA fallback
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start
app.listen(PORT, () => {
    console.log('\n  ╔══════════════════════════════════════════╗');
    console.log('  ║   GravityBI Platform — AI-Powered BI     ║');
    console.log('  ╠══════════════════════════════════════════╣');
    console.log(`  ║   🌐  http://localhost:${PORT}              ║`);
    console.log('  ║   📊  Dynamic CSV Engine    ✓            ║');
    console.log('  ║   🧪  Business Simulation   ✓            ║');
    console.log('  ║   🤖  H.O.N.E.Y AI         ✓            ║');
    console.log('  ╚══════════════════════════════════════════╝\n');
    loadDefaultDataset();
});

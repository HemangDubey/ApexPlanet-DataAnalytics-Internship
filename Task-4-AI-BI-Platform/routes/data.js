// ── Data Routes: CSV Upload, KPI, Charts ──
const express = require('express');
const multer = require('multer');
const path = require('path');
const router = express.Router();
const { parseCSV, detectSchema, validateCSV } = require('../services/csvEngine');
const { generateKPIs } = require('../services/kpiEngine');
const { generateCharts } = require('../services/chartEngine');
const { saveDataset, getActiveDataset, getDatasetList, setActiveDataset } = require('../db/database');

// Multer config
const storage = multer.diskStorage({
    destination: path.join(__dirname, '..', 'uploads'),
    filename: (req, file, cb) => cb(null, `${Date.now()}_${file.originalname}`),
});
const upload = multer({
    storage,
    limits: { fileSize: (process.env.MAX_FILE_SIZE_MB || 10) * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) cb(null, true);
        else cb(new Error('Only CSV files allowed'));
    },
});

// GET /api/data/summary — current dataset KPIs + metadata
router.get('/summary', (req, res) => {
    try {
        const ds = getActiveDataset();
        if (!ds) return res.status(404).json({ error: 'No dataset loaded' });
        res.json({
            id: ds.id, name: ds.name, filename: ds.filename,
            row_count: ds.row_count, col_count: ds.col_count,
            schema: ds.schema_info, kpis: ds.kpis, created_at: ds.created_at,
        });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET /api/data/charts — auto-mapped charts
router.get('/charts', (req, res) => {
    try {
        const ds = getActiveDataset();
        if (!ds) return res.status(404).json({ error: 'No dataset loaded' });
        const charts = generateCharts(ds.raw_data, ds.schema_info);
        res.json({ charts });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET /api/data/columns — column metadata
router.get('/columns', (req, res) => {
    try {
        const ds = getActiveDataset();
        if (!ds) return res.status(404).json({ error: 'No dataset loaded' });
        res.json({ columns: ds.schema_info });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET /api/data/datasets — list all datasets
router.get('/datasets', (req, res) => {
    try { res.json({ datasets: getDatasetList() }); }
    catch (e) { res.status(500).json({ error: e.message }); }
});

// POST /api/data/upload — upload new CSV
router.post('/upload', upload.single('file'), (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
        const { data, fields } = parseCSV(req.file.path, true);
        const validation = validateCSV(data, fields);
        if (!validation.valid) return res.status(400).json({ error: 'Validation failed', issues: validation.issues });

        const schema = detectSchema(data, fields);
        const kpis = generateKPIs(data, schema);
        const id = saveDataset({
            name: req.file.originalname.replace('.csv', ''),
            filename: req.file.filename,
            row_count: data.length,
            col_count: fields.length,
            schema_info: schema,
            kpis: kpis,
            raw_data: data,
        });

        const charts = generateCharts(data, schema);
        res.json({ success: true, id, name: req.file.originalname, row_count: data.length, col_count: fields.length, kpis, charts, schema });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// POST /api/data/switch — switch active dataset
router.post('/switch', (req, res) => {
    try {
        const { id } = req.body;
        if (!id) return res.status(400).json({ error: 'Dataset ID required' });
        setActiveDataset(id);
        res.json({ success: true });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;

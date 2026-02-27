// ── Simulation Routes ──
const express = require('express');
const router = express.Router();
const { runSimulation } = require('../services/simEngine');
const { getActiveDataset } = require('../db/database');

// POST /api/simulate
router.post('/', (req, res) => {
    try {
        const ds = getActiveDataset();
        if (!ds) return res.status(404).json({ error: 'No dataset loaded' });
        const params = {
            priceChange: clamp(Number(req.body.priceChange) || 0, -50, 100),
            growthRate: clamp(Number(req.body.growthRate) || 5, -20, 50),
            churnRate: clamp(Number(req.body.churnRate) || 3, 0, 30),
            conversionChange: clamp(Number(req.body.conversionChange) || 0, -50, 100),
            months: clamp(Number(req.body.months) || 12, 3, 36),
        };
        const result = runSimulation(params, ds.kpis);
        res.json(result);
    } catch (e) { res.status(500).json({ error: e.message }); }
});

function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

module.exports = router;

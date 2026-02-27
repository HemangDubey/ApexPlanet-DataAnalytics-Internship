// ── AI Routes: H.O.N.E.Y Chatbot ──
const express = require('express');
const rateLimit = require('express-rate-limit');
const router = express.Router();
const aiService = require('../services/aiService');
const { getActiveDataset, saveChatMessage, getChatHistory } = require('../db/database');

// Rate limiting for AI endpoint
const aiLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: Number(process.env.AI_RATE_LIMIT) || 30,
    message: { error: 'Too many AI requests. Please wait a moment.' },
});

// POST /api/ai/chat
router.post('/chat', aiLimiter, async (req, res) => {
    try {
        const { message } = req.body;
        if (!message || typeof message !== 'string' || message.trim().length === 0) {
            return res.status(400).json({ error: 'Message is required' });
        }
        if (message.length > 2000) {
            return res.status(400).json({ error: 'Message too long (max 2000 chars)' });
        }

        const ds = getActiveDataset();
        const datasetId = ds ? ds.id : null;
        const history = datasetId ? getChatHistory(datasetId, 10) : [];

        // Save user message
        if (datasetId) saveChatMessage(datasetId, 'user', message.trim());

        // Get AI response
        const result = await aiService.chat(message.trim(), ds, history);

        // Save assistant response
        if (datasetId && result.success) saveChatMessage(datasetId, 'assistant', result.response);

        res.json({
            response: result.response,
            success: result.success,
            usage: result.usage || null,
        });
    } catch (e) {
        console.error('AI Route Error:', e);
        res.status(500).json({ error: 'AI service error', detail: e.message });
    }
});

// GET /api/ai/history
router.get('/history', (req, res) => {
    try {
        const ds = getActiveDataset();
        if (!ds) return res.json({ history: [] });
        const history = getChatHistory(ds.id, 50);
        res.json({ history });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;

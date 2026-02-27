// ── GravityBI Server — serves dashboard + AI proxy on port 8765 ──
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const Groq = require('groq-sdk');

const app = express();
const PORT = process.env.PORT || 8765;

app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, 'Task_3_Output')));

// ── Simulation Endpoint ──
app.post('/api/simulate', (req, res) => {
    try {
        const { priceChange = 0, growthRate = 5, churnRate = 3, conversionChange = 0, months = 12, baseRevenue = 0 } = req.body;
        const base = Number(baseRevenue) || 10000;
        const monthlyBase = base / 6;
        const pM = 1 + (Number(priceChange) / 100), gM = Number(growthRate) / 100, cM = Number(churnRate) / 100, cvM = 1 + (Number(conversionChange) / 100);
        const baseline = [], projected = [];
        let bTotal = 0, pTotal = 0;
        for (let m = 1; m <= Number(months); m++) {
            const bRev = monthlyBase;
            baseline.push({ month: m, revenue: Math.round(bRev * 100) / 100 });
            bTotal += bRev;
            const pRev = monthlyBase * pM * Math.pow(1 + gM, m - 1) * Math.pow(1 - cM, m - 1) * cvM;
            projected.push({ month: m, revenue: Math.round(pRev * 100) / 100 });
            pTotal += pRev;
        }
        const impact = bTotal > 0 ? Math.round(((pTotal - bTotal) / bTotal) * 100 * 100) / 100 : 0;
        const insights = [];
        if (Number(priceChange) > 10) insights.push('⚠️ Price increase >10% may reduce demand elasticity');
        if (Number(priceChange) < -10) insights.push('💡 Aggressive pricing may boost volume but compress margins');
        if (Number(churnRate) > 8) insights.push('🔴 High churn rate — invest in retention programs');
        if (Number(growthRate) > 15) insights.push('🚀 High growth target — ensure supply chain scales');
        if (impact > 50) insights.push('✅ Strong positive trajectory — reinvest profits');
        if (impact < -20) insights.push('⚠️ Significant revenue decline — review strategy');
        if (!insights.length) insights.push('📊 Moderate scenario — within normal variance');
        res.json({
            baseline: { monthly: baseline, total: Math.round(bTotal * 100) / 100 },
            projected: { monthly: projected, total: Math.round(pTotal * 100) / 100 },
            impact: { percentChange: impact, delta: Math.round((pTotal - bTotal) * 100) / 100, direction: impact >= 0 ? 'positive' : 'negative' },
            insights
        });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// ── H.O.N.E.Y AI Endpoint ──
const aiLimiter = rateLimit({ windowMs: 60000, max: 30, message: { error: 'Rate limited. Wait a moment.' } });
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

app.post('/api/ai/chat', aiLimiter, async (req, res) => {
    try {
        const { message, context } = req.body;
        if (!message || message.length > 2000) return res.status(400).json({ error: 'Invalid message' });
        const completion = await groq.chat.completions.create({
            model: 'llama-3.3-70b-versatile',
            messages: [
                { role: 'system', content: `You are H.O.N.E.Y (Holistic Operational Neural Enterprise Yield), an elite AI Business Intelligence assistant for a retail analytics dashboard.\n\nCapabilities: Explain KPIs, generate SQL, analyze simulations, provide business insights.\nRules: Be concise (max 3-4 paragraphs), use bullets, relate to user's data, use emoji sparingly.\n\n${context || ''}` },
                { role: 'user', content: message }
            ],
            temperature: 0.7, max_tokens: 1024, top_p: 0.9,
        });
        res.json({ success: true, response: completion.choices[0]?.message?.content || 'No response.', usage: completion.usage });
    } catch (e) {
        console.error('AI Error:', e.message);
        res.json({ success: false, response: `AI temporarily unavailable: ${e.message}` });
    }
});

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => {
    console.log(`\n  ╔═════════════════════════════════════════════╗`);
    console.log(`  ║  GravityBI Dashboard — http://localhost:${PORT}  ║`);
    console.log(`  ║  📊 Analytics  🧪 Simulation  🍯 H.O.N.E.Y   ║`);
    console.log(`  ╚═════════════════════════════════════════════╝\n`);
});

// ── H.O.N.E.Y AI Service (Groq API) ──
// Holistic Operational Neural Enterprise Yield
const Groq = require('groq-sdk');

let groqClient = null;

function getClient() {
    if (!groqClient) {
        groqClient = new Groq({ apiKey: process.env.GROQ_API_KEY });
    }
    return groqClient;
}

const SYSTEM_PROMPT = `You are H.O.N.E.Y (Holistic Operational Neural Enterprise Yield), an elite AI Business Intelligence assistant embedded in the GravityBI dashboard platform.

Your capabilities:
1. EXPLAIN KPIs and business metrics in plain language
2. GENERATE SQL queries for data analysis
3. ANALYZE simulation results and provide strategic recommendations
4. PROVIDE business insights based on dataset characteristics

Rules:
- Be concise and actionable (max 3-4 paragraphs)
- Use bullet points for lists
- When showing SQL, use standard SQL syntax
- Always relate answers to the user's actual dataset context
- Use emoji sparingly for visual clarity
- If asked about data you don't have, say so honestly
- Format numbers with currency symbols and commas`;

function buildContext(dataset) {
    if (!dataset) return 'No dataset is currently loaded.';

    const schema = dataset.schema_info || {};
    const kpis = dataset.kpis || [];
    const columns = Object.entries(schema).map(([name, info]) =>
        `${name} (${info.type}${info.type === 'categorical' ? `, ${info.uniqueCount} unique` : ''}${info.type === 'numerical' ? `, range: ${info.stats?.min}-${info.stats?.max}` : ''})`
    ).join(', ');

    const kpiSummary = kpis.map(k => `${k.label}: ${k.formatted}`).join(' | ');

    return `DATASET CONTEXT:
- Name: ${dataset.name}
- Rows: ${dataset.row_count} | Columns: ${dataset.col_count}
- Schema: ${columns}
- KPIs: ${kpiSummary}`;
}

async function chat(userMessage, dataset, history = []) {
    const client = getClient();
    const context = buildContext(dataset);

    const messages = [
        { role: 'system', content: `${SYSTEM_PROMPT}\n\n${context}` },
        ...history.slice(-6).map(h => ({ role: h.role, content: h.content })),
        { role: 'user', content: userMessage },
    ];

    try {
        const completion = await client.chat.completions.create({
            model: 'llama-3.3-70b-versatile',
            messages,
            temperature: 0.7,
            max_tokens: 1024,
            top_p: 0.9,
        });
        return {
            success: true,
            response: completion.choices[0]?.message?.content || 'No response generated.',
            usage: completion.usage,
        };
    } catch (error) {
        console.error('Groq API Error:', error.message);
        return {
            success: false,
            response: `AI service temporarily unavailable: ${error.message}`,
            error: error.message,
        };
    }
}

module.exports = { chat };

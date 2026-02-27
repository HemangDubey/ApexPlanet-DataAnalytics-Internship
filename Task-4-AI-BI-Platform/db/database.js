// ── SQLite Database Layer ──
const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = path.join(__dirname, '..', 'gravity_bi.db');
let db;

function getDb() {
    if (!db) {
        db = new Database(DB_PATH);
        db.pragma('journal_mode = WAL');
        db.pragma('foreign_keys = ON');
        initSchema();
    }
    return db;
}

function initSchema() {
    db.exec(`
    CREATE TABLE IF NOT EXISTS datasets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      filename TEXT,
      row_count INTEGER DEFAULT 0,
      col_count INTEGER DEFAULT 0,
      schema_info TEXT DEFAULT '{}',
      kpis TEXT DEFAULT '{}',
      raw_data TEXT DEFAULT '[]',
      is_active INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS chat_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      dataset_id INTEGER,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    );
  `);
}

// ── Dataset CRUD ──
function saveDataset(data) {
    const stmt = getDb().prepare(`
    INSERT INTO datasets (name, filename, row_count, col_count, schema_info, kpis, raw_data, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
  `);
    // Deactivate all existing
    getDb().prepare('UPDATE datasets SET is_active = 0').run();
    const result = stmt.run(
        data.name, data.filename || null, data.row_count, data.col_count,
        JSON.stringify(data.schema_info), JSON.stringify(data.kpis),
        JSON.stringify(data.raw_data)
    );
    return result.lastInsertRowid;
}

function getActiveDataset() {
    const row = getDb().prepare('SELECT * FROM datasets WHERE is_active = 1 ORDER BY id DESC LIMIT 1').get();
    if (!row) return null;
    return {
        ...row,
        schema_info: JSON.parse(row.schema_info || '{}'),
        kpis: JSON.parse(row.kpis || '{}'),
        raw_data: JSON.parse(row.raw_data || '[]'),
    };
}

function getDatasetList() {
    return getDb().prepare('SELECT id, name, filename, row_count, col_count, is_active, created_at FROM datasets ORDER BY id DESC').all();
}

function setActiveDataset(id) {
    getDb().prepare('UPDATE datasets SET is_active = 0').run();
    getDb().prepare('UPDATE datasets SET is_active = 1 WHERE id = ?').run(id);
}

// ── Chat History ──
function saveChatMessage(datasetId, role, content) {
    getDb().prepare('INSERT INTO chat_history (dataset_id, role, content) VALUES (?, ?, ?)').run(datasetId, role, content);
}

function getChatHistory(datasetId, limit = 20) {
    return getDb().prepare('SELECT role, content, created_at FROM chat_history WHERE dataset_id = ? ORDER BY id DESC LIMIT ?').all(datasetId, limit).reverse();
}

module.exports = { getDb, saveDataset, getActiveDataset, getDatasetList, setActiveDataset, saveChatMessage, getChatHistory };

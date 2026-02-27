// ── CSV Engine: Parse, Detect Schema, Validate ──
const fs = require('fs');
const Papa = require('papaparse');

/**
 * Parse a CSV file or string and return structured data
 */
function parseCSV(input, isFilePath = false) {
    const csvString = isFilePath ? fs.readFileSync(input, 'utf-8') : input;
    const result = Papa.parse(csvString, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        transformHeader: h => h.trim(),
    });
    if (result.errors.length > 0) {
        const critical = result.errors.filter(e => e.type === 'Delimiter' || e.type === 'FieldMismatch');
        if (critical.length > 0) throw new Error(`CSV Parse Error: ${critical[0].message}`);
    }
    return { data: result.data, fields: result.meta.fields, errors: result.errors };
}

/**
 * Detect column types: numerical, categorical, datetime
 */
function detectSchema(data, fields) {
    const schema = {};
    fields.forEach(field => {
        const values = data.map(r => r[field]).filter(v => v != null && v !== '');
        const sample = values.slice(0, 50);
        // Datetime detection
        if (isDateColumn(sample, field)) {
            schema[field] = { type: 'datetime', sample: sample.slice(0, 5).map(String), nonNull: values.length };
        }
        // Numerical detection
        else if (isNumerical(sample)) {
            const nums = values.map(Number).filter(n => !isNaN(n));
            schema[field] = {
                type: 'numerical',
                sample: nums.slice(0, 5),
                nonNull: values.length,
                stats: calcStats(nums),
            };
        }
        // Categorical
        else {
            const unique = [...new Set(values.map(String))];
            schema[field] = {
                type: 'categorical',
                sample: unique.slice(0, 10),
                nonNull: values.length,
                uniqueCount: unique.length,
                topValues: getTopValues(values),
            };
        }
    });
    return schema;
}

function isDateColumn(sample, name) {
    const dateNames = ['date', 'time', 'created', 'updated', 'timestamp', 'day', 'month', 'year', 'invoicedate'];
    if (dateNames.some(n => name.toLowerCase().includes(n))) return true;
    const dateCount = sample.filter(v => {
        if (typeof v !== 'string') return false;
        const d = new Date(v);
        return !isNaN(d.getTime()) && v.length > 5;
    }).length;
    return dateCount / sample.length > 0.7;
}

function isNumerical(sample) {
    const numCount = sample.filter(v => typeof v === 'number' || (!isNaN(Number(v)) && v !== '' && v !== null)).length;
    return numCount / sample.length > 0.8;
}

function calcStats(nums) {
    if (!nums.length) return {};
    nums.sort((a, b) => a - b);
    const sum = nums.reduce((a, b) => a + b, 0);
    const mean = sum / nums.length;
    const variance = nums.reduce((a, b) => a + (b - mean) ** 2, 0) / nums.length;
    return {
        min: nums[0],
        max: nums[nums.length - 1],
        mean: Math.round(mean * 100) / 100,
        median: nums[Math.floor(nums.length / 2)],
        sum: Math.round(sum * 100) / 100,
        std: Math.round(Math.sqrt(variance) * 100) / 100,
        count: nums.length,
    };
}

function getTopValues(values) {
    const freq = {};
    values.forEach(v => { freq[v] = (freq[v] || 0) + 1; });
    return Object.entries(freq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([value, count]) => ({ value, count }));
}

/**
 * Validate dataset
 */
function validateCSV(data, fields) {
    const issues = [];
    if (data.length === 0) issues.push('Dataset is empty');
    if (data.length > 100000) issues.push('Dataset exceeds 100K row limit');
    if (fields.length === 0) issues.push('No columns detected');
    if (fields.length > 50) issues.push('Too many columns (max 50)');
    const dupes = fields.filter((f, i) => fields.indexOf(f) !== i);
    if (dupes.length) issues.push(`Duplicate columns: ${dupes.join(', ')}`);
    return { valid: issues.length === 0, issues };
}

module.exports = { parseCSV, detectSchema, validateCSV };

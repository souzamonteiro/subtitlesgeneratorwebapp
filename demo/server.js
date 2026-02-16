// server.js - Fixed version
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const tar = require('tar');

const app = express();
const PORT = process.env.PORT || 8080;

// Enable CORS
app.use(cors());

// Add cross-origin isolation headers so SharedArrayBuffer is available to workers
app.use((req, res, next) => {
    res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
    res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
    // ensure wasm served with correct mime-type
    if (req.path.endsWith('.wasm')) {
        res.setHeader('Content-Type', 'application/wasm');
    }
    next();
});

// Serve static files
app.use(express.static(__dirname));

// avoid favicon 404 noise
app.get('/favicon.ico', (req, res) => res.sendStatus(204));

// Serve Vosk models as tar.gz files
app.get('/vosk-model-small-en-us-0.15.tar.gz', (req, res) => {
    const modelPath = path.join(__dirname, 'vosk-model-small-en-us-0.15');
    
    if (!fs.existsSync(modelPath)) {
        return res.status(404).json({ error: 'English model not found' });
    }
    
    console.log(`Serving English model from: ${modelPath}`);
    
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', 'attachment; filename="vosk-model-small-en-us-0.15.tar.gz"');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    tar.create(
        {
            gzip: true,
            cwd: modelPath
        },
        fs.readdirSync(modelPath)
    ).pipe(res);
});

app.get('/vosk-model-small-pt-0.3.tar.gz', (req, res) => {
    const modelPath = path.join(__dirname, 'vosk-model-small-pt-0.3');
    
    if (!fs.existsSync(modelPath)) {
        return res.status(404).json({ error: 'Portuguese model not found' });
    }
    
    console.log(`Serving Portuguese model from: ${modelPath}`);
    
    res.setHeader('Content-Type', 'application/gzip');
    res.setHeader('Content-Disposition', 'attachment; filename="vosk-model-small-pt-0.3.tar.gz"');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    tar.create(
        {
            gzip: true,
            cwd: modelPath
        },
        fs.readdirSync(modelPath)
    ).pipe(res);
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`Server running at: http://localhost:${PORT}`);
});


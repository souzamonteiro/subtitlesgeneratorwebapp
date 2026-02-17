const http = require('http');
const fs = require('fs');
const path = require('path');
const { contentType } = require('mime-types');

const PORT = Number(process.env.PORT) || 8080;
const ROOT = path.join(__dirname, 'www');

function send(res, statusCode, body, headers = {}) {
    res.writeHead(statusCode, headers);
    res.end(body);
}

function safeResolve(urlPath) {
    const decoded = decodeURIComponent(urlPath);
    const clean = decoded.replace(/^\/+/, '');
    const resolved = path.resolve(ROOT, clean);
    if (!resolved.startsWith(ROOT)) {
        return null;
    }
    return resolved;
}

const server = http.createServer((req, res) => {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
        return send(res, 405, 'Method Not Allowed', { 'Content-Type': 'text/plain' });
    }

    const urlPath = (req.url || '/').split('?')[0];
    let filePath;
    try {
        filePath = safeResolve(urlPath);
    } catch (err) {
        return send(res, 400, 'Bad Request', { 'Content-Type': 'text/plain' });
    }

    if (!filePath) {
        return send(res, 403, 'Forbidden', { 'Content-Type': 'text/plain' });
    }

    fs.stat(filePath, (err, stat) => {
        if (err) {
            return send(res, 404, 'Not Found', { 'Content-Type': 'text/plain' });
        }

        if (stat.isDirectory()) {
            const indexPath = path.join(filePath, 'index.html');
            return fs.stat(indexPath, (idxErr, idxStat) => {
                if (idxErr || !idxStat.isFile()) {
                    return send(res, 404, 'Not Found', { 'Content-Type': 'text/plain' });
                }
                return streamFile(indexPath, idxStat, req, res);
            });
        }

        if (!stat.isFile()) {
            return send(res, 404, 'Not Found', { 'Content-Type': 'text/plain' });
        }

        return streamFile(filePath, stat, req, res);
    });
});

function streamFile(filePath, stat, req, res) {
    console.log(`Serving: ${filePath}`);
    
    const type = contentType(path.basename(filePath)) || 'application/octet-stream';
    const headers = {
        'Content-Type': type,
        'Content-Length': stat.size,
        'Access-Control-Allow-Origin': '*',
        'Cross-Origin-Opener-Policy': 'same-origin',
        'Cross-Origin-Embedder-Policy': 'require-corp',
        'Cross-Origin-Resource-Policy': 'cross-origin'
    };

    if (req.method === 'HEAD') {
        return send(res, 200, null, headers);
    }

    res.writeHead(200, headers);
    fs.createReadStream(filePath).pipe(res);
}

server.listen(PORT, () => {
    console.log(`HTTP server running at: http://localhost:${PORT}`);
    console.log(`Serving directory: ${ROOT}`);
});
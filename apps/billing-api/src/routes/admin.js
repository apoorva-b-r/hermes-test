const express = require('express');
const router = express.Router();

function requireAuth(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (authHeader !== 'Bearer demo-metrics-token') {
    return res.status(401).json({ error: 'unauthorized' });
  }
  next();
}

router.post('/admin/export', (req, res) => {
  res.status(202).json({ queued: true });
});

router.all('/admin/export', (req, res) => {
  res.status(405).json({ error: 'method not allowed' });
});

router.get('/internal/metrics', requireAuth, (req, res) => {
  res.status(200).json({ requests: 1234 });
});

router.get('/health', (req, res) => {
  res.status(200).json({ ok: true });
});

module.exports = router;


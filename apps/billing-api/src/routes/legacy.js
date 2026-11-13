const express = require('express');
const router = express.Router();

router.get('/v1/invoices', (req, res) => {
  res.status(200).json([
    { invoice_id: 4812, amount: 129.5 }
  ]);
});

/** @deprecated Use GET /v2/invoices. Removed for all clients on 2026-03-31. */
router.get('/v1/orders', (req, res) => {
  res.set('Deprecation', 'true');
  res.status(410).json({ error: 'gone', use: '/v2/invoices' });
});

module.exports = router;


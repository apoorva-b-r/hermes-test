const express = require('express');
const router = express.Router();

router.get('/invoices', (req, res) => {
  res.status(200).json([
    { id: 4812, customerId: 17, total: 129.5, currency: 'GBP' }
  ]);
});

router.get('/invoices/:invoiceId', (req, res) => {
  const invoiceId = Number(req.params.invoiceId);
  res.status(200).json({
    id: invoiceId,
    customerId: 17,
    total: 129.5,
    currency: 'GBP'
  });
});

router.get('/customers', (req, res) => {
  res.status(200).json([
    { id: 17, name: 'Placeholder Ltd' }
  ]);
});

module.exports = router;


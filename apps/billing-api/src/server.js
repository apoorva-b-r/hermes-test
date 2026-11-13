const express = require('express');
const cors = require('cors');

const invoicesRouter = require('./routes/invoices');
const legacyRouter = require('./routes/legacy');
const adminRouter = require('./routes/admin');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/v2', invoicesRouter);
app.use('/', legacyRouter);
app.use('/', adminRouter);

app.use((req, res) => {
  // /admin/export only takes POST. Answering other methods here, rather than with
  // router.all, keeps the code to the one route the demo plants.
  if (req.path === '/admin/export') {
    return res.status(405).json({ error: 'method not allowed' });
  }
  res.status(404).json({ error: 'not found' });
});

const PORT = process.env.PORT || 3001;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Billing API listening on port ${PORT}`);
  });
}

module.exports = app;


fetch('https://api.yourdemo.com/v2/invoices')
  .then(response => response.json())
  .then(invoices => {
    const list = document.getElementById('invoices');
    invoices.forEach(invoice => {
      const li = document.createElement('li');
      li.textContent = 'Invoice #' + invoice.id;
      const id = invoice.id;
      li.addEventListener('click', () => {
        fetch('https://api.yourdemo.com/v2/invoices/' + id);
      });
      list.appendChild(li);
    });
  })
  .catch(error => {
    console.error('Error fetching invoices:', error);
  });

fetch('https://api.yourdemo.com/v2/customers')
  .then(response => response.json())
  .then(customers => {
    console.log('Customer count:', customers.length);
  })
  .catch(error => {
    console.error('Error fetching customers:', error);
  });

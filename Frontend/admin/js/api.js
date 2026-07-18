window.PortfolioAdmin = Object.freeze({
  csrfToken() {
    return document.querySelector('input[name="csrf_token"]')?.value || '';
  },
});

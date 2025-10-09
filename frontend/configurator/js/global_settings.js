export function initGlobalSettings() {
  const posButtons = document.querySelectorAll('.pos-btn');

  posButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      posButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
      button.classList.toggle('active');
    });
  });
}

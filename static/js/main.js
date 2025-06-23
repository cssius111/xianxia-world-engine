document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('command-input');
  const rollBtn = document.getElementById('roll-btn');

  function handleKeyUp(e) {
    if (e.target.disabled) {
      e.target.disabled = false;
    }
  }

  if (input) {
    input.addEventListener('keyup', handleKeyUp);
  }

  if (rollBtn) {
    rollBtn.addEventListener('click', () => {
      const val = Math.floor(Math.random() * 10 + 1);
      const c = document.getElementById('roll-cards');
      if (c) {
        c.textContent = '随机属性: ' + val;
      }
      if (val >= 7) {
        alert('极品');
      }
    });
  }
});

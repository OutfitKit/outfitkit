/*  OutfitKit · swipe-list
 *  Auto-init para <ul class="swipe"> con <li class="swipe-item">.
 *  Touch-first: detecta gesto horizontal, abre/cierra acciones.
 *  Click fuera cierra la fila abierta. Tap en la fila abierta también.
 */
(function () {
  const SWIPE_THRESHOLD = 32;       // px de gesto para abrir
  const VELOCITY_OPEN = 0.35;       // px/ms — flick rápido siempre abre
  const PAN_LOCK = 8;               // px de tolerancia antes de decidir eje

  function actionsWidth(item) {
    const styles = getComputedStyle(item.closest('.swipe') || item);
    const raw = styles.getPropertyValue('--actions-width').trim();
    if (!raw) return 160;
    if (raw.endsWith('rem')) return parseFloat(raw) * 16;
    return parseFloat(raw) || 160;
  }

  function setOpen(item, open) {
    if (open) {
      item.classList.add('is-open');
      item.setAttribute('data-swipe-open', 'true');
    } else {
      item.classList.remove('is-open');
      item.removeAttribute('data-swipe-open');
      const row = item.querySelector(':scope > .swipe-row');
      if (row) row.style.transform = '';
    }
  }

  function closeOthers(except) {
    document.querySelectorAll('.swipe-item.is-open').forEach((it) => {
      if (it !== except) setOpen(it, false);
    });
  }

  function init(item) {
    if (item._okSwipeBound) return;
    item._okSwipeBound = true;
    const row = item.querySelector(':scope > .swipe-row');
    if (!row) return;

    let startX = 0, startY = 0, startTime = 0, dx = 0, locked = null;
    const W = () => actionsWidth(item);

    function onStart(e) {
      const t = e.touches ? e.touches[0] : e;
      startX = t.clientX;
      startY = t.clientY;
      startTime = Date.now();
      dx = 0;
      locked = null;
      row.style.transition = 'none';
    }

    function onMove(e) {
      const t = e.touches ? e.touches[0] : e;
      const mx = t.clientX - startX;
      const my = t.clientY - startY;

      if (locked === null) {
        if (Math.abs(mx) < PAN_LOCK && Math.abs(my) < PAN_LOCK) return;
        locked = Math.abs(mx) > Math.abs(my) ? 'x' : 'y';
      }
      if (locked === 'y') return;
      if (e.cancelable) e.preventDefault();

      const isOpen = item.classList.contains('is-open');
      // si está abierto, el inicio es -W; si cerrado, 0
      const base = isOpen ? -W() : 0;
      dx = Math.max(-W() * 1.05, Math.min(W() * 0.15, base + mx));
      row.style.transform = `translateX(${dx}px)`;
    }

    function onEnd() {
      row.style.transition = '';
      if (locked !== 'x') return;
      const dt = Math.max(1, Date.now() - startTime);
      const isOpen = item.classList.contains('is-open');
      const w = W();
      const velocity = (dx - (isOpen ? -w : 0)) / dt; // px/ms
      let shouldOpen;
      if (Math.abs(velocity) >= VELOCITY_OPEN) {
        shouldOpen = velocity < 0; // flick a izquierda abre
      } else {
        shouldOpen = dx < -SWIPE_THRESHOLD;
      }
      setOpen(item, shouldOpen);
      if (shouldOpen) closeOthers(item);
    }

    row.addEventListener('touchstart', onStart, { passive: true });
    row.addEventListener('touchmove', onMove, { passive: false });
    row.addEventListener('touchend', onEnd);
    row.addEventListener('touchcancel', onEnd);

    // Mouse fallback (desktop) — opt-in con data-swipe-mouse en la lista
    if ((item.closest('.swipe') || item).hasAttribute('data-swipe-mouse')) {
      row.addEventListener('mousedown', (e) => {
        onStart(e);
        const mm = (ev) => onMove(ev);
        const mu = () => {
          onEnd();
          document.removeEventListener('mousemove', mm);
          document.removeEventListener('mouseup', mu);
        };
        document.addEventListener('mousemove', mm);
        document.addEventListener('mouseup', mu);
      });
    }
  }

  function initAll(root) {
    (root || document).querySelectorAll('.swipe .swipe-item').forEach(init);
  }

  // Click fuera cierra
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.swipe-item.is-open')) closeOthers(null);
  });

  // Click en la fila abierta también cierra (excepto si pulsas una swipe-btn)
  document.addEventListener('click', (e) => {
    const open = e.target.closest('.swipe-item.is-open');
    if (!open) return;
    if (e.target.closest('.swipe-btn')) return; // deja que la acción se ejecute
    if (e.target.closest('.swipe-row')) setOpen(open, false);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initAll());
  } else {
    initAll();
  }

  window.OKSwipe = { init, initAll, setOpen };
})();

/*  OutfitKit · pull-to-refresh
 *  Auto-init para <div data-ptr-host> que contenga un <div class="ptr"> y un
 *  contenedor con la lista. Touch-first. Reacciona al gesto "pull desde top".
 *
 *  Markup mínimo:
 *    <div data-ptr-host data-ptr-action="refreshList">
 *      <div class="ptr" data-state="idle">
 *        <div class="ptr-spinner"></div>
 *        <span class="ptr-label">Tira para actualizar</span>
 *      </div>
 *      <div class="ptr-content">… lista scrollable o no …</div>
 *    </div>
 *
 *  El callback se dispara como CustomEvent("ptr:refresh", {detail:{done}})
 *  en el host. El consumidor llama detail.done() cuando termina.
 *  Si no se llama done() en 3 s, el spinner vuelve a idle por seguridad.
 */
(function () {
  const TRIGGER = 64;     // px de pull para disparar refresh
  const MAX_PULL = 96;    // px de pull máximo (resistencia visual)
  const RESET_MS = 3000;

  function setLabel(host, state) {
    const lbl = host.querySelector('.ptr-label');
    if (!lbl) return;
    const labels = {
      idle: lbl.dataset.idle || 'Tira para actualizar',
      pulling: lbl.dataset.pulling || 'Tira para actualizar',
      ready: lbl.dataset.ready || 'Suelta para actualizar',
      refreshing: lbl.dataset.refreshing || 'Actualizando…',
    };
    lbl.textContent = labels[state] || labels.idle;
  }

  function init(host) {
    if (host._okPtrBound) return;
    host._okPtrBound = true;
    const ptr = host.querySelector(':scope > .ptr, .ptr');
    if (!ptr) return;

    let startY = 0, pull = 0, pulling = false, refreshing = false, resetTimer = null;
    const content = ptr.nextElementSibling || host;

    function setState(state) {
      ptr.setAttribute('data-state', state);
      setLabel(host, state);
    }
    setState('idle');

    function atTop() {
      // El gesto solo cuenta si la lista está al scrollTop=0
      const scroller = content.closest('[data-ptr-scroller]') || content;
      return (scroller.scrollTop || 0) <= 0;
    }

    function onStart(e) {
      if (refreshing) return;
      if (!atTop()) return;
      const t = e.touches ? e.touches[0] : e;
      startY = t.clientY;
      pulling = true;
      pull = 0;
    }

    function onMove(e) {
      if (!pulling || refreshing) return;
      const t = e.touches ? e.touches[0] : e;
      const dy = t.clientY - startY;
      if (dy <= 0) { pull = 0; ptr.style.setProperty('--pull-progress', 0); content.style.transform = ''; return; }
      if (e.cancelable) e.preventDefault();
      // Resistencia logarítmica
      pull = Math.min(MAX_PULL, Math.sqrt(dy) * 9);
      content.style.transform = `translateY(${pull}px)`;
      ptr.style.setProperty('--pull-progress', (pull / TRIGGER).toFixed(2));
      setState(pull >= TRIGGER ? 'ready' : 'pulling');
    }

    function onEnd() {
      if (!pulling || refreshing) return;
      pulling = false;
      content.style.transition = 'transform 280ms var(--ease-out, ease-out)';
      content.addEventListener('transitionend', () => { content.style.transition = ''; }, { once: true });

      if (pull >= TRIGGER) {
        refreshing = true;
        content.style.transform = `translateY(40px)`;
        setState('refreshing');

        const done = () => {
          clearTimeout(resetTimer);
          refreshing = false;
          pull = 0;
          content.style.transition = 'transform 320ms var(--ease-out, ease-out)';
          content.style.transform = '';
          setState('idle');
        };
        resetTimer = setTimeout(done, RESET_MS);
        host.dispatchEvent(new CustomEvent('ptr:refresh', { bubbles: true, detail: { done } }));
      } else {
        content.style.transform = '';
        setState('idle');
      }
      pull = 0;
    }

    const target = host;
    target.addEventListener('touchstart', onStart, { passive: true });
    target.addEventListener('touchmove', onMove, { passive: false });
    target.addEventListener('touchend', onEnd);
    target.addEventListener('touchcancel', onEnd);

    if (host.hasAttribute('data-ptr-mouse')) {
      target.addEventListener('mousedown', (e) => {
        onStart(e);
        const mm = (ev) => onMove(ev);
        const mu = () => { onEnd(); document.removeEventListener('mousemove', mm); document.removeEventListener('mouseup', mu); };
        document.addEventListener('mousemove', mm);
        document.addEventListener('mouseup', mu);
      });
    }
  }

  function initAll(root) {
    (root || document).querySelectorAll('[data-ptr-host]').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initAll());
  } else { initAll(); }

  window.OKPullToRefresh = { init, initAll };
})();

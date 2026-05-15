/*  OutfitKit · infinite scroll
 *  Auto-init para .iscroll. Usa IntersectionObserver sobre .iscroll-sentinel.
 *  Dispara CustomEvent("iscroll:more", {detail:{done, end}}) en .iscroll
 *  cuando el sentinel entra en viewport. El consumidor:
 *    - llama detail.done() al cargar más items.
 *    - llama detail.end() si no quedan más (marca .is-end).
 *
 *  Estados controlados vía clases:
 *    .iscroll.is-loading  → muestra .iscroll-loader
 *    .iscroll.is-end      → muestra .iscroll-end, desactiva observer
 */
(function () {
  function init(root) {
    if (root._okIScrollBound) return;
    root._okIScrollBound = true;

    const sentinel = root.querySelector('.iscroll-sentinel');
    if (!sentinel) return;
    // Scroll root opcional vía atributo, si no usa el viewport.
    const scrollRoot = root.dataset.iscrollRoot
      ? document.querySelector(root.dataset.iscrollRoot)
      : null;

    let pending = false;

    const io = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        if (pending) continue;
        if (root.classList.contains('is-end')) continue;
        pending = true;
        root.classList.add('is-loading');

        const done = () => {
          pending = false;
          root.classList.remove('is-loading');
        };
        const end = () => {
          pending = false;
          root.classList.remove('is-loading');
          root.classList.add('is-end');
          io.disconnect();
        };

        root.dispatchEvent(new CustomEvent('iscroll:more', {
          bubbles: true,
          detail: { done, end },
        }));
      }
    }, {
      root: scrollRoot,
      rootMargin: root.dataset.iscrollMargin || '300px 0px',
      threshold: 0,
    });

    io.observe(sentinel);
    root._okIScrollObserver = io;
  }

  function initAll(root) {
    (root || document).querySelectorAll('.iscroll').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initAll());
  } else { initAll(); }

  window.OKInfiniteScroll = { init, initAll };
})();

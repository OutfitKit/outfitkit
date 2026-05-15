/* ============================================================
   OutfitKit · Virtual Scroll runtime
   Auto-inicializa cualquier `.virtual-scroll` en el DOM.
   Lee config de data-attrs:
     data-vs-rows    JSON array de objetos {idx, main, meta} u
                     objetos arbitrarios si das data-vs-template.
     data-vs-height  altura de fila en px (default 40).
     data-vs-buffer  filas extra arriba/abajo a renderizar (default 5).
     data-vs-template  id de un <template> que define el HTML de fila;
                       usa {{key}} para interpolar campos del item.
                       Si no se da, usa la plantilla por defecto idx/main/meta.
   Emite:
     evento "vs:render" con {start, end, total} cada vez que renderiza.
   ============================================================ */
(function () {
  'use strict';

  var DEFAULT_TPL = '<span class="vs-idx">{{idx}}</span><span class="vs-main">{{main}}</span><span class="vs-meta">{{meta}}</span>';

  function escapeHTML(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderRow(tpl, item) {
    return tpl.replace(/\{\{(\w+)\}\}/g, function (_, key) {
      return escapeHTML(item[key]);
    });
  }

  function init(el) {
    if (el.__vsInit) return;
    el.__vsInit = true;

    var rowH = parseInt(el.dataset.vsHeight || '40', 10);
    var buffer = parseInt(el.dataset.vsBuffer || '5', 10);
    var rows;
    try {
      rows = JSON.parse(el.dataset.vsRows || '[]');
    } catch (e) {
      console.error('virtual-scroll: invalid data-vs-rows JSON', e);
      rows = [];
    }
    var total = rows.length;

    /* Plantilla de fila */
    var tplStr = DEFAULT_TPL;
    var tplId = el.dataset.vsTemplate;
    if (tplId) {
      var tplEl = document.getElementById(tplId);
      if (tplEl) tplStr = tplEl.innerHTML.trim();
    }

    /* Set CSS var de altura de fila por si difiere del default */
    el.style.setProperty('--row-height', rowH + 'px');

    /* Estructura interna */
    var spacer = document.createElement('div');
    spacer.className = 'virtual-scroll-spacer';
    spacer.style.height = (total * rowH) + 'px';
    el.appendChild(spacer);

    var viewport = document.createElement('div');
    viewport.className = 'virtual-scroll-viewport';
    el.appendChild(viewport);

    var lastStart = -1;
    var lastEnd = -1;

    function render() {
      var scrollTop = el.scrollTop;
      var visibleH = el.clientHeight;
      var start = Math.max(0, Math.floor(scrollTop / rowH) - buffer);
      var end = Math.min(total, Math.ceil((scrollTop + visibleH) / rowH) + buffer);

      /* Skip si la ventana no cambió (zoom / resize sin scroll) */
      if (start === lastStart && end === lastEnd) return;
      lastStart = start;
      lastEnd = end;

      viewport.style.transform = 'translateY(' + (start * rowH) + 'px)';

      var html = '';
      for (var i = start; i < end; i++) {
        html += '<div class="virtual-scroll-row" data-vs-index="' + i + '" style="height:' + rowH + 'px">';
        html += renderRow(tplStr, rows[i]);
        html += '</div>';
      }
      viewport.innerHTML = html;

      el.dispatchEvent(new CustomEvent('vs:render', {
        detail: { start: start, end: end, total: total }
      }));
    }

    el.addEventListener('scroll', render, { passive: true });
    window.addEventListener('resize', render, { passive: true });

    /* Render inicial */
    render();
    el.setAttribute('data-vs-ready', '');
  }

  function initAll(root) {
    (root || document).querySelectorAll('.virtual-scroll').forEach(init);
  }

  /* Auto-init al cargar */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { initAll(); });
  } else {
    initAll();
  }

  /* Exporta global para reinicializar tras inyectar HTML dinámicamente */
  window.OKVirtualScroll = { init: init, initAll: initAll };
})();

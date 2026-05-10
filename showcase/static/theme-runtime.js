/* OutfitKit · theme runtime (showcase bootstrap)
 *
 * Synchronous bootstrap that sets up window.okTheme BEFORE Datastar processes
 * the data-effect on .ok-app. Persists theme + template to localStorage.
 *
 * The full module would be shipped as part of the consumer's bundle; this is
 * a minimal showcase-only implementation.
 */
(function () {
  /* Normalize a value coming from localStorage so we never paint with a
     stale or unknown value. data-theme must be one of these two; everything
     else is treated as the default (dark). */
  var KNOWN_THEMES = { 'erplora': 1, 'erplora-light': 1 };
  function normTheme(v) {
    return KNOWN_THEMES[v] ? v : 'erplora';
  }
  var KNOWN_TEMPLATES = {
    '': 1, 'default': 1, 'corporate': 1, 'glass': 1,
    'glass-mono': 1, 'mono': 1,
  };
  function normTemplate(v) {
    return KNOWN_TEMPLATES[v] ? v : '';
  }

  var STATE = {
    theme: normTheme(localStorage.getItem('ok-theme')),
    template: normTemplate(localStorage.getItem('ok-template')),
  };

  function applyOn(el) {
    if (!el || !el.setAttribute) return;
    el.setAttribute('data-theme', STATE.theme);
    /* Templates compose with data-theme inside their CSS:
       [data-template="glass"][data-theme="erplora-light"] vs [data-theme="erplora"].
       So we just write the bare template name; the matching CSS picks the
       right variant based on data-theme. */
    if (STATE.template) el.setAttribute('data-template', STATE.template);
    else el.removeAttribute('data-template');
  }

  function applyAll() {
    applyOn(document.documentElement);
  }

  function persist() {
    try {
      localStorage.setItem('ok-theme', STATE.theme);
      localStorage.setItem('ok-template', STATE.template);
    } catch (_) {}
  }

  // First paint is correct.
  applyAll();

  window.okTheme = {
    getState: function () {
      return { theme: STATE.theme, template: STATE.template };
    },
    set: function (theme, template) {
      var dirty = false;
      if (typeof theme === 'string') {
        var nt = normTheme(theme);
        if (STATE.theme !== nt) { STATE.theme = nt; dirty = true; }
      }
      if (template !== undefined) {
        var ntpl = normTemplate(template);
        if (STATE.template !== ntpl) { STATE.template = ntpl; dirty = true; }
      }
      if (dirty) {
        persist();
        applyAll();
      }
    },
  };
})();

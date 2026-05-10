/* OutfitKit · theme runtime (showcase bootstrap)
 *
 * Synchronous bootstrap that sets up window.okTheme BEFORE Datastar processes
 * the data-effect on .ok-app. Persists theme + template to localStorage.
 *
 * The full module would be shipped as part of the consumer's bundle; this is
 * a minimal showcase-only implementation.
 */
(function () {
  var STATE = {
    theme: localStorage.getItem('ok-theme') || 'erplora',
    template: localStorage.getItem('ok-template') || '',
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
      if (typeof theme === 'string' && STATE.theme !== theme) {
        STATE.theme = theme;
        dirty = true;
      }
      if (template !== undefined && STATE.template !== (template || '')) {
        STATE.template = template || '';
        dirty = true;
      }
      if (dirty) {
        persist();
        applyAll();
      }
    },
  };
})();

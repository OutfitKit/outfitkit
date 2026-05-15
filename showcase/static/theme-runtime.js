/* OutfitKit · theme runtime (showcase bootstrap)
 *
 * Synchronous bootstrap that sets up window.okTheme BEFORE Datastar processes
 * the data-effect on .ok-app. Persists theme + template to localStorage.
 *
 * Cross-frame sync:
 *   The showcase mounts each app demo inside an <iframe>. When the parent
 *   shell switches Dark↔Light or changes the template, this runtime picks
 *   it up in the iframe through two channels:
 *     1. The browser-native `storage` event, fired in every same-origin
 *        document when localStorage is mutated by another document.
 *     2. A `message` (postMessage) listener as an explicit fallback —
 *        useful before localStorage propagates, or for scenarios where
 *        we want to force an immediate sync (e.g. on first paint).
 *
 * The full module would be shipped as part of the consumer's bundle; this
 * file is the showcase-only minimal implementation.
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
    'glass-mono': 1, 'mono': 1, 'erplora': 1,
  };
  function normTemplate(v) {
    return KNOWN_TEMPLATES[v] ? v : 'erplora';
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

  function notifyChildFrames() {
    /* Push the current state to any same-origin iframes embedded in this
       document. They will also receive a `storage` event, but postMessage
       is synchronous-ish and avoids a race where the iframe paints with
       the previous value before `storage` fires. */
    var msg = { type: 'ok-theme', theme: STATE.theme, template: STATE.template };
    var frames = document.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      try { frames[i].contentWindow.postMessage(msg, location.origin); } catch (_) {}
    }
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
        notifyChildFrames();
      }
    },
  };

  /* Cross-frame: react when another same-origin document writes to
     localStorage. This is what keeps an iframe in sync when its parent
     shell flips the theme. */
  window.addEventListener('storage', function (e) {
    if (e.key !== 'ok-theme' && e.key !== 'ok-template') return;
    var nextTheme = normTheme(localStorage.getItem('ok-theme'));
    var nextTemplate = normTemplate(localStorage.getItem('ok-template'));
    var dirty = false;
    if (nextTheme !== STATE.theme) { STATE.theme = nextTheme; dirty = true; }
    if (nextTemplate !== STATE.template) { STATE.template = nextTemplate; dirty = true; }
    if (dirty) applyAll();
  });

  /* postMessage path — the parent shell sends one when it changes its
     own theme. Faster than `storage` and works even if the iframe was
     loaded before the parent persisted to localStorage. */
  window.addEventListener('message', function (e) {
    if (e.origin !== location.origin) return;
    var d = e.data;
    if (!d || d.type !== 'ok-theme') return;
    var nextTheme = normTheme(d.theme);
    var nextTemplate = normTemplate(d.template);
    var dirty = false;
    if (nextTheme !== STATE.theme) { STATE.theme = nextTheme; dirty = true; }
    if (nextTemplate !== STATE.template) { STATE.template = nextTemplate; dirty = true; }
    if (dirty) {
      STATE.theme = nextTheme;
      STATE.template = nextTemplate;
      // The parent already persisted, but persist locally so a later
      // reload of this iframe has the right initial value too.
      persist();
      applyAll();
    }
  });
})();

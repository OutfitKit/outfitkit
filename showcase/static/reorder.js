/*  OutfitKit · reorder list
 *  Auto-init para <ol|ul class="reorder-list"> con <li class="reorder-item">.
 *  Drag handle: cualquier elemento con clase .reorder-handle dentro del item.
 *  Touch-first: usa pointer events para cubrir touch + mouse.
 *
 *  Dispara CustomEvent("reorder:change", {detail:{from,to,values}}) en la lista
 *  cuando se completa un reorden.
 *
 *  Cada .reorder-item debe tener data-value="<id>" para que values[] sea útil.
 */
(function () {

  function collectValues(list) {
    return [...list.querySelectorAll(':scope > .reorder-item')]
      .map(it => it.dataset.value || it.textContent.trim());
  }

  function indexOf(list, item) {
    return [...list.children].filter(c => c.classList.contains('reorder-item')).indexOf(item);
  }

  function init(list) {
    if (list._okReorderBound) return;
    list._okReorderBound = true;

    let dragging = null, ghost = null, startY = 0, originalNext = null;

    function onPointerDown(e) {
      const handle = e.target.closest('.reorder-handle');
      if (!handle) return;
      const item = handle.closest('.reorder-item');
      if (!item || item.parentElement !== list) return;
      e.preventDefault();
      dragging = item;
      originalNext = item.nextElementSibling;
      startY = e.clientY;
      item.classList.add('is-dragging');
      handle.setPointerCapture?.(e.pointerId);

      // Ghost flotante para feedback visual mientras arrastras
      ghost = item.cloneNode(true);
      ghost.style.position = 'fixed';
      ghost.style.left = item.getBoundingClientRect().left + 'px';
      ghost.style.top = item.getBoundingClientRect().top + 'px';
      ghost.style.width = item.offsetWidth + 'px';
      ghost.style.pointerEvents = 'none';
      ghost.style.opacity = '0.85';
      ghost.style.boxShadow = 'var(--shadow-lg, 0 12px 40px rgba(0,0,0,.25))';
      ghost.style.zIndex = '9999';
      ghost.classList.remove('is-dragging');
      document.body.appendChild(ghost);

      list.addEventListener('pointermove', onPointerMove);
      list.addEventListener('pointerup', onPointerUp);
      list.addEventListener('pointercancel', onPointerUp);
    }

    function onPointerMove(e) {
      if (!dragging) return;
      const dy = e.clientY - startY;
      if (ghost) ghost.style.transform = `translateY(${dy}px)`;

      // Encuentra sobre qué item se está arrastrando
      const targetItem = document.elementFromPoint(e.clientX, e.clientY)?.closest('.reorder-item');
      list.querySelectorAll('.is-drop-target').forEach(el => el.classList.remove('is-drop-target'));

      if (targetItem && targetItem !== dragging && targetItem.parentElement === list) {
        const rect = targetItem.getBoundingClientRect();
        const middle = rect.top + rect.height / 2;
        if (e.clientY < middle) {
          list.insertBefore(dragging, targetItem);
        } else {
          list.insertBefore(dragging, targetItem.nextElementSibling);
        }
        targetItem.classList.add('is-drop-target');
        setTimeout(() => targetItem.classList.remove('is-drop-target'), 180);
      }
    }

    function onPointerUp() {
      if (!dragging) return;
      const finalNext = dragging.nextElementSibling;
      dragging.classList.remove('is-dragging');

      if (ghost) ghost.remove();
      ghost = null;

      if (finalNext !== originalNext) {
        list.dispatchEvent(new CustomEvent('reorder:change', {
          bubbles: true,
          detail: {
            from: -1,  // pre-mover, ya estaba reubicado vivo
            to: indexOf(list, dragging),
            values: collectValues(list),
            item: dragging,
          }
        }));
      }
      dragging = null;
      list.removeEventListener('pointermove', onPointerMove);
      list.removeEventListener('pointerup', onPointerUp);
      list.removeEventListener('pointercancel', onPointerUp);
    }

    list.addEventListener('pointerdown', onPointerDown);
  }

  function initAll(root) {
    (root || document).querySelectorAll('.reorder-list').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initAll());
  } else { initAll(); }

  window.OKReorder = { init, initAll, collectValues };
})();

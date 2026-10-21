/* فرم محصول: عنوان‌های منو فقط برای دستهٔ انتخاب‌شده، با تیتر گروه */
(function () {
  function boxes() { return Array.prototype.slice.call(document.querySelectorAll('input[name="menu_items"]')); }
  function wrap(inp) { var l = inp.closest('label'); return (l && l.parentElement && l.parentElement.id !== 'id_menu_items') ? l.parentElement : (l || inp); }
  function render(clear) {
    var sel = document.getElementById('id_category'), cat = sel ? sel.value : '', last = null, shown = 0;
    document.querySelectorAll('.yp-grp,.yp-hint').forEach(function (e) { e.remove(); });
    boxes().forEach(function (inp) {
      var w = wrap(inp), ok = cat && inp.getAttribute('data-cat') === cat;
      var lb = inp.closest('label'); if (lb) lb.style.cssText = 'float:none;width:auto;display:inline;padding:0 4px;margin:0';
      w.style.display = ok ? '' : 'none';
      if (!ok && clear) inp.checked = false;
      if (ok) {
        shown++;
        var g = inp.getAttribute('data-group');
        if (g !== last) {
          var h = document.createElement('div'); h.className = 'yp-grp'; h.textContent = inp.getAttribute('data-group-title');
          h.style.cssText = 'font-weight:700;margin:10px 0 4px;color:#417690';
          w.parentNode.insertBefore(h, w); last = g;
        }
      }
    });
    var first = boxes()[0];
    if (!shown && first) {
      var p = document.createElement('p'); p.className = 'yp-hint'; p.style.cssText = 'color:#888;margin:4px 0';
      p.textContent = cat ? 'برای این دسته هنوز عنوانی در «گروه‌های منو» تعریف نشده.' : 'اول دسته‌بندی را انتخاب کنید.';
      var box = document.getElementById('id_menu_items') || wrap(first).parentNode;
      box.parentNode.insertBefore(p, box);
    }
  }
  document.addEventListener('DOMContentLoaded', function () {
    var sel = document.getElementById('id_category');
    if (sel) sel.addEventListener('change', function () { render(true); });
    render(false);
  });
})();

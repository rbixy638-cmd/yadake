/* پیش‌نمایش زندهٔ قیمت فروش در فرم محصول: قیمت خرید + درصد سود */
(function () {
  function num(v) { v = String(v || '').replace(/[۰-۹]/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'.indexOf(d); }).replace(/[^0-9.]/g, ''); return parseFloat(v) || 0; }
  function upd() {
    var p = document.getElementById('id_price'), m = document.getElementById('id_markup_percent'), d = document.getElementById('id_discount');
    var out = document.querySelector('.field-final_price .readonly');
    if (!p || !m || !out) return;
    var sale = Math.round(num(p.value) * (100 + num(m.value)) / 100);
    var fin = Math.floor((sale * (100 - num(d ? d.value : 0)) + 50) / 100);
    out.textContent = fin.toLocaleString('en-US') + '  (قیمت خرید ' + Math.round(num(p.value)).toLocaleString('en-US') + ' + ' + num(m.value) + '٪)';
  }
  document.addEventListener('DOMContentLoaded', function () {
    ['id_price', 'id_markup_percent', 'id_discount'].forEach(function (id) {
      var e = document.getElementById(id); if (e) e.addEventListener('input', upd);
    });
    upd();
  });
})();

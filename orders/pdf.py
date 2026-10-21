"""ساخت فاکتور / پیش‌فاکتور PDF فارسی با طرح فاکتورهای حسابداری ایران."""
import io
import os

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .jalali import jdate, to_fa
from .numwords import number_to_words
from django.utils import timezone

try:
    import arabic_reshaper
except Exception:  # pragma: no cover
    arabic_reshaper = None
try:
    from bidi import get_display
except Exception:  # pragma: no cover
    try:
        from bidi.algorithm import get_display
    except Exception:
        get_display = None

FONT = 'YPFont'
FONT_B = 'YPFontBold'
_ready = False


def _register():
    global _ready
    if _ready:
        return
    d = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    regular = next((os.path.join(d, f) for f in ('Vazirmatn-Regular.ttf', 'Vazir.ttf', 'DejaVuSans.ttf')
                    if os.path.exists(os.path.join(d, f))), None)
    bold = next((os.path.join(d, f) for f in ('Vazirmatn-Bold.ttf', 'Vazir-Bold.ttf', 'DejaVuSans-Bold.ttf')
                 if os.path.exists(os.path.join(d, f))), regular)
    if not regular:
        raise RuntimeError('فونت فارسی در static/fonts پیدا نشد.')
    pdfmetrics.registerFont(TTFont(FONT, regular))
    pdfmetrics.registerFont(TTFont(FONT_B, bold))
    _ready = True


def shape(t):
    t = str(t)
    if arabic_reshaper and get_display:
        return get_display(arabic_reshaper.reshape(t))
    return t


_LATIN = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')


def make_fmt(site):
    """ارقام فاکتور: انگلیسی (مثل نمونهٔ نرم‌افزار حسابداری) یا فارسی؛ از تنظیمات سایت."""
    persian = getattr(site, 'invoice_digits', 'latin') == 'persian'

    def fd(s):
        s = str(s)
        return to_fa(s.translate(_LATIN)) if persian else s.translate(_LATIN)

    def money(n):
        return fd('{:,}'.format(int(n)))
    return fd, money


def stamp(dt):
    dt = timezone.localtime(dt) if timezone.is_aware(dt) else dt
    h = dt.hour
    return '%s   %02d:%02d:%02d %s' % (jdate(dt), h % 12 or 12, dt.minute, dt.second, 'ق.ظ' if h < 12 else 'ب.ظ')


def _wrap(text, width, font, size):
    words, lines, cur = str(text).split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if pdfmetrics.stringWidth(shape(t), font, size) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or ['']


def build_invoice(order, site, kind='invoice'):
    """kind: invoice (فاکتور فروش، بعد از پرداخت) | pre (پیش‌فاکتور، قبل از پرداخت)."""
    _register()
    fd, money = make_fmt(site)
    scale = 10 if getattr(site, 'invoice_unit', 'toman') == 'rial' else 1
    uw = 'ریال' if scale == 10 else 'تومان'
    site_name = getattr(site, 'site_name', 'یدک‌پخش')
    phone = getattr(site, 'phone', '')
    title = '( فاکتور فروش )' if kind == 'invoice' else '( پیش فاکتور )'

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4
    M = 28
    L, R = M + 10, W - M - 10
    items = list(order.items.all())
    pay = order.payments.filter(status='success').first() if kind == 'invoice' else None
    inv_date = fd(jdate(order.paid_at if (kind == 'invoice' and order.paid_at) else order.created))
    cust = order.customer
    debt = int(getattr(cust, 'debt', 0) or 0) * scale

    def rt(x, y, text, size=10, bold=False):
        c.setFont(FONT_B if bold else FONT, size)
        c.drawRightString(x, y, shape(text))

    def lt(x, y, text, size=10, bold=False):
        c.setFont(FONT_B if bold else FONT, size)
        c.drawString(x, y, shape(text))

    def ct(x, y, text, size=10, bold=False):
        c.setFont(FONT_B if bold else FONT, size)
        c.drawCentredString(x, y, shape(text))

    def tab_line(y, label):
        c.setStrokeColorRGB(0.05, 0.05, 0.05)
        c.setLineWidth(1.6)
        c.line(M, y, W - M, y)
        w = pdfmetrics.stringWidth(shape(label), FONT_B, 9) + 26
        c.setFillColorRGB(0.94, 0.94, 0.94)
        c.setLineWidth(1)
        c.roundRect(W / 2 - w / 2, y - 8, w, 16, 5, stroke=1, fill=1)
        c.setFillColorRGB(0, 0, 0)
        ct(W / 2, y - 3, label, 9, True)

    # ---- سربرگ: در همهٔ صفحه‌ها تکرار می‌شود
    addr_lines = _wrap('آدرس : ' + (order.address or '—'), R - L, FONT, 9)[:3]
    hdr_bottom = H - 224 - 15 * len(addr_lines) - 8

    # ستون‌ها از راست به چپ مثل نمونه: ردیف، شرح کالا، مقدار، واحد، فی، مبلغ کل
    cols = [('ردیف', 28), ('شرح کالا', 216), ('مقدار', 46), ('واحد', 40), ('فی', 87), ('مبلغ کل', 102)]
    table_w = sum(w for _, w in cols)

    def desc(it):
        return it.name + (' ' + it.model_code if it.model_code else '')

    def row_h(it):
        return 14 * len(_wrap(desc(it), cols[1][1] - 10, FONT, 9)[:2]) + 8

    TB = 235
    y_min = M + 38
    top_rows = hdr_bottom - 24 - 22
    pages, cur_p, y = [], [], top_rows
    for it in items:
        h = row_h(it)
        if y - h < y_min:
            pages.append(cur_p)
            cur_p, y = [], top_rows
        cur_p.append(it)
        y -= h
    pages.append(cur_p)
    if y - TB < y_min:
        pages.append([])
    total_pages = len(pages)

    num = 0
    for pno, rows in enumerate(pages, 1):
        c.setStrokeColorRGB(0.05, 0.05, 0.05)
        c.setLineWidth(1)
        c.rect(M, M, W - 2 * M, H - 2 * M)
        ct(W / 2, H - 50, title, 10, True)
        ct(W / 2, H - 80, site_name, 24, True)
        lt(L, H - 50, 'صفحه %s از %s' % (fd(pno), fd(total_pages)), 9, True)
        rt(R, H - 104, 'تلفن های تماس : ' + fd(phone), 9, True)
        tab_line(H - 118, 'مشخصات فاکتور')
        rt(R, H - 146, 'توسط : ثبت آنلاین از سایت', 9, True)
        ct(W / 2 + 40, H - 146, 'تاریخ : ' + inv_date, 9, True)
        if pay and pay.ref_id:
            rt(R, H - 162, 'کد پیگیری پرداخت : ' + fd(pay.ref_id), 9)
        c.line(L + 104, H - 130, L + 104, H - 170)
        ct(L + 52, H - 142, 'شماره فاکتور', 9, True)
        ct(L + 52, H - 164, fd(order.number.replace('YP-', '')), 15)
        tab_line(H - 180, 'مشخصات خریدار')
        yy = H - 202
        rt(R, yy, 'عنوان : ' + order.name, 9, True)
        ct(W / 2 - 60, yy, 'کد : ' + fd(cust.pk), 9, True)
        yy -= 15
        rt(R, yy, 'تلفن های تماس : ( موبایل ) ' + fd(order.phone), 9, True)
        if order.postal_code:
            lt(L + 4, yy, 'کد پستی : ' + fd(order.postal_code), 9, True)
        yy -= 15
        for ln in addr_lines:
            rt(R, yy, ln, 9, True)
            yy -= 15

        if rows:
            yt = hdr_bottom - 24
            c.setFillColorRGB(0.92, 0.92, 0.92)
            c.rect(R - table_w, yt - 6, table_w, 22, stroke=1, fill=1)
            c.setFillColorRGB(0, 0, 0)
            x = R
            for t, w in cols:
                ct(x - w / 2, yt, t, 9, True)
                x -= w
            y = yt - 6
            for it in rows:
                num += 1
                h = row_h(it)
                lines = _wrap(desc(it), cols[1][1] - 10, FONT, 9)[:2]
                base = y - 14
                x = R
                vals = [fd(num), None, fd(it.qty), it.unit or 'عدد', money(it.unit_price * scale), money(it.line_total * scale)]
                for (t, w), v in zip(cols, vals):
                    if v is None:
                        yy = base
                        for ln in lines:
                            rt(x - 5, yy, ln, 9)
                            yy -= 14
                    else:
                        ct(x - w / 2, base, v, 9)
                    x -= w
                y -= h
                c.setStrokeColorRGB(0.82, 0.82, 0.82)
                c.line(R - table_w, y, R, y)
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            x = R
            for t, w in cols:
                c.line(x, yt + 16, x, y)
                x -= w
            c.line(x, yt + 16, x, y)
            c.line(R - table_w, y, R, y)
            c.setStrokeColorRGB(0.05, 0.05, 0.05)
        else:
            y = hdr_bottom - 10

        if pno == total_pages:
            total = order.total * scale
            qty = sum(i.qty for i in items)
            # ردیف جمع زیر جدول: تعداد اقلام، جمع مقدار، جمع مبلغ
            if rows:
                c.setFillColorRGB(0.96, 0.96, 0.96)
                c.rect(R - table_w, y - 20, table_w, 20, stroke=1, fill=1)
                c.setFillColorRGB(0, 0, 0)
                rt(R - 5, y - 14, 'تعداد : ' + fd(len(items)), 9, True)
                ct(R - cols[0][1] - cols[1][1] - cols[2][1] / 2, y - 14, fd(qty), 9, True)
                ct(R - table_w + cols[5][1] / 2, y - 14, money(total), 9, True)
                y -= 20
            y -= 14
            if order.note:
                for ln in _wrap('توضیحات : ' + order.note, R - L, FONT, 9)[:2]:
                    rt(R, y, ln, 9)
                    y -= 14
                y -= 4
            # خلاصهٔ مبالغ مثل نمونه
            rowsum = [('مبلغ کل فاکتور', money(total), False), ('تخفیف', '-', False), ('کرایه حمل', 'پس‌کرایه', False)]
            words = '%s %s قابل پرداخت' % (number_to_words(total), uw)
            wl = _wrap(words, R - L - 130, FONT_B, 9)[:3]
            box_h = 20 * len(rowsum) + 14 * len(wl) + 14
            c.setStrokeColorRGB(0.4, 0.4, 0.4)
            c.rect(L, y - box_h, R - L, box_h)
            yy = y - 15
            for a_, b_, bold in rowsum:
                rt(R - 8, yy, a_, 9, True)
                lt(L + 8, yy, b_, 9, True)
                yy -= 20
            c.line(L, yy + 14, R, yy + 14)
            lt(L + 8, yy - 1, money(total), 11, True)
            for k, ln in enumerate(wl):
                rt(R - 8, yy - 1 - 13 * k, ln, 9, True)
            y -= box_h + 18
            st = 'بدهکار' if debt > 0 else 'بی حساب'
            for ln in _wrap('مانده حساب شما تا قبل از این فاکتور در تاریخ ( %s ) ، مبلغ %s %s %s می باشد .' % (inv_date, money(debt), uw, st), R - L, FONT, 9):
                rt(R, y, ln, 9)
                y -= 14
            for ln in _wrap('مانده حساب نهایی شما ، مبلغ %s %s %s می باشد .' % (money(debt), uw, st), R - L, FONT, 9):
                rt(R, y, ln, 9)
                y -= 14
        c.setFillColorRGB(0.3, 0.3, 0.3)
        lt(L, M + 12, 'تاریخ چاپ : ' + fd(stamp(timezone.now())), 8, True)
        rt(R, M + 12, 'صادرشده از سایت ' + site_name, 8, True)
        c.setFillColorRGB(0, 0, 0)
        c.showPage()
    c.save()
    return buf.getvalue()

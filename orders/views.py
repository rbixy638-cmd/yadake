import datetime
import json
import re
import secrets
from functools import wraps

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from shop.models import Product, ShippingMethod, SiteSetting

from . import payments, pdf, sms
from .jalali import jdate
from .models import Customer, Driver, Order, OrderItem, OtpCode, Payment, Worker
from .utils import allow, client_ip, normalize_phone, to_en, valid_national_id

OTP_TTL = 120  # ثانیه
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')


# ---------------------------------------------------------------- کمکی
def jerr(msg, status=400, **extra):
    d = {'ok': False, 'error': msg}
    d.update(extra)
    return JsonResponse(d, status=status)


def jbody(request):
    try:
        d = json.loads(request.body.decode('utf-8') or '{}')
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def current_customer(request):
    cid = request.session.get('customer_id')
    if not cid:
        return None
    return Customer.objects.filter(pk=cid).first()


def customer_json(c):
    if not c:
        return None
    return {
        'phone': c.phone, 'first': c.first_name, 'last': c.last_name, 'email': c.email, 'address': c.address,
        'nid': c.national_id, 'postal': c.postal_code, 'photo': c.photo.url if c.photo else '',
        'lat': c.lat, 'lng': c.lng, 'debt': c.debt, 'complete': c.profile_done,
        'blocked': c.status == 'blocked', 'canBuy': c.can_buy,
        'createdAt': c.created.isoformat(),
    }


def first_image(product):
    if not product:
        return ''
    im = product.images.all()[:1]
    return im[0].image.url if im else ''


def order_json(o, detail=True):
    items = []
    for it in o.items.select_related('product').all():
        items.append({'id': it.product_id, 'name': it.name, 'model': it.model_code, 'brand': it.brand, 'q': it.qty,
                      'unit': it.unit_price, 'img': first_image(it.product),
                      'icon': (it.product.picto or it.product.category.picto) if it.product else 'bearing'})
    d = {
        'number': o.number, 'status': o.status, 'statusLabel': o.status_fa, 'date': o.created.isoformat(),
        'total': o.total, 'items': items, 'ship': o.ship_method, 'note': o.note, 'publicNote': o.public_note,
        'canPay': o.can_pay, 'invoice': reverse('invoice_pdf', args=[o.number]) if o.paid_at else '',
        'paidAt': o.paid_at.isoformat() if o.paid_at else '',
    }
    if detail:
        d.update({'name': o.name, 'address': o.address, 'lat': o.lat, 'lng': o.lng})
    return d


# ---------------------------------------------------------------- ورود با پیامک
@require_POST
def otp_send(request):
    phone = normalize_phone(jbody(request).get('phone'))
    if not phone:
        return jerr('شمارهٔ موبایل را درست وارد کنید.')
    if not allow('otp_ip:' + client_ip(request), 20, 3600) or not allow('otp_ph:' + phone, 6, 3600):
        return jerr('تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.', 429)
    last = OtpCode.objects.filter(phone=phone).first()
    if last and (timezone.now() - last.created).total_seconds() < 45:
        return jerr('برای ارسال مجدد کمی صبر کنید.', 429)
    code = '%05d' % (10000 + secrets.randbelow(90000))
    res = sms.send_otp(phone, code)
    if not res:
        return jerr('ارسال پیامک ناموفق بود. دوباره تلاش کنید.', 502)
    if isinstance(res, str):  # some providers (Melipayamak) generate the code themselves and return it
        code = res
    OtpCode.objects.create(phone=phone, code=code)
    from django.conf import settings
    out = {'ok': True, 'phone': phone, 'ttl': OTP_TTL}
    if settings.SMS_BACKEND == 'console':
        out['demoCode'] = code  # فقط برای تست؛ با SMS_BACKEND=kavenegar حذف می‌شود
    return JsonResponse(out)


@require_POST
def otp_verify(request):
    d = jbody(request)
    phone = normalize_phone(d.get('phone'))
    code = to_en(d.get('code')).strip()
    if not phone or not code:
        return jerr('اطلاعات ناقص است.')
    if not allow('otpv_ip:' + client_ip(request), 40, 600):
        return jerr('تلاش‌های زیاد؛ ده دقیقه دیگر دوباره امتحان کنید.', 429)
    otp = OtpCode.objects.filter(phone=phone, used=False).first()
    if not otp or (timezone.now() - otp.created).total_seconds() > OTP_TTL:
        return jerr('کد منقضی شد؛ دوباره ارسال کنید.')
    if otp.tries >= 5:
        return jerr('تعداد تلاش‌ها زیاد بود؛ کد جدید بگیرید.')
    if not secrets.compare_digest(otp.code, code):
        otp.tries += 1
        otp.save(update_fields=['tries'])
        return jerr('کد اشتباه است.')
    otp.used = True
    otp.save(update_fields=['used'])
    customer, _ = Customer.objects.get_or_create(phone=phone)
    request.session.cycle_key()
    request.session['customer_id'] = customer.pk
    return JsonResponse({'ok': True, 'complete': customer.profile_done})


@require_POST
def logout_view(request):
    request.session.pop('customer_id', None)
    return JsonResponse({'ok': True})


@require_POST
def profile_save(request):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    d = jbody(request)
    first, last = str(d.get('first', '')).strip(), str(d.get('last', '')).strip()
    email, address = str(d.get('email', '')).strip(), str(d.get('address', '')).strip()
    errs = {}
    if not 2 <= len(first) <= 40:
        errs['first'] = 'نام را وارد کنید.'
    if not 2 <= len(last) <= 60:
        errs['last'] = 'نام خانوادگی را وارد کنید.'
    if not EMAIL_RE.match(email) or len(email) > 100:
        errs['email'] = 'ایمیل معتبر وارد کنید.'
    if not 10 <= len(address) <= 300:
        errs['address'] = 'آدرس را کامل‌تر بنویسید.'
    nid = to_en(d.get('nid', '')).strip()
    if c.profile_done and c.national_id:  # کد ملی بعد از ثبت قفل است؛ فقط مدیر تغییر می‌دهد
        nid = c.national_id
    elif not valid_national_id(nid):
        errs['nid'] = 'کد ملی معتبر نیست.'
    postal = to_en(d.get('postal', '')).strip()
    if not re.fullmatch(r'\d{10}', postal):
        errs['postal'] = 'کد پستی باید ۱۰ رقم باشد.'
    try:
        lat, lng = float(d.get('lat')), float(d.get('lng'))
        if not (24 <= lat <= 40.5 and 43.5 <= lng <= 64):
            raise ValueError
    except Exception:
        errs['loc'] = 'موقعیت را روی نقشه (داخل ایران) انتخاب کنید.'
        lat = lng = None
    debt = c.debt
    if not c.profile_done:  # مبلغ بدهی فقط بار اول توسط مشتری وارد می‌شود؛ بعد از آن فقط مدیر تغییر می‌دهد
        try:
            debt = int(to_en(d.get('debt')))
            if debt < 0 or debt > 10 ** 13:
                raise ValueError
        except Exception:
            errs['debt'] = 'مبلغ بدهی را وارد کنید (اگر بدهی ندارید ۰).'
    if errs:
        return jerr('لطفاً فیلدها را اصلاح کنید.', fields=errs)
    c.first_name, c.last_name, c.email, c.address = first, last, email, address
    c.national_id, c.postal_code = nid, postal
    c.lat, c.lng, c.debt, c.profile_done = lat, lng, debt, True
    c.save()
    return JsonResponse({'ok': True, 'me': customer_json(c)})


@require_POST
def profile_photo(request):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    f = request.FILES.get('photo')
    if not f:
        return jerr('عکسی ارسال نشد.')
    if f.size > 4 * 1024 * 1024:
        return jerr('حجم عکس بیشتر از ۴ مگابایت است.')
    try:
        from PIL import Image
        img = Image.open(f)
        fmt = img.format
        img.verify()
    except Exception:
        return jerr('فایل انتخاب‌شده تصویر معتبر نیست.')
    ext = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}.get(fmt)
    if not ext:
        return jerr('فقط عکس JPG، PNG یا WEBP قابل قبول است.')
    f.seek(0)
    if c.photo:
        c.photo.delete(save=False)
    c.photo.save('u%d-%s.%s' % (c.pk, secrets.token_hex(3), ext), f, save=True)
    return JsonResponse({'ok': True, 'photo': c.photo.url})


# ---------------------------------------------------------------- سفارش
@require_POST
def order_create(request):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    if not c.profile_done:
        return jerr('ابتدا اطلاعات حساب را تکمیل کنید.', 403)
    if c.status == 'blocked':
        return jerr('حساب شما مسدود است و امکان ثبت سفارش ندارید.', 403)
    if c.debt > 0:
        return jerr('به دلیل بدهی معوق تا تسویه حساب امکان ثبت سفارش ندارید.', 403)
    d = jbody(request)
    items = d.get('items')
    if not isinstance(items, list) or not items or len(items) > 200:
        return jerr('سبد خرید خالی است.')
    merged = {}
    for it in items:
        try:
            pid, q = int(it['id']), int(it['q'])
        except Exception:
            return jerr('اطلاعات سبد خرید نامعتبر است.')
        if q <= 0:
            return jerr('تعداد نامعتبر است.')
        merged[pid] = merged.get(pid, 0) + q
    pmap = {p.pk: p for p in Product.objects.filter(pk__in=list(merged), active=True, category__active=True).select_related('brand')}
    for pid, q in merged.items():
        p = pmap.get(pid)
        if not p or p.stock < 1:
            return jerr('کالای «%s» موجود نیست؛ آن را از سبد حذف کنید.' % (p.name if p else 'نامشخص'))
        lo = min(p.min_qty, p.stock)
        if q < lo:
            return jerr('حداقل سفارش «%s» %d عدد است.' % (p.name, lo))
        if q > p.stock:
            return jerr('موجودی «%s» برای این تعداد کافی نیست؛ تعداد را کمتر کنید.' % p.name)
    ship = ShippingMethod.objects.filter(slug=str(d.get('ship', '')), active=True).first()
    if not ship:
        return jerr('روش ارسال را انتخاب کنید.')
    with transaction.atomic():
        order = Order.objects.create(
            number=Order.new_number(), customer=c, ship_method=ship.name, note=str(d.get('note', ''))[:300].strip(),
            name=c.full_name, phone=c.phone, address=c.address, postal_code=c.postal_code, lat=c.lat, lng=c.lng)
        total = 0
        for pid, q in merged.items():
            p = pmap[pid]
            OrderItem.objects.create(order=order, product=p, name=p.name, model_code=p.model_code, unit=p.unit,
                                     brand=p.brand.name if p.brand else '', qty=q, unit_price=p.wholesale_price)
            total += q * p.wholesale_price
        order.total = total
        order.save(update_fields=['total'])
    return JsonResponse({'ok': True, 'number': order.number})


@require_GET
@never_cache
def my_orders(request):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    qs = c.orders.prefetch_related('items__product__images', 'items__product__category')
    return JsonResponse({'ok': True, 'orders': [order_json(o, detail=False) for o in qs]})


@require_GET
@never_cache
def order_detail(request, number):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    o = c.orders.filter(number=number).first()
    if not o:
        return jerr('سفارش پیدا نشد.', 404)
    return JsonResponse({'ok': True, 'order': order_json(o)})


# ---------------------------------------------------------------- پرداخت آنلاین
@require_POST
def pay_start(request):
    c = current_customer(request)
    if not c:
        return jerr('ابتدا وارد شوید.', 401)
    o = c.orders.filter(number=str(jbody(request).get('number', ''))).first()
    if not o:
        return jerr('سفارش پیدا نشد.', 404)
    if o.status != 'approved':
        return jerr('این سفارش هنوز توسط مدیر تأیید نشده است یا قبلاً پرداخت شده.')
    try:
        url = payments.start(o, SiteSetting.load(), request.build_absolute_uri(reverse('pay_callback')))
    except payments.PaymentError as e:
        return jerr(str(e), 502)
    return JsonResponse({'ok': True, 'url': url})


@require_GET
def pay_mock(request, authority):
    """درگاه آزمایشی؛ فقط وقتی در تنظیمات «درگاه آزمایشی» انتخاب شده باشد کار می‌کند."""
    site = SiteSetting.load()
    pay = Payment.objects.select_related('order').filter(authority=authority, gateway='mock', status='initiated').first()
    if site.gateway != 'mock' or not pay:
        raise Http404()
    return render(request, 'ops/mock_gateway.html', {'pay': pay, 'order': pay.order,
                                                      'ok_url': '%s?Authority=%s&Status=OK' % (reverse('pay_callback'), authority),
                                                      'no_url': '%s?Authority=%s&Status=NOK' % (reverse('pay_callback'), authority)})


@require_GET
def pay_callback(request):
    authority = request.GET.get('Authority') or request.GET.get('authority') or ''
    pay = Payment.objects.select_related('order').filter(authority=authority).first()
    if not pay:
        return redirect('/')
    order = pay.order
    back = '/order/?id=' + order.number
    if pay.status == 'success':
        return redirect(back + '&paid=1')
    if request.GET.get('Status', '') != 'OK':
        pay.status = 'failed'
        pay.save(update_fields=['status'])
        return redirect(back + '&pay=failed')
    try:
        ok, ref = payments.verify(pay, SiteSetting.load())
    except Exception:
        ok, ref = False, ''
    if not ok:
        pay.status = 'failed'
        pay.save(update_fields=['status'])
        return redirect(back + '&pay=failed')
    with transaction.atomic():
        pay.status, pay.ref_id, pay.paid_at = 'success', ref, timezone.now()
        pay.save()
        if order.status == 'approved':
            for it in order.items.select_related('product'):
                if it.product_id:
                    p = Product.objects.select_for_update().get(pk=it.product_id)
                    p.stock = max(0, p.stock - it.qty)
                    p.save(update_fields=['stock'])
            order.set_status('paid')
    return redirect(back + '&paid=1')


@require_GET
def invoice_pdf(request, number):
    o = Order.objects.select_related('customer').filter(number=number).first()
    if not o:
        raise Http404()
    c = current_customer(request)
    staff = request.user.is_authenticated and request.user.is_staff
    if not staff and not (c and o.customer_id == c.pk):
        raise Http404()
    if not o.paid_at:
        raise Http404()           # PDF فقط بعد از پرداخت موفق صادر می‌شود
    data = pdf.build_invoice(o, SiteSetting.load(), 'invoice')
    resp = HttpResponse(data, content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="invoice-%s.pdf"' % o.number
    return resp


# ================================================================ کارگر انبار و راننده
PER_PAGE = 10
CARD_REL = ('customer', 'collected_by', 'driver')


def _since(rng):
    now = timezone.localtime()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return {'today': start, '7': now - datetime.timedelta(days=7), '30': now - datetime.timedelta(days=30)}.get(rng)


def _today_start():
    return timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)


def _filtered(qs, request, date_field):
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(phone__icontains=to_en(q)) |
                       Q(items__name__icontains=q) | Q(items__model_code__icontains=q)).distinct()
    since = _since(request.GET.get('range', ''))
    if since:
        qs = qs.filter(**{date_field + '__gte': since})
    ship = request.GET.get('ship', '')
    if ship:
        qs = qs.filter(ship_method=ship)
    return qs


def _ordered(qs, request, field, default):
    sort = request.GET.get('sort', default)
    return qs.order_by(field if sort == 'old' else '-' + field), sort


def _cards(orders):
    out = []
    for o in orders:
        rows = [{'it': it, 'img': first_image(it.product)} for it in o.items.all()]
        out.append({'o': o, 'rows': rows, 'qty': sum(r['it'].qty for r in rows)})
    return out


def _group(cards, field):
    groups = []
    for c in cards:
        label = jdate(getattr(c['o'], field))
        if not groups or groups[-1]['date'] != label:
            groups.append({'date': label, 'cards': []})
        groups[-1]['cards'].append(c)
    return groups


def _list_context(request, base, field, default):
    qs, sort = _ordered(_filtered(base, request, field), request, field, default)
    qs = qs.select_related(*CARD_REL).prefetch_related('items__product__images')
    page = Paginator(qs, PER_PAGE).get_page(request.GET.get('page'))
    qd = request.GET.copy()
    qd.pop('page', None)
    ships = list(Order.objects.exclude(ship_method='').order_by('ship_method').values_list('ship_method', flat=True).distinct())
    return {'page': page, 'qstring': qd.urlencode(), 'groups': _group(_cards(page.object_list), field), 'sort': sort,
            'ships': ships, 'f': {'q': request.GET.get('q', ''), 'range': request.GET.get('range', ''),
                                  'ship': request.GET.get('ship', ''), 'mine': request.GET.get('mine', '')}}


def _back(request, fallback):
    n = request.POST.get('next', '')
    if n.startswith(fallback) and '//' not in n and '\\' not in n:
        return redirect(n)
    return redirect(fallback)


# ---------------------------------------------------------------- صفحهٔ کارگر (جمع‌آوری)
def worker_required(view):
    @wraps(view)
    def inner(request, *a, **k):
        w = Worker.objects.filter(pk=request.session.get('worker_id'), active=True).first()
        if not w:
            return redirect('worker_login')
        request.worker = w
        return view(request, *a, **k)
    return inner


def _staff_auth(ident, password):
    """راننده (نام کاربری یا شمارهٔ موبایل) یا انباردار (نام کاربری) را با رمز تشخیص می‌دهد."""
    ident = (ident or '').strip()
    ph = normalize_phone(ident)
    cond = Q(username=ident) | Q(phone=ph) if ph else Q(username=ident)
    d = Driver.objects.filter(active=True).filter(cond).first()
    if d and d.check_password(password):
        return 'driver', d
    w = Worker.objects.filter(active=True, username=ident).first() if ident else None
    if w and w.check_password(password):
        return 'worker', w
    return None, None


def _staff_session(request, role, obj):
    request.session.cycle_key()
    request.session.pop('driver_id', None)
    request.session.pop('worker_id', None)
    request.session['driver_id' if role == 'driver' else 'worker_id'] = obj.pk
    return '/driver/' if role == 'driver' else '/worker/'


@require_POST
def staff_login_api(request):
    if not allow('sl:' + client_ip(request), 10, 600):
        return jerr('تلاش‌های زیاد؛ چند دقیقه صبر کنید.', 429)
    d = jbody(request)
    role, obj = _staff_auth(d.get('username', ''), str(d.get('password', '')))
    if not role:
        return jerr('نام کاربری یا رمز اشتباه است.', 401)
    return JsonResponse({'ok': True, 'role': role, 'url': _staff_session(request, role, obj)})


def worker_login(request):
    err = ''
    if request.method == 'POST':
        if not allow('sl:' + client_ip(request), 10, 600):
            err = 'تلاش‌های زیاد؛ چند دقیقه صبر کنید.'
        else:
            role, obj = _staff_auth(request.POST.get('username', ''), request.POST.get('password', ''))
            if role:
                return redirect(_staff_session(request, role, obj))
            err = 'نام کاربری یا رمز اشتباه است.'
    return render(request, 'ops/staff_login.html', {'error': err})


def worker_logout(request):
    request.session.pop('worker_id', None)
    return redirect('worker_login')


@worker_required
@never_cache
def worker_home(request):
    w = request.worker
    tab = 'done' if request.GET.get('tab') == 'done' else 'todo'
    start = _today_start()
    stats = {
        'todo': Order.objects.filter(status='paid').count(),
        'today': Order.objects.filter(collected_at__gte=start).count(),
        'today_mine': Order.objects.filter(collected_at__gte=start, collected_by=w).count(),
        'items_today': OrderItem.objects.filter(order__collected_at__gte=start).aggregate(s=Sum('qty'))['s'] or 0,
        'total_mine': Order.objects.filter(collected_by=w).count(),
        'total_all': Order.objects.filter(collected_at__isnull=False).count(),
    }
    if tab == 'todo':
        ctx = _list_context(request, Order.objects.filter(status='paid'), 'paid_at', 'old')
        ctx['field'] = 'paid_at'
    else:
        base = Order.objects.filter(collected_at__isnull=False)
        if request.GET.get('mine') == '1':
            base = base.filter(collected_by=w)
        ctx = _list_context(request, base, 'collected_at', 'new')
        ctx['field'] = 'collected_at'
    ctx.update({'worker': w, 'tab': tab, 'stats': stats, 'total_found': ctx['page'].paginator.count})
    return render(request, 'ops/worker.html', ctx)


@require_GET
@worker_required
@never_cache
def worker_count(request):
    return JsonResponse({'todo': Order.objects.filter(status='paid').count()})


@require_POST
@worker_required
def worker_collect(request, pk):
    note = request.POST.get('note', '').strip()[:250]
    with transaction.atomic():
        o = Order.objects.select_for_update().filter(pk=pk, status='paid').first()
        if o:
            o.collected_by = request.worker
            o.worker_note = note
            o.set_status('collected')
    return _back(request, '/worker/')


@require_POST
@worker_required
def worker_undo(request, pk):
    """برگرداندن «جمع شد» در صورت اشتباه (فقط اگر هنوز راننده برنداشته)."""
    with transaction.atomic():
        o = Order.objects.select_for_update().filter(pk=pk, status='collected', collected_by=request.worker).first()
        if o:
            o.status, o.collected_at, o.collected_by = 'paid', None, None
            o.save()
    return _back(request, '/worker/')


# ---------------------------------------------------------------- صفحهٔ راننده
def driver_required(view):
    @wraps(view)
    def inner(request, *a, **k):
        d = Driver.objects.filter(pk=request.session.get('driver_id'), active=True).first()
        if not d:
            return redirect('driver_login')
        request.driver = d
        return view(request, *a, **k)
    return inner


driver_login = worker_login  # صفحهٔ ورود مشترک؛ نقش از روی نام کاربری و رمز تشخیص داده می‌شود


def driver_logout(request):
    request.session.pop('driver_id', None)
    return redirect('driver_login')


@driver_required
@never_cache
def driver_home(request):
    d = request.driver
    tab = request.GET.get('tab') if request.GET.get('tab') in ('mine', 'done') else 'ready'
    start = _today_start()
    stats = {
        'ready': Order.objects.filter(status='collected').count(),
        'mine': Order.objects.filter(status='shipped', driver=d).count(),
        'today': Order.objects.filter(status='delivered', driver=d, delivered_at__gte=start).count(),
        'total': Order.objects.filter(status='delivered', driver=d).count(),
    }
    if tab == 'ready':
        ctx = _list_context(request, Order.objects.filter(status='collected'), 'collected_at', 'old')
        ctx['field'] = 'collected_at'
    elif tab == 'mine':
        ctx = _list_context(request, Order.objects.filter(status='shipped', driver=d), 'shipped_at', 'old')
        ctx['field'] = 'shipped_at'
    else:
        ctx = _list_context(request, Order.objects.filter(status='delivered', driver=d), 'delivered_at', 'new')
        ctx['field'] = 'delivered_at'
    ctx.update({'driver': d, 'tab': tab, 'stats': stats, 'total_found': ctx['page'].paginator.count})
    return render(request, 'ops/driver.html', ctx)


@require_GET
@driver_required
@never_cache
def driver_count(request):
    return JsonResponse({'ready': Order.objects.filter(status='collected').count()})


@require_POST
@driver_required
def driver_take(request, pk):
    with transaction.atomic():
        o = Order.objects.select_for_update().filter(pk=pk, status='collected').first()
        if o:
            o.driver = request.driver
            o.driver_note = ''
            o.set_status('shipped')
    return _back(request, '/driver/')


@require_POST
@driver_required
def driver_deliver(request, pk):
    note = request.POST.get('note', '').strip()[:250]
    with transaction.atomic():
        o = Order.objects.select_for_update().filter(pk=pk, status='shipped', driver=request.driver).first()
        if o:
            o.driver_note = note
            o.set_status('delivered')
    return _back(request, '/driver/')


@require_POST
@driver_required
def driver_return(request, pk):
    """نتوانستم تحویل بدهم: سفارش با دلیل به لیست «آمادهٔ ارسال» برمی‌گردد."""
    note = request.POST.get('note', '').strip()[:250]
    with transaction.atomic():
        o = Order.objects.select_for_update().filter(pk=pk, status='shipped', driver=request.driver).first()
        if o:
            o.status, o.shipped_at, o.driver = 'collected', None, None
            o.driver_note = ('برگشت خورد: ' + note) if note else 'برگشت خورد'
            o.save()
    return _back(request, '/driver/')

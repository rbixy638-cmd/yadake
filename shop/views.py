import json
import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from orders.models import Order
from orders.utils import allow, client_ip, to_en
from orders.views import current_customer, customer_json

from .models import (FAQ, Banner, Benefit, Brand, Category, ContactMessage, FooterColumn, Product,
                     ShippingMethod, SiteSetting, Slide, StaticPage, TopLink)

STATUS_COLORS = {'pending': '#8a5200', 'approved': '#176b32', 'blocked': '#b00020', 'paid': '#0a58ca',
                 'collected': '#8a5200', 'shipped': '#0a58ca', 'delivered': '#176b32', 'cancelled': '#777777'}
FLOW = ['pending', 'approved', 'paid', 'collected', 'shipped', 'delivered']
FLOW_LABELS = ['ثبت و بررسی', 'مجاز شد', 'پرداخت', 'جمع‌آوری', 'در مسیر', 'تحویل']


def _url(f):
    return f.url if f else ''


def _paragraphs(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text or '') if p.strip()]


def prose(text):
    """متن ساده را به HTML امن تبدیل می‌کند. «## عنوان»، «- مورد» و پاراگراف‌های جدا با خط خالی."""
    out = []
    for block in re.split(r'\n\s*\n', (text or '').strip()):
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        if lines[0].startswith('## '):
            m = re.match(r'^## (.*?)(?:\s*\{#([\w-]+)\})?$', lines[0])
            idattr = ' id="%s"' % escape(m.group(2)) if m and m.group(2) else ''
            out.append('<h2%s>%s</h2>' % (idattr, escape(m.group(1) if m else lines[0][3:])))
            lines = lines[1:]
            if not lines:
                continue
        if all(l.startswith('- ') for l in lines):
            out.append('<ul>' + ''.join('<li>%s</li>' % escape(l[2:]) for l in lines) + '</ul>')
        else:
            out.append('<p>%s</p>' % '<br>'.join(escape(l) for l in lines))
    return mark_safe(''.join(out))


def _footer():
    """ستون‌های فوتر؛ لینک‌های مقالات/بلاگ دیگر نمایش داده نمی‌شود و ستون خالی حذف می‌شود."""
    out = []
    for col in FooterColumn.objects.prefetch_related('links'):
        links = [{'t': l.title, 'u': l.url} for l in col.links.all() if not l.url.startswith(('/blog', '/article'))]
        if links:
            out.append({'title': col.title, 'links': links})
    return out


@never_cache
@ensure_csrf_cookie
def data_js(request):
    """همهٔ داده‌های فروشگاه از دیتابیس؛ توسط صفحات به‌صورت اسکریپت خوانده می‌شود."""
    s = SiteSetting.load()
    cats = Category.objects.filter(active=True).prefetch_related('groups__items')
    CATS = [{'id': c.slug, 'n': c.name, 'ic': c.picto, 'img': _url(c.image),
             'g': [[g.title, [i.title for i in g.items.all()]] for g in c.groups.all()]} for c in cats]
    brands = list(Brand.objects.filter(active=True))
    products = Product.objects.filter(active=True, category__active=True).select_related('category', 'brand').prefetch_related('images', 'menu_items')
    PRODUCTS = []
    for p in products:
        imgs = [_url(i.image) for i in p.images.all()]
        PRODUCTS.append({'id': p.pk, 'name': p.name, 'model': p.model_code, 'cat': p.category.slug,
                         'icon': p.picto or p.category.picto, 'brand': p.brand.name if p.brand else '',
                         'price': p.sale_price, 'disc': p.discount, 'wprice': p.wholesale_price,
                         # موجودی واقعی به مشتری نشان داده نمی‌شود: فقط موجود (عدد بزرگ) یا ناموجود (۰)
                         'min': min(p.min_qty, p.stock) if p.stock > 0 else p.min_qty,
                         'stock': 100000 if p.stock > 0 else 0, 'unit': p.unit, 'flags': p.flags, 'img': imgs[0] if imgs else '', 'images': imgs,
                         'desc': p.description, 'tags': [i.title for i in p.menu_items.all()]})
    POP = [{'t': i.title, 'c': g.category.slug, 'ic': g.category.picto, 'img': _url(g.category.image)}
           for c in cats for g in c.groups.all() for i in g.items.all() if i.is_popular]
    SHIP = [{'id': m.slug, 'n': m.name, 'd': m.description, 'ic': m.icon} for m in ShippingMethod.objects.filter(active=True)]
    SITE = {
        'name': s.site_name, 'tagline': s.tagline, 'logo': _url(s.logo), 'topText': s.top_text, 'phone': s.phone,
        'phoneFooterText': s.phone_footer_text, 'address': s.address, 'email': s.email, 'hours': s.work_hours,
        'copyright': s.copyright_name, 'instagram': s.instagram, 'telegram': s.telegram,
        'neshanKey': s.neshan_key, 'neshanType': s.neshan_type,
        'topLinks': [{'t': t.title, 'i': t.icon, 'img': _url(t.icon_image), 'u': t.url} for t in TopLink.objects.filter(active=True) if not t.url.startswith(('/blog', '/article'))],
        'slides': [{'t': x.title, 'p': x.text, 'b': x.button_text, 'u': x.url, 'ic': x.picto, 'img': _url(x.image),
                    'cls': x.theme, 'spin': x.spin} for x in Slide.objects.filter(active=True)],
        'benefits': [{'i': b.icon, 't': b.title, 's': b.subtitle} for b in Benefit.objects.filter(active=True)],
        'banners1': [], 'banners2': [],
        'footer': _footer(),
    }
    for b in Banner.objects.filter(active=True):
        SITE['banners1' if b.placement == 'home1' else 'banners2'].append(
            {'t': b.title, 's': b.subtitle, 'b': b.button_text, 'u': b.url, 'ic': b.picto, 'img': _url(b.image), 'cls': b.theme})
    STATUS = {k: [label, STATUS_COLORS.get(k, '#555')] for k, label in Order.STATUS_FA}
    ME = customer_json(current_customer(request))
    parts = [
        ('SITE', SITE), ('CATS', CATS), ('BRANDS', [b.name for b in brands]),
        ('BRAND_LOGOS', {b.name: _url(b.logo) for b in brands if b.logo}), ('PRODUCTS', PRODUCTS),
        ('POP', POP), ('SHIP', SHIP), ('STATUS', STATUS), ('FLOW', FLOW), ('FLOW_LABELS', FLOW_LABELS), ('ME', ME),
    ]
    js = '\n'.join('const %s=%s;' % (k, json.dumps(v, ensure_ascii=False)) for k, v in parts)
    js += '\nwindow.YP_CONFIG={neshanKey:SITE.neshanKey,neshanType:SITE.neshanType};\n'
    return HttpResponse(js, content_type='application/javascript; charset=utf-8')


def page(template):
    def view(request):
        return render(request, template)
    return view


def about(request):
    p = StaticPage.objects.filter(slug='about').first()
    return render(request, 'pages/text_page.html', {'p': p, 'html': prose(p.body) if p else '', 'pagekey': 'about',
                                                    'fallback_title': 'درباره ما'})


def guide(request):
    p = StaticPage.objects.filter(slug='guide').first()
    return render(request, 'pages/guide.html', {'p': p, 'html': prose(p.body) if p else '',
                                                'faqs': FAQ.objects.filter(active=True)})


def contact(request):
    return render(request, 'pages/contact.html')


@require_POST
def contact_api(request):
    if not allow('ct:' + client_ip(request), 8, 3600):
        return JsonResponse({'ok': False, 'error': 'تعداد پیام‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.'}, status=429)
    try:
        d = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        d = {}
    name, phone, msg = str(d.get('name', '')).strip(), to_en(d.get('phone', '')).strip(), str(d.get('message', '')).strip()
    if len(name) < 2 or not re.fullmatch(r'0\d{9,10}', phone) or len(msg) < 3:
        return JsonResponse({'ok': False, 'error': 'اطلاعات را کامل و درست وارد کنید.'}, status=400)
    ContactMessage.objects.create(name=name[:60], phone=phone[:20], message=msg[:2000])
    return JsonResponse({'ok': True})


def not_found(request, exception=None):
    return render(request, 'pages/404.html', status=404)

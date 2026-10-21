import json
from pathlib import Path
from urllib.parse import urlencode

from django.core.management.base import BaseCommand

from orders.models import Driver, Worker
from shop.models import (FAQ, Article, Banner, Benefit, Brand, Category, CategoryGroup, CategoryItem, FooterColumn,
                         FooterLink, Product, ShippingMethod, SiteSetting, Slide, StaticPage, TopLink)


def cat_url(**kw):
    return '/category/#' + urlencode(kw)


POPULAR = ['لنت ترمز جلو', 'فیلتر روغن', 'شمع', 'کمک\u200cفنر جلو', 'باتری']

ABOUT = """## ما که هستیم؟

یدک‌پخش مرکز پخش و فروش عمده قطعات یدکی خودرو برای فروشگاه‌ها، تعمیرگاه‌ها و رانندگان است. قیمت عمده هر قطعه و حداقل تعداد سفارش روی کارت محصول مشخص است تا بدون تماس و استعلام، سفارش خود را ثبت کنید.

## چه چیزی ارائه می‌دهیم؟

- قطعات از برندهای معتبر داخلی و خارجی در دسته‌های ترمز، فیلتر، موتور، جلوبندی، برق، روغن، لاستیک و ابزار
- پیش‌فاکتور رسمی و مشاورهٔ تخصصی برای انتخاب قطعهٔ سازگار با خودرو
- ارسال به سراسر کشور با باربری، تیپاکس و پیک
- ضمانت اصالت کالا و امکان بازگشت در صورت مغایرت

## چرا یدک‌پخش؟

هدف ما کوتاه کردن مسیر تأمین قطعه برای شماست: قیمت شفاف، موجودی به‌روز و پاسخ‌گویی سریع کارشناسان."""

GUIDE = """## مراحل خرید

- با شمارهٔ موبایل وارد شوید و اطلاعات حساب را تکمیل کنید.
- قطعه را جستجو یا از دسته‌بندی‌ها انتخاب کنید و با رعایت حداقل تعداد به سبد اضافه کنید.
- سفارش را ثبت کنید؛ پس از تأیید مدیر («مجاز» شدن سفارش)، از صفحهٔ سفارش آن را آنلاین پرداخت کنید.
- بعد از پرداخت، فاکتور PDF صادر می‌شود و سفارش جمع‌آوری و ارسال می‌شود.

## روش‌های ارسال {#shipping}

سفارش‌ها با باربری، تیپاکس و پیک (در تهران) ارسال می‌شوند. هزینهٔ ارسال به‌صورت پس‌کرایه و طبق تعرفهٔ شرکت حمل محاسبه می‌شود. قطعات حساس در بسته‌بندی ضدضربه ارسال می‌شوند.

## ضمانت بازگشت کالا {#returns}

در صورت مغایرت کالا با سفارش یا وجود عیب، تا ۳۰ روز پس از دریافت می‌توانید درخواست بازگشت بدهید. کالا باید بدون استفاده و در بستهٔ اصلی باشد."""

FAQS = [
    ('چطور ثبت‌نام کنم؟', 'با شمارهٔ موبایل وارد شوید، کد پیامکی را وارد کنید و سپس نام، ایمیل، آدرس و موقعیت روی نقشه را تکمیل کنید.'),
    ('حداقل تعداد سفارش چقدر است؟', 'هر کالا حداقل تعداد عمده مخصوص خود را دارد که روی کارت کالا و صفحهٔ محصول نوشته شده است.'),
    ('چرا نمی‌توانم خرید کنم؟', 'اگر در حساب شما بدهی معوق ثبت شده یا حساب مسدود شده باشد، امکان ثبت سفارش وجود ندارد. وضعیت را در بخش «وضعیت مالی» حساب ببینید.'),
    ('چرا سفارش من «در انتظار تأیید» است؟', 'هر سفارش ابتدا توسط مدیر بررسی می‌شود. پس از مجاز شدن، دکمهٔ پرداخت آنلاین فعال می‌شود.'),
    ('اگر قطعه با خودرو سازگار نبود چه کنم؟', 'پیش از سفارش کد فنی یا مدل خودرو را با کارشناسان بررسی کنید. در صورت مغایرت کالا طبق شرایط بازگشت قابل مرجوع است.'),
]


class Command(BaseCommand):
    help = 'داده‌های نمونهٔ فروشگاه را (فقط اگر خالی باشد) می‌سازد.'

    def handle(self, *args, **opts):
        data = json.loads((Path(__file__).resolve().parents[2] / 'seed_data.json').read_text(encoding='utf-8'))
        SiteSetting.load()

        if not Category.objects.exists():
            for ci, c in enumerate(data['CATS']):
                cat = Category.objects.create(slug=c['id'], name=c['n'], picto=c['ic'], sort_order=ci)
                for gi, (title, items) in enumerate(c['g']):
                    g = CategoryGroup.objects.create(category=cat, title=title, sort_order=gi)
                    for ii, t in enumerate(items):
                        CategoryItem.objects.create(group=g, title=t, sort_order=ii, is_popular=t in POPULAR)
            for bi, b in enumerate(data['BRANDS']):
                Brand.objects.create(name=b, sort_order=bi)
            cats = {c.slug: c for c in Category.objects.all()}
            brands = {b.name: b for b in Brand.objects.all()}
            for i, p in enumerate(data['PRODUCTS']):
                sale = (p['price'] * (100 - p['disc']) + 50) // 100   # قیمت فروش قبلی
                Product.objects.create(
                    category=cats[p['cat']], brand=brands.get(p['brand']), name=p['name'], model_code=p['model'],
                    price=int(round(sale / 1.2 / 100.0)) * 100, markup_percent=20, discount=0,   # قیمت خرید + ۲۰٪
                    min_qty=p['min'], stock=p['stock'],
                    picto='' if p['icon'] == cats[p['cat']].picto else p['icon'],
                    is_special='s' in p['flags'], is_bestseller='b' in p['flags'], is_new='n' in p['flags'], sort_order=i)
            self.stdout.write('Demo categories, brands and products created.')

        if not ShippingMethod.objects.exists():
            for i, (slug, s) in enumerate(zip(['bar', 'tipax', 'peyk'], data['SHIP'])):
                ShippingMethod.objects.create(slug=slug, name=s['n'], description=s['d'], icon=s['ic'], sort_order=i)
        if not TopLink.objects.exists():
            for i, (ic, t, u) in enumerate([('about', 'درباره ما', '/about/')]):
                TopLink.objects.create(title=t, icon=ic, url=u, sort_order=i)
        if not Slide.objects.exists():
            for i, (th, t, p, b, u, ic, sp) in enumerate([
                ('s1', 'قطعات یدکی اصل با قیمت عمده', 'لنت، فیلتر و جلوبندی از برندهای معتبر، مستقیم از انبار پخش.', 'ثبت‌نام و خرید عمده', '/login/', 'brake', True),
                ('s2', 'پیش‌فاکتور در کمتر از ۳۰ دقیقه', 'لیست قطعات را بفرستید؛ قیمت عمده و موجودی را همان روز بگیرید.', 'درخواست پیش‌فاکتور', '/contact/', 'filter', False),
                ('s3', 'تخفیف عمده تا ۳۰٪ روی شمع و فیلتر', 'با خرید کارتنی، قیمت هر عدد پایین‌تر می‌آید.', 'دیدن پیشنهادها', cat_url(list='special'), 'plug', False),
                ('s4', 'ارسال به سراسر کشور', 'باربری، تیپاکس و پیک؛ بسته‌بندی ضدضربه برای قطعات حساس.', 'مشاهده محصولات', cat_url(list='best'), 'tire', True)]):
                Slide.objects.create(theme=th, title=t, text=p, button_text=b, url=u, picto=ic, spin=sp, sort_order=i)
        if not Benefit.objects.exists():
            for i, (ic, t, s) in enumerate([('truck', 'پردازش، بسته‌بندی و ارسال', 'باربری، تیپاکس و پیک'),
                                            ('shield', 'ضمانت بازگشت کالا', 'تا ۳۰ روز پس از خرید'),
                                            ('shield', 'ضمانت اصالت کالا', 'قطعات اصل و معتبر'),
                                            ('headset', 'مشاوره تخصصی رایگان', 'انتخاب قطعه مناسب خودرو'),
                                            ('card', 'پرداخت آنلاین امن', 'درگاه بانکی معتبر')]):
                Benefit.objects.create(icon=ic, title=t, subtitle=s, sort_order=i)
        if not Banner.objects.exists():
            for i, (th, t, s, u, ic) in enumerate([
                ('lb1', 'لنت و دیسک ترمز', 'ایمنی از ترمز شروع می‌شود', cat_url(cat='brake', title='لنت و دیسک ترمز', terms='لنت|دیسک'), 'brake'),
                ('lb2', 'فیلتر روغن و هوا', 'تخفیف عمده تا ۲۵٪', cat_url(cat='filter', title='فیلتر روغن و هوا', terms='فیلتر روغن|فیلتر هوا'), 'filter'),
                ('lb3', 'کمک‌فنر و جلوبندی', 'برای همه خودروها', cat_url(cat='susp'), 'shock'),
                ('lb4', 'روغن موتور', 'کارتنی و بشکه‌ای', cat_url(cat='oil', sub='روغن موتور'), 'oil')]):
                Banner.objects.create(placement='home1', theme=th, title=t, subtitle=s, url=u, picto=ic, sort_order=i)
            Banner.objects.create(placement='home2', theme='lb1', title='فروش عمده قطعات یدکی', subtitle='قیمت همکار از تعداد مشخص هر کالا',
                                  button_text='ثبت‌نام و ورود', url='/login/', picto='tools', sort_order=0)
            Banner.objects.create(placement='home2', theme='lb2', title='ویژه تعمیرکاران و فروشگاه‌ها', subtitle='فاکتور رسمی و ارسال به سراسر کشور',
                                  button_text='ثبت‌نام همکار', url='/login/', picto='bearing', sort_order=1)
        if not FooterColumn.objects.exists():
            cols = [('دسترسی سریع', [('پیشنهاد ویژه', cat_url(list='special')), ('پرفروش‌ترین‌ها', cat_url(list='best')),
                                     ('برندها', '/#brands'), ('جدیدترین محصولات', cat_url(list='new'))]),
                    ('خدمات مشتریان', [('راهنمای خرید', '/guide/'), ('روش‌های ارسال', '/guide/#shipping'),
                                       ('ضمانت بازگشت کالا', '/guide/#returns'), ('ثبت‌نام همکار', '/login/')]),
                    ('درباره ما', [('درباره ما', '/about/'), ('تماس با ما', '/contact/')])]
            for i, (t, links) in enumerate(cols):
                col = FooterColumn.objects.create(title=t, sort_order=i)
                for j, (lt, lu) in enumerate(links):
                    FooterLink.objects.create(column=col, title=lt, url=lu, sort_order=j)
        if not StaticPage.objects.exists():
            StaticPage.objects.create(slug='about', title='درباره یدک‌پخش', body=ABOUT)
            StaticPage.objects.create(slug='guide', title='راهنمای خرید', body=GUIDE)
        if not FAQ.objects.exists():
            for i, (q, a) in enumerate(FAQS):
                FAQ.objects.create(question=q, answer=a, sort_order=i)
        if not Worker.objects.filter(username__isnull=False).exists():
            w = Worker.objects.filter(username__isnull=True).first() or Worker(name='انباردار نمونه')
            w.username = 'anbar'
            w.set_password('anbar123')
            w.active = True
            w.save()
            self.stdout.write('Demo warehouse worker: anbar / anbar123')
        if not Driver.objects.exists():
            d = Driver(name='راننده نمونه', username='driver', phone='09120000000')
            d.set_password('driver123')
            d.save()
            self.stdout.write('Demo driver created (driver / driver123).')

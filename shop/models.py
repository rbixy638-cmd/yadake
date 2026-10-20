from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# پیکتوگرام‌های دسته‌بندی و محصول (در static/assets/app.js تعریف شده‌اند)
PICTO_CHOICES = [
    ('brake', 'Brakes & clutch'), ('filter', 'Filter'), ('plug', 'Spark plug / engine'), ('shock', 'Shock absorber / suspension'),
    ('battery', 'Battery / electrical'), ('oil', 'Oil & fluids'), ('bearing', 'Bearing / body'), ('belt', 'Belt'),
    ('bulb', 'Bulb / lighting'), ('wiper', 'Wiper'), ('tire', 'Tire & rim'), ('tools', 'Tools'),
]
# آیکن‌های رابط (هدر، مزایا، بنرها)
UI_ICON_CHOICES = [
    ('about', 'About us'), ('org', 'Organizations'), ('partner', 'Partner'), ('gift', 'Gift'), ('truck', 'Truck / shipping'),
    ('shield', 'Shield / warranty'), ('headset', 'Headset / support'), ('card', 'Bank card'), ('question', 'Question'),
    ('location', 'Location'), ('home', 'Home'), ('call', 'Phone'), ('user', 'User'), ('mail', 'Email'),
    ('box', 'Package'), ('wallet', 'Wallet'), ('clock', 'Clock'), ('check', 'Check mark'), ('info', 'Info'),
]
SLIDE_THEMES = [('s1', 'Yellow'), ('s2', 'Black'), ('s3', 'Gray'), ('s4', 'Cream')]
BANNER_THEMES = [('lb1', 'Color 1'), ('lb2', 'Color 2'), ('lb3', 'Color 3'), ('lb4', 'Color 4')]
ARTICLE_THEMES = [('bg1', 'Color 1'), ('bg2', 'Color 2'), ('bg3', 'Color 3'), ('bg4', 'Color 4')]


class SiteSetting(models.Model):
    INVOICE_UNITS = [('toman', 'Toman'), ('rial', 'Rial')]
    GATEWAYS = [('mock', 'Test gateway (testing only)'), ('zarinpal', 'ZarinPal')]
    site_name = models.CharField('Site name', max_length=60, default='یدک‌پخش')
    tagline = models.CharField('Tagline under logo', max_length=120, default='پخش و عمده قطعات یدکی', blank=True)
    logo = models.ImageField('Logo', upload_to='site/', blank=True, help_text='If empty, the default logo is shown.')
    favicon = models.ImageField('Browser tab icon', upload_to='site/', blank=True)
    top_text = models.CharField('Text next to the header phone number', max_length=80, default='تماس با کارشناس یدک‌پخش :', blank=True)
    phone = models.CharField('Phone number', max_length=30, default='021-12345678', help_text='Example: 021-12345678')
    phone_footer_text = models.CharField('Text above the footer phone number', max_length=80, default='مشاوره و ثبت سفارش', blank=True)
    address = models.CharField('Address', max_length=250, default='تهران، خیابان نمونه، پلاک ۱۰', blank=True)
    email = models.CharField('Email', max_length=100, default='info@example.ir', blank=True)
    work_hours = models.CharField('Working hours', max_length=100, default='شنبه تا پنجشنبه، ۹ تا ۱۸', blank=True)
    copyright_name = models.CharField('Name in copyright', max_length=60, default='یدک‌پخش', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    telegram = models.URLField('Telegram', blank=True)
    neshan_key = models.CharField('Neshan map key (web key)', max_length=120, blank=True,
                                  help_text='Get it from developers.neshan.org. Empty = OpenStreetMap.')
    neshan_type = models.CharField('Neshan map style', max_length=30, default='standard-day', blank=True)
    gateway = models.CharField('Payment gateway', max_length=20, choices=GATEWAYS, default='mock',
                               help_text='For a live site, choose ZarinPal. The test gateway does not collect real money!')
    zarinpal_merchant = models.CharField('ZarinPal merchant code', max_length=60, blank=True)
    zarinpal_sandbox = models.BooleanField('ZarinPal sandbox mode', default=False)
    invoice_digits = models.CharField('Digit style on invoice', max_length=8, default='latin',
                                      choices=[('latin', 'Latin (1405/07/19)'), ('persian', 'Persian (۱۴۰۵/۰۷/۱۹)')])
    invoice_unit = models.CharField('Currency unit on PDF invoice', max_length=6, choices=INVOICE_UNITS, default='toman',
                                    help_text='Site prices are in Toman; if you choose Rial, PDF amounts are multiplied by 10.')

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings (header, contact, payment, map)'

    def __str__(self):
        return 'Site settings'

    def save(self, *a, **k):
        self.pk = 1
        super().save(*a, **k)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TopLink(models.Model):
    title = models.CharField('Title', max_length=40)
    icon = models.CharField('Icon', max_length=20, choices=UI_ICON_CHOICES, default='about')
    icon_image = models.ImageField('Or icon image', upload_to='icons/', blank=True)
    url = models.CharField('Link', max_length=200, default='/')
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Top header icon'
        verbose_name_plural = 'Top header icons'

    def __str__(self):
        return self.title


class FooterColumn(models.Model):
    title = models.CharField('Column title', max_length=60)
    sort_order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Footer column'
        verbose_name_plural = 'Footer columns'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name='links', verbose_name='Column')
    title = models.CharField('Title', max_length=60)
    url = models.CharField('Link', max_length=200)
    sort_order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Footer link'
        verbose_name_plural = 'Footer links'

    def __str__(self):
        return self.title


class Slide(models.Model):
    image = models.ImageField('Slide image', upload_to='slides/', blank=True,
                              help_text='Upload a full banner image (recommended 1300x420 px). It is shown completely, never cropped. '
                                        'If empty, the classic text + icon slide below is used.')
    url = models.CharField('Link (opens when the slide is clicked)', max_length=200, default='/category/#cat=all', blank=True)
    title = models.CharField('Title (classic slide only, optional)', max_length=120, blank=True)
    text = models.CharField('Text (classic slide only)', max_length=250, blank=True)
    button_text = models.CharField('Button text (classic slide only)', max_length=40, blank=True)
    picto = models.CharField('Icon (classic slide only)', max_length=20, choices=PICTO_CHOICES, default='brake')
    theme = models.CharField('Color (classic slide only)', max_length=5, choices=SLIDE_THEMES, default='s1')
    spin = models.BooleanField('Spin icon (classic slide only)', default=False)
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Home slide'
        verbose_name_plural = 'Home slides'

    def __str__(self):
        return self.title or ('Slide #%s' % self.pk)


class Benefit(models.Model):
    icon = models.CharField('Icon', max_length=20, choices=UI_ICON_CHOICES, default='truck')
    title = models.CharField('Title', max_length=60)
    subtitle = models.CharField('Subtitle', max_length=80, blank=True)
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Benefit (bar under slider)'
        verbose_name_plural = 'Benefits (bar under slider)'

    def __str__(self):
        return self.title


class Banner(models.Model):
    PLACES = [('home1', '4 colored cards'), ('home2', 'Two large banners (bottom)')]
    placement = models.CharField('Placement', max_length=10, choices=PLACES, default='home1')
    title = models.CharField('Title', max_length=80)
    subtitle = models.CharField('Subtitle', max_length=120, blank=True)
    button_text = models.CharField('Button text (large banner only)', max_length=40, blank=True)
    url = models.CharField('Link', max_length=200, default='/category/#cat=all')
    picto = models.CharField('Icon', max_length=20, choices=PICTO_CHOICES, default='brake')
    image = models.ImageField('Or custom image', upload_to='banners/', blank=True)
    theme = models.CharField('Color', max_length=5, choices=BANNER_THEMES, default='lb1')
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['placement', 'sort_order', 'id']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return self.title


class Category(models.Model):
    slug = models.SlugField('Latin slug (used in the link)', max_length=30, unique=True, allow_unicode=False,
                            help_text='Example: brake. English letters and digits only; do not change after creation.')
    name = models.CharField('Category name', max_length=60)
    picto = models.CharField('Icon', max_length=20, choices=PICTO_CHOICES, default='tools')
    image = models.ImageField('Or category image', upload_to='categories/', blank=True)
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class CategoryGroup(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='groups', verbose_name='Category')
    title = models.CharField('Group title (in menu)', max_length=60)
    sort_order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Menu group'
        verbose_name_plural = 'Menu groups'

    def __str__(self):
        return '%s ‹ %s' % (self.category.name, self.title)


class CategoryItem(models.Model):
    group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, related_name='items', verbose_name='Group')
    title = models.CharField('Sub-item title', max_length=60,
                             help_text='Products whose name contains this phrase are shown under this sub-item.')
    is_popular = models.BooleanField('Show in "Popular categories" on the home page', default=False)
    sort_order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Sub-item'
        verbose_name_plural = 'Sub-items'

    def __str__(self):
        return self.title


class Brand(models.Model):
    name = models.CharField('Brand name', max_length=60, unique=True)
    logo = models.ImageField('Brand logo', upload_to='brands/', blank=True)
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name


UNIT_CHOICES = [('عدد', 'عدد'), ('دست', 'دست'), ('ست', 'ست'), ('جفت', 'جفت'), ('کارتن', 'کارتن'), ('بسته', 'بسته'),
                ('لیتر', 'لیتر'), ('شاخه', 'شاخه'), ('متر', 'متر')]


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Category')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Brand')
    name = models.CharField('Product name', max_length=160)
    model_code = models.CharField('Part code', max_length=40, blank=True)
    price = models.PositiveBigIntegerField('Purchase price (Toman)', help_text='The price you paid; customers never see this.')
    markup_percent = models.DecimalField('Profit margin (+%)', max_digits=6, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)],
                                         help_text='Enter the percentage only; customer price = purchase price + this percentage.')
    discount = models.PositiveSmallIntegerField('Bulk discount (optional, %)', default=0, validators=[MaxValueValidator(90)],
                                                help_text='Use this to discount the sale price. Usually 0.')
    menu_items = models.ManyToManyField('CategoryItem', blank=True, related_name='products',
                                        verbose_name='Show under menu titles',
                                        help_text='You can select several titles; the product appears under all of them in the menu.')
    unit = models.CharField('Unit', max_length=12, choices=UNIT_CHOICES, default='عدد')
    min_qty = models.PositiveIntegerField('Minimum bulk order', default=1)
    stock = models.PositiveIntegerField('Stock', default=0,
                                        help_text='Customers do not see the number, only In stock / Out of stock. It decreases automatically with every payment.')
    picto = models.CharField('Icon (if no photo)', max_length=20, choices=PICTO_CHOICES, blank=True,
                             help_text='Empty = the category icon')
    description = models.TextField('Description', blank=True)
    is_special = models.BooleanField('Special offer', default=False)
    is_bestseller = models.BooleanField('Best seller', default=False)
    is_new = models.BooleanField('New', default=False)
    active = models.BooleanField('Active (shown on the site)', default=True)
    sort_order = models.PositiveIntegerField('Display order', default=0)
    created = models.DateTimeField('Date added', auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    @property
    def sale_price(self):
        """قیمت فروش = قیمت خرید + درصد سود (گرد شده به تومان)."""
        v = Decimal(self.price or 0) * (Decimal(100) + Decimal(self.markup_percent or 0)) / Decimal(100)
        return int(v.quantize(Decimal(1), rounding=ROUND_HALF_UP))

    @property
    def wholesale_price(self):
        """قیمتی که مشتری می‌پردازد (بعد از تخفیف اختیاری)."""
        return (self.sale_price * (100 - self.discount) + 50) // 100

    @property
    def flags(self):
        return ('s' if self.is_special else '') + ('b' if self.is_bestseller else '') + ('n' if self.is_new else '')


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Product')
    image = models.ImageField('Image', upload_to='products/')
    alt = models.CharField('Image description (alt text)', max_length=120, blank=True)
    sort_order = models.PositiveIntegerField('Order', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'

    def __str__(self):
        return self.alt or ('Image %s' % self.pk)


class Article(models.Model):
    title = models.CharField('Title', max_length=160)
    summary = models.CharField('Summary', max_length=250, blank=True)
    body = models.TextField('Article text', help_text='Separate paragraphs with a blank line.')
    image = models.ImageField('Image', upload_to='articles/', blank=True)
    picto = models.CharField('Icon (if no image)', max_length=20, choices=PICTO_CHOICES, default='brake')
    theme = models.CharField('Color', max_length=5, choices=ARTICLE_THEMES, default='bg1')
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)
    created = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-id']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField('Question', max_length=200)
    answer = models.TextField('Answer')
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class StaticPage(models.Model):
    SLUGS = [('about', 'About us'), ('guide', 'Buying guide')]
    slug = models.CharField('Page', max_length=20, choices=SLUGS, unique=True)
    title = models.CharField('Title', max_length=100)
    body = models.TextField('Text', help_text='Separate paragraphs with a blank line. Section heading: a line starting with ##.')

    class Meta:
        verbose_name = 'Text page'
        verbose_name_plural = 'Text pages (About us, Guide)'

    def __str__(self):
        return self.get_slug_display()


class ShippingMethod(models.Model):
    slug = models.SlugField('Slug', max_length=20, unique=True)
    name = models.CharField('Name', max_length=60)
    description = models.CharField('Description', max_length=160, blank=True)
    icon = models.CharField('Icon', max_length=20, choices=UI_ICON_CHOICES, default='truck')
    sort_order = models.PositiveIntegerField('Order', default=0)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Shipping method'
        verbose_name_plural = 'Shipping methods'

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField('Name', max_length=60)
    phone = models.CharField('Phone', max_length=20)
    message = models.TextField('Message')
    created = models.DateTimeField('Time', auto_now_add=True)
    handled = models.BooleanField('Followed up', default=False)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Contact message'
        verbose_name_plural = 'Contact messages / pro-forma requests'

    def __str__(self):
        return '%s — %s' % (self.name, self.phone)

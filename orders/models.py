import random

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from .utils import normalize_phone


class Customer(models.Model):
    STATUS = [('allowed', 'Allowed'), ('blocked', 'Blocked')]
    phone = models.CharField('Mobile', max_length=11, unique=True)
    first_name = models.CharField('Name', max_length=40, blank=True)
    last_name = models.CharField('Last name', max_length=60, blank=True)
    email = models.CharField('Email', max_length=100, blank=True)
    national_id = models.CharField('National ID', max_length=10, blank=True)
    postal_code = models.CharField('Postal code', max_length=10, blank=True)
    photo = models.ImageField('Profile photo', upload_to='avatars/', blank=True)
    address = models.TextField('Address', blank=True)
    lat = models.FloatField('Latitude', null=True, blank=True)
    lng = models.FloatField('Longitude', null=True, blank=True)
    debt = models.PositiveBigIntegerField('Outstanding debt (Toman)', default=0,
                                          help_text='If greater than zero, the customer cannot place orders.')
    status = models.CharField('Account status', max_length=10, choices=STATUS, default='allowed')
    admin_note = models.CharField('Admin note', max_length=250, blank=True)
    profile_done = models.BooleanField('Profile completed', default=False)
    created = models.DateTimeField('Joined', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip() or self.phone

    @property
    def full_name(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()

    @property
    def can_buy(self):
        return self.profile_done and self.status == 'allowed' and self.debt <= 0


class OtpCode(models.Model):
    phone = models.CharField(max_length=11, db_index=True)
    code = models.CharField(max_length=12)
    created = models.DateTimeField(auto_now_add=True)
    tries = models.PositiveSmallIntegerField(default=0)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        verbose_name = 'SMS code'
        verbose_name_plural = 'SMS codes'


class Worker(models.Model):
    name = models.CharField('Warehouse worker name', max_length=60)
    username = models.CharField('Username', max_length=30, unique=True, null=True)
    password = models.CharField('Password', max_length=128, default='')
    active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Warehouse worker'
        verbose_name_plural = 'Warehouse workers'

    def __str__(self):
        return self.name

    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        return bool(self.password) and check_password(raw, self.password)


class Driver(models.Model):
    name = models.CharField('Driver name', max_length=60)
    phone = models.CharField('Phone', max_length=20, blank=True)
    username = models.CharField('Username', max_length=30, unique=True)
    password = models.CharField('Password', max_length=128,
                                help_text='When editing, type the new password in the New password box.')
    active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'

    def __str__(self):
        return self.name

    def save(self, *a, **k):
        self.phone = normalize_phone(self.phone) or self.phone
        super().save(*a, **k)

    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        return bool(self.password) and check_password(raw, self.password)


class Order(models.Model):
    STATUS = [
        ('pending', 'Pending admin approval'),
        ('approved', 'Approved - ready for payment'),
        ('blocked', 'Blocked'),
        ('paid', 'Paid - waiting to be collected'),
        ('collected', 'Collected - ready to ship'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    # Persian labels: shown to customers on the storefront only (the admin panel is English)
    STATUS_FA = [
        ('pending', 'در انتظار تأیید مدیر'),
        ('approved', 'مجاز — آمادهٔ پرداخت'),
        ('blocked', 'مسدود'),
        ('paid', 'پرداخت شد — در انتظار جمع‌آوری'),
        ('collected', 'جمع‌آوری شد — آمادهٔ ارسال'),
        ('shipped', 'در مسیر ارسال'),
        ('delivered', 'تحویل شد'),
        ('cancelled', 'لغو شد'),
    ]
    number = models.CharField('Order number', max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders', verbose_name='Customer')
    status = models.CharField('Status', max_length=12, choices=STATUS, default='pending', db_index=True)
    total = models.PositiveBigIntegerField('Total (Toman)', default=0)
    ship_method = models.CharField('Shipping method', max_length=60, blank=True)
    note = models.CharField('Customer notes', max_length=300, blank=True)
    public_note = models.CharField('Admin message to customer', max_length=250, blank=True,
                                   help_text='E.g. the reason for blocking; the customer sees it on the order page.')
    # عکس لحظهٔ ثبت سفارش
    name = models.CharField('Recipient', max_length=100)
    phone = models.CharField('Mobile', max_length=11)
    address = models.TextField('Address')
    postal_code = models.CharField('Postal code', max_length=10, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    worker_note = models.CharField('Warehouse note', max_length=250, blank=True)
    driver_note = models.CharField('Driver note', max_length=250, blank=True)

    created = models.DateTimeField('Placed at', auto_now_add=True)
    approved_at = models.DateTimeField('Approved at', null=True, blank=True)
    paid_at = models.DateTimeField('Paid at', null=True, blank=True)
    collected_at = models.DateTimeField('Collected at', null=True, blank=True)
    collected_by = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Collected by')
    shipped_at = models.DateTimeField('Shipped at', null=True, blank=True)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Driver')
    delivered_at = models.DateTimeField('Delivered at', null=True, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return self.number

    STAMPS = {'approved': 'approved_at', 'paid': 'paid_at', 'collected': 'collected_at',
              'shipped': 'shipped_at', 'delivered': 'delivered_at'}

    @property
    def status_fa(self):
        return dict(self.STATUS_FA).get(self.status, self.status)

    def set_status(self, new, save=True):
        """تغییر وضعیت و ثبت زمان مرحله."""
        self.status = new
        f = self.STAMPS.get(new)
        if f and not getattr(self, f):
            setattr(self, f, timezone.now())
        if save:
            self.save()

    @property
    def can_pay(self):
        return self.status == 'approved'

    @classmethod
    def new_number(cls):
        while True:
            n = 'YP-%d' % random.SystemRandom().randint(100000, 999999)
            if not cls.objects.filter(number=n).exists():
                return n


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Order')
    product = models.ForeignKey('shop.Product', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Product')
    name = models.CharField('Product name', max_length=160)
    model_code = models.CharField('Part code', max_length=40, blank=True)
    brand = models.CharField('Brand', max_length=60, blank=True)
    unit = models.CharField('Unit', max_length=12, blank=True, default='عدد')
    qty = models.PositiveIntegerField('Quantity')
    unit_price = models.PositiveBigIntegerField('Unit price (Toman)')

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'

    def __str__(self):
        return '%s × %s' % (self.name, self.qty)

    @property
    def line_total(self):
        return self.qty * self.unit_price


class Payment(models.Model):
    STATUS = [('initiated', 'Initiated'), ('success', 'Successful'), ('failed', 'Failed')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='Order')
    gateway = models.CharField('Gateway', max_length=20)
    authority = models.CharField('Transaction ID', max_length=80, unique=True)
    amount = models.PositiveBigIntegerField('Amount (Toman)')
    status = models.CharField('Status', max_length=10, choices=STATUS, default='initiated')
    ref_id = models.CharField('Bank reference code', max_length=60, blank=True)
    created = models.DateTimeField('Created at', auto_now_add=True)
    paid_at = models.DateTimeField('Payment time', null=True, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return '%s — %s' % (self.order.number, self.get_status_display())

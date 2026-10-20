from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Customer, Driver, Order, OrderItem, Payment, Worker


@admin.action(description='Allow selected accounts')
def allow_customers(modeladmin, request, queryset):
    queryset.update(status='allowed')


@admin.action(description='Block selected accounts')
def block_customers(modeladmin, request, queryset):
    queryset.update(status='blocked')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('avatar', 'phone', 'full_name', 'national_id', 'debt', 'status', 'profile_done', 'created')
    list_display_links = ('phone',)
    list_editable = ('debt', 'status')
    list_filter = ('status', 'profile_done')
    search_fields = ('phone', 'first_name', 'last_name', 'email', 'national_id', 'postal_code')
    readonly_fields = ('created', 'avatar')
    actions = [allow_customers, block_customers]

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.full_name or '—'

    @admin.display(description='Photo')
    def avatar(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:38px;width:38px;border-radius:50%;object-fit:cover">', obj.photo.url)
        return '—'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = ('name', 'model_code', 'brand', 'qty', 'unit', 'unit_price')
    readonly_fields = ('name', 'model_code', 'brand', 'qty', 'unit', 'unit_price')

    def has_add_permission(self, request, obj=None):
        return False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    fields = ('gateway', 'authority', 'amount', 'status', 'ref_id', 'paid_at')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description='✔ Approve order (customer can pay)')
def approve_orders(modeladmin, request, queryset):
    n = 0
    for o in queryset.filter(status__in=['pending', 'blocked']):
        o.set_status('approved')
        n += 1
    modeladmin.message_user(request, '%d order(s) approved.' % n, messages.SUCCESS)


@admin.action(description='✖ Block order')
def block_orders(modeladmin, request, queryset):
    n = 0
    for o in queryset.filter(status__in=['pending', 'approved']):
        o.set_status('blocked')
        n += 1
    modeladmin.message_user(request, '%d order(s) blocked.' % n, messages.WARNING)


@admin.action(description='Cancel order')
def cancel_orders(modeladmin, request, queryset):
    n = 0
    for o in queryset.exclude(status__in=['paid', 'collected', 'shipped', 'delivered']):
        o.set_status('cancelled')
        n += 1
    modeladmin.message_user(request, '%d order(s) cancelled.' % n, messages.WARNING)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'total', 'status', 'created', 'invoice_link')
    list_filter = ('status',)
    search_fields = ('number', 'phone', 'name')
    date_hierarchy = 'created'
    actions = [approve_orders, block_orders, cancel_orders]
    inlines = [OrderItemInline, PaymentInline]
    save_on_top = True
    fieldsets = (
        ('Status (approve / block here)', {'fields': ('status', 'public_note')}),
        ('Order', {'fields': ('number', 'customer', 'total', 'ship_method', 'note')}),
        ('Recipient', {'fields': ('name', 'phone', 'address', 'postal_code', 'lat', 'lng')}),
        ('Warehouse & driver notes', {'fields': ('worker_note', 'driver_note')}),
        ('Times & agents', {'fields': ('created', 'approved_at', 'paid_at', 'collected_at', 'collected_by',
                                         'shipped_at', 'driver', 'delivered_at')}),
    )
    readonly_fields = ('number', 'customer', 'total', 'ship_method', 'note', 'name', 'phone', 'address', 'postal_code', 'lat', 'lng',
                       'worker_note', 'driver_note', 'created', 'approved_at', 'paid_at', 'collected_at', 'collected_by', 'shipped_at', 'driver',
                       'delivered_at')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.set_status(obj.status, save=False)
        super().save_model(request, obj, form, change)

    @admin.display(description='Invoice')
    def invoice_link(self, obj):
        if obj.paid_at:
            return format_html('<a href="{}" target="_blank">📄 Invoice</a>', reverse('invoice_pdf', args=[obj.number]))
        return '—'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'gateway', 'amount', 'status', 'ref_id', 'created')
    list_filter = ('status', 'gateway')
    search_fields = ('order__number', 'authority', 'ref_id')

    def has_add_permission(self, request):
        return False


class WorkerForm(forms.ModelForm):
    new_password = forms.CharField(label='New password', required=False, widget=forms.PasswordInput(render_value=False),
                                   help_text='Required for a new warehouse worker; when editing, fill it only to change the password.')

    class Meta:
        model = Worker
        fields = ('name', 'username', 'active')

    def clean(self):
        data = super().clean()
        if not self.instance.password and not data.get('new_password'):
            self.add_error('new_password', 'A password is required for this warehouse worker.')
        return data


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    form = WorkerForm
    list_display = ('name', 'username', 'active')
    list_editable = ('active',)

    def save_model(self, request, obj, form, change):
        pw = form.cleaned_data.get('new_password')
        if pw:
            obj.set_password(pw)
        super().save_model(request, obj, form, change)


class DriverForm(forms.ModelForm):
    new_password = forms.CharField(label='New password', required=False, widget=forms.PasswordInput(render_value=False),
                                   help_text='Required for a new driver; when editing, fill it only to change the password.')

    class Meta:
        model = Driver
        fields = ('name', 'phone', 'username', 'active')

    def clean(self):
        data = super().clean()
        if not self.instance.pk and not data.get('new_password'):
            self.add_error('new_password', 'A password is required for this driver.')
        return data


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    form = DriverForm
    list_display = ('name', 'username', 'phone', 'active')
    list_editable = ('active',)

    def save_model(self, request, obj, form, change):
        pw = form.cleaned_data.get('new_password')
        if pw:
            obj.set_password(pw)
        super().save_model(request, obj, form, change)

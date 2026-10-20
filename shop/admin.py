from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (FAQ, Article, Banner, Benefit, Brand, Category, CategoryGroup, CategoryItem, ContactMessage,
                     FooterColumn, FooterLink, Product, ProductImage, ShippingMethod, SiteSetting, Slide,
                     StaticPage, TopLink)

admin.site.site_header = 'Yadakpakhsh administration'
admin.site.site_title = 'Admin panel'
admin.site.index_title = 'Store administration dashboard'


def _thumb(f, h=44):
    if f:
        return format_html('<img src="{}" style="height:{}px;border-radius:6px">', f.url, h)
    return '—'


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site identity', {'fields': ('site_name', 'tagline', 'logo', 'favicon', 'copyright_name')}),
        ('Header & contact', {'fields': ('top_text', 'phone', 'phone_footer_text', 'address', 'email', 'work_hours')}),
        ('Social networks', {'fields': ('instagram', 'telegram')}),
        ('Iran map', {'fields': ('neshan_key', 'neshan_type')}),
        ('Online payment', {'fields': ('gateway', 'zarinpal_merchant', 'zarinpal_sandbox')}),
        ('Invoice', {'fields': ('invoice_unit', 'invoice_digits')}),
    )

    def changelist_view(self, request, extra_context=None):
        obj = SiteSetting.load()
        return redirect(reverse('admin:shop_sitesetting_change', args=[obj.pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TopLink)
class TopLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'url', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 2


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order')
    list_editable = ('sort_order',)
    inlines = [FooterLinkInline]


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'preview', 'url', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')
    fieldsets = (
        ('Image slide (recommended)', {'fields': ('image', 'url', 'sort_order', 'active')}),
        ('Classic text slide (only used when there is no image)',
         {'classes': ('collapse',), 'fields': ('title', 'text', 'button_text', 'picto', 'theme', 'spin')}),
    )

    @admin.display(description='Preview')
    def preview(self, obj):
        return _thumb(obj.image, 52)


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'icon', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement', 'theme', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')
    list_filter = ('placement',)


class CategoryGroupInline(admin.TabularInline):
    model = CategoryGroup
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'picto', 'sort_order', 'active', 'product_count')
    list_editable = ('sort_order', 'active')
    inlines = [CategoryGroupInline]

    @admin.display(description='Product count')
    def product_count(self, obj):
        return obj.products.count()


class CategoryItemInline(admin.TabularInline):
    model = CategoryItem
    extra = 3
    fields = ('title', 'is_popular', 'sort_order')


@admin.register(CategoryGroup)
class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'sort_order')
    list_filter = ('category',)
    list_editable = ('sort_order',)
    inlines = [CategoryItemInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'sort_order', 'active')
    list_display_links = ('name',)
    list_editable = ('sort_order', 'active')

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        return _thumb(obj.logo)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt', 'sort_order')


@admin.action(description='Activate')
def make_active(modeladmin, request, queryset):
    queryset.update(active=True)


@admin.action(description='Deactivate')
def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


class MenuItemsWidget(forms.CheckboxSelectMultiple):
    """چک‌باکس عنوان‌های منو؛ هر گزینه دسته و گروهش را دارد تا با جاوااسکریپت بر اساس دستهٔ انتخاب‌شده فیلتر شود."""
    meta = {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opt = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        m = self.meta.get(str(value))
        if m:
            opt['attrs'].update({'data-cat': str(m[0]), 'data-group': str(m[1]), 'data-group-title': m[2]})
        return opt


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = CategoryItem.objects.select_related('group__category').order_by(
            'group__category__sort_order', 'group__category_id', 'group__sort_order', 'group_id', 'sort_order', 'id')
        w = MenuItemsWidget()
        w.meta = {str(i.pk): (i.group.category_id, i.group_id, i.group.title) for i in qs}
        self.fields['menu_items'] = forms.ModelMultipleChoiceField(
            queryset=qs, required=False, widget=w, label='Show in menu (group → title)',
            help_text='First choose the Category; then that category\'s groups and titles appear. You can tick several titles.')
        self.fields['menu_items'].label_from_instance = lambda obj: obj.title

    def clean(self):
        data = super().clean()
        cat, items = data.get('category'), data.get('menu_items')
        if cat is not None and items is not None:
            data['menu_items'] = [i for i in items if i.group.category_id == cat.pk]   # فقط عنوان‌های همان دسته
        return data


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('thumb', 'name', 'model_code', 'category', 'brand', 'price', 'markup_percent', 'final_price', 'unit',
                    'min_qty', 'stock', 'stock_state', 'sort_order', 'active')
    list_display_links = ('name',)
    list_editable = ('price', 'markup_percent', 'min_qty', 'stock', 'sort_order', 'active')
    list_filter = ('category', 'brand', 'active', 'is_special', 'is_bestseller', 'is_new')
    search_fields = ('name', 'model_code', 'brand__name')
    list_select_related = ('category', 'brand')
    list_per_page = 50
    save_on_top = True
    inlines = [ProductImageInline]
    actions = [make_active, make_inactive]
    readonly_fields = ('final_price',)
    fieldsets = (
        (None, {'fields': ('name', 'model_code', 'category', 'menu_items', 'brand', 'unit', 'description')}),
        ('Price: purchase price + profit margin', {'fields': ('price', 'markup_percent', 'discount', 'final_price')}),
        ('Stock', {'fields': ('min_qty', 'stock')}),
        ('Show on home page', {'fields': ('is_special', 'is_bestseller', 'is_new', 'sort_order', 'active', 'picto')}),
    )

    class Media:
        js = ('admin/yp_price.js', 'admin/yp_menu.js')

    @admin.display(description='Customer sale price (Toman)')
    def final_price(self, obj):
        if not obj or not obj.pk:
            return 'Shown after saving, or live here as you change the numbers'
        return '{:,}'.format(obj.wholesale_price)

    @admin.display(description='Status on site')
    def stock_state(self, obj):
        return 'In stock' if obj.stock > 0 else 'Out of stock'

    @admin.display(description='Image')
    def thumb(self, obj):
        first = obj.images.all()[:1]
        return _thumb(first[0].image) if first else '—'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_order', 'active')
    list_editable = ('sort_order', 'active')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created', 'handled')
    list_editable = ('handled',)
    list_filter = ('handled',)
    readonly_fields = ('name', 'phone', 'message', 'created')

    def has_add_permission(self, request):
        return False

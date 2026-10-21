from urllib.parse import quote

from django.shortcuts import redirect

from .models import Customer

# مسیرهایی که بدون ورود هم باز هستند
OPEN_PREFIXES = (
    '/login/', '/register/',          # صفحهٔ ورود / عضویت
    '/static/', '/media/',            # فایل‌های ظاهری
    '/api/',                          # API ها خودشان ورود را بررسی می‌کنند (ارسال کد پیامکی و ...)
    '/data.js',                       # اسکریپت داده‌ای که خود صفحهٔ ورود هم لازم دارد
    '/admin/',                        # پنل مدیریت
    '/worker/', '/driver/',           # کارگر انبار و راننده (ورود جدا دارند)
    '/pay/',                          # بازگشت از درگاه پرداخت
    '/favicon.ico', '/robots.txt',
)


class CustomerGateMiddleware:
    """مرحلهٔ ۱: ورود با شمارهٔ موبایل (کد پیامکی). مرحلهٔ ۲: تکمیل اطلاعات در صفحهٔ ثبت‌نام.
    فقط بعد از هر دو مرحله بازدیدکننده به همهٔ سایت دسترسی دارد."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('GET', 'HEAD') and not request.path.startswith(OPEN_PREFIXES) and not self._is_staff(request):
            target = self._target(request)
            if target:
                path = request.path
                if path == '/':
                    return redirect(target)
                full = path + ('?' + request.META['QUERY_STRING'] if request.META.get('QUERY_STRING') else '')
                return redirect(target + '?next=' + quote(full, safe='/'))
        return self.get_response(request)

    @staticmethod
    def _is_staff(request):
        u = getattr(request, 'user', None)
        return u is not None and u.is_authenticated and u.is_staff   # مدیر واردشده در پنل

    @staticmethod
    def _target(request):
        """None = اجازهٔ عبور؛ در غیر این صورت آدرسی که باید به آن برود."""
        cid = request.session.get('customer_id')
        c = Customer.objects.filter(pk=cid).only('profile_done').first() if cid else None
        if not c:
            return '/login/'            # هنوز با موبایل وارد نشده
        if not c.profile_done:
            return '/register/'         # وارد شده ولی اطلاعاتش را کامل نکرده
        return None



class AdminEnglishMiddleware:
    """پنل /admin/ همیشه انگلیسی (LTR) است؛ بقیهٔ سایت فارسی می‌ماند."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            from django.utils import translation
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
        return self.get_response(request)

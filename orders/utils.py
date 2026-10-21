import re

from django.core.cache import cache

_EN = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def to_en(s):
    return str(s if s is not None else '').translate(_EN)


def normalize_phone(v):
    v = re.sub(r'[\s\-()]', '', to_en(v))
    if v.startswith('+98'):
        v = '0' + v[3:]
    elif v.startswith('0098'):
        v = '0' + v[4:]
    elif re.fullmatch(r'9\d{9}', v):
        v = '0' + v
    return v if re.fullmatch(r'09\d{9}', v) else ''


def client_ip(request):
    return request.META.get('REMOTE_ADDR', '') or 'x'


def allow(key, limit, window):
    """True اگر هنوز از حد مجاز تلاش در بازهٔ زمانی (ثانیه) رد نشده باشد؛ هر فراخوانی یک تلاش حساب می‌شود."""
    n = cache.get(key, 0)
    if n >= limit:
        return False
    if cache.add(key, 1, window) is False:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, window)
    return True


def valid_national_id(code):
    """اعتبارسنجی کد ملی ایران (۱۰ رقم + رقم کنترل)."""
    code = to_en(code).strip()
    if not re.fullmatch(r'\d{10}', code) or len(set(code)) == 1:
        return False
    s = sum(int(code[i]) * (10 - i) for i in range(9))
    r = s % 11
    return (r < 2 and int(code[9]) == r) or (r >= 2 and int(code[9]) == 11 - r)

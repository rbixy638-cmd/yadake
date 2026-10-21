"""تبدیل تاریخ میلادی به شمسی (بدون وابستگی خارجی)."""
from django.utils import timezone

_FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def to_fa(s):
    return str(s).translate(_FA)


def g2j(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def jdate(dt, with_time=False):
    if not dt:
        return '—'
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    jy, jm, jd = g2j(dt.year, dt.month, dt.day)
    s = '%04d/%02d/%02d' % (jy, jm, jd)
    if with_time:
        s += '  %02d:%02d' % (dt.hour, dt.minute)
    return to_fa(s)

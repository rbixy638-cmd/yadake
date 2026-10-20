"""اتصال به درگاه پرداخت اینترنتی. فقط پرداخت آنلاین پشتیبانی می‌شود."""
import json
import urllib.request
import uuid

from django.urls import reverse

from .models import Payment


class PaymentError(Exception):
    pass


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode() or '{}')


def _host(site):
    return 'https://sandbox.zarinpal.com' if site.zarinpal_sandbox else 'https://payment.zarinpal.com'


def start(order, site, callback_url):
    """یک تراکنش می‌سازد و آدرس رفتن به درگاه را برمی‌گرداند."""
    if site.gateway == 'zarinpal':
        if not site.zarinpal_merchant:
            raise PaymentError('مرچنت‌کد زرین‌پال در تنظیمات سایت وارد نشده است.')
        try:
            res = _post(_host(site) + '/pg/v4/payment/request.json', {
                'merchant_id': site.zarinpal_merchant,
                'amount': order.total * 10,  # ریال
                'callback_url': callback_url,
                'description': 'سفارش %s' % order.number,
                'metadata': {'mobile': order.phone},
            })
        except Exception:
            raise PaymentError('ارتباط با درگاه برقرار نشد. کمی بعد دوباره تلاش کنید.')
        data = res.get('data') if isinstance(res.get('data'), dict) else {}
        if data.get('code') == 100 and data.get('authority'):
            Payment.objects.create(order=order, gateway='zarinpal', authority=data['authority'], amount=order.total)
            return _host(site) + '/pg/StartPay/' + data['authority']
        raise PaymentError('درگاه درخواست را نپذیرفت. با پشتیبانی تماس بگیرید.')
    authority = 'MOCK' + uuid.uuid4().hex[:24]
    Payment.objects.create(order=order, gateway='mock', authority=authority, amount=order.total)
    return reverse('pay_mock', args=[authority])


def verify(payment, site):
    """(موفق؟، کد پیگیری)"""
    if payment.gateway == 'mock':
        return True, 'TEST-' + payment.authority[-6:]
    res = _post(_host(site) + '/pg/v4/payment/verify.json', {
        'merchant_id': site.zarinpal_merchant, 'amount': payment.amount * 10, 'authority': payment.authority})
    data = res.get('data') if isinstance(res.get('data'), dict) else {}
    if data.get('code') in (100, 101):
        return True, str(data.get('ref_id', ''))
    return False, ''

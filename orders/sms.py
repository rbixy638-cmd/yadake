import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings


def _log(msg):
    # يظهر في نافذة الأوامر (CMD) التي يعمل فيها الموقع / Shows in the terminal window running the site
    print('[SMS] ' + msg, flush=True)


def _send_melipayamak(phone):
    """Melipayamak OTP: it generates + sends the code itself and returns it. Returns the code (str) or False."""
    url = getattr(settings, 'MELIPAYAMAK_OTP_URL', '')
    if not url:
        _log('MELIPAYAMAK_OTP_URL is empty in settings.py')
        return False
    req = urllib.request.Request(
        url, data=json.dumps({'to': phone}).encode(),
        headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode() or '{}')
        except Exception:
            body = {}
        _log('Melipayamak ERROR http=%s body=%s' % (e.code, body))
        return False
    except Exception as e:
        _log('Could not reach melipayamak.com: %r' % (e,))
        return False
    code = str(body.get('code') or '').strip()
    if code.isdigit():
        return code
    _log('Melipayamak ERROR response=%s' % (body,))
    return False


def send_otp(phone, code):
    """ارسال کد ورود. روی حالت console فقط چاپ می‌شود (کد در صفحه نمایش داده می‌شود)."""
    if settings.SMS_BACKEND == 'melipayamak':
        return _send_melipayamak(phone)
    if settings.SMS_BACKEND == 'kavenegar' and settings.KAVENEGAR_API_KEY:
        method = getattr(settings, 'KAVENEGAR_METHOD', 'send')
        if method == 'lookup':  # needs the "advanced" Kavenegar service (error 426 on the free/standard one)
            path = 'verify/lookup.json'
            params = {'receptor': phone, 'token': code, 'template': settings.KAVENEGAR_TEMPLATE}
        else:  # plain SMS: works on the free/standard service
            path = 'sms/send.json'
            params = {'receptor': phone, 'message': getattr(settings, 'KAVENEGAR_MESSAGE', 'Your login code: {code}').format(code=code)}
            if getattr(settings, 'KAVENEGAR_SENDER', ''):
                params['sender'] = settings.KAVENEGAR_SENDER
        url = 'https://api.kavenegar.com/v1/%s/%s' % (settings.KAVENEGAR_API_KEY, path)
        data = urllib.parse.urlencode(params).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
                body = json.loads(r.read().decode() or '{}')
        except urllib.error.HTTPError as e:
            # Kavenegar answers errors with an HTTP status and a JSON body that says what is wrong
            try:
                body = json.loads(e.read().decode() or '{}')
            except Exception:
                body = {}
            ret = body.get('return', {})
            _log('Kavenegar ERROR http=%s status=%s message=%s (method=%s)' % (
                e.code, ret.get('status'), ret.get('message'), method))
            return False
        except Exception as e:  # no internet / blocked / timeout
            _log('Could not reach api.kavenegar.com: %r' % (e,))
            return False
        ret = body.get('return', {})
        if ret.get('status') == 200:
            return True
        _log('Kavenegar ERROR status=%s message=%s (method=%s)' % (
            ret.get('status'), ret.get('message'), method))
        return False
    print('[SMS] %s -> %s' % (phone, code))
    return True

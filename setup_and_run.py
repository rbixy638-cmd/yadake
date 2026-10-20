#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yadakpakhsh (Django) - one-click setup + run. Double-click RUN-Windows.bat / RUN-Mac.command / RUN-Linux.sh"""
import hashlib
import os
import shutil
import socket
import subprocess
import sys
import threading
import venv
import webbrowser

try:  # never crash on Windows consoles because of encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
VENV = os.path.join(ROOT, '.venv')
ADMIN_USER = os.environ.get('YP_ADMIN_USER', 's')
ADMIN_PASS = os.environ.get('YP_ADMIN_PASS', '0')
ENV = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')


def py():
    return os.path.join(VENV, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(VENV, 'bin', 'python')


def step(t):
    print('\n=== ' + t, flush=True)


def die(msg):
    print('\n[ERROR] ' + msg)
    print('Please take a screenshot of this window and send it to the developer.')
    if not os.environ.get('YP_NO_PAUSE'):
        try:
            input('Press Enter to close...')
        except Exception:
            pass
    sys.exit(1)


def run(args, **kw):
    r = subprocess.run(args, env=ENV, **kw)
    if r.returncode != 0:
        die('This command failed:  ' + ' '.join(args))
    return r


def venv_ok():
    if not os.path.exists(py()):
        return False
    try:
        return subprocess.run([py(), '-m', 'pip', '--version'], env=ENV, capture_output=True).returncode == 0
    except Exception:
        return False


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def free_port(start=8000):
    for p in range(start, start + 30):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return start


def main():
    if sys.version_info < (3, 8):
        die('Python 3.8 or newer is required (you have %s).' % sys.version.split()[0])
    try:
        ROOT.encode('ascii')
    except UnicodeEncodeError:
        print('[WARNING] The folder path has non-English characters. If something fails, move the folder to e.g. C:\\yadak')
    print('Python %s  |  folder: %s' % (sys.version.split()[0], ROOT))

    if not venv_ok():
        step('Creating the virtual environment (first run only)')
        shutil.rmtree(VENV, ignore_errors=True)
        try:
            venv.create(VENV, with_pip=True)
        except Exception as e:
            die('Could not create the virtual environment: %s\n(On Ubuntu/Debian run: sudo apt install python3-venv)' % e)
        if not venv_ok():
            die('The virtual environment was created but pip is missing.')

    if os.environ.get('YP_DRY_RUN'):
        print('\nDRY RUN OK (venv works). Stopping before install.')
        return

    req = open('requirements.txt', 'rb').read()
    mark = os.path.join(VENV, 'req.hash')
    h = hashlib.sha256(req).hexdigest()
    if not (os.path.exists(mark) and open(mark).read() == h):
        step('Installing libraries (Django, ...) - internet is required, please wait 1-3 minutes')
        cmd = [py(), '-m', 'pip', 'install', '--disable-pip-version-check', '--prefer-binary', '-r', 'requirements.txt']
        r = subprocess.run(cmd, env=ENV)
        if r.returncode != 0:
            print('\nInstall failed, trying once more...')
            r = subprocess.run(cmd, env=ENV)
        if r.returncode != 0:
            die('Library installation failed. Check your internet connection (turn VPN/proxy on or off) and run again.\n'
                'If your Python is very new (3.14+), install Python 3.12 from python.org and delete the .venv folder.')
        open(mark, 'w').write(h)

    step('Preparing the database')
    run([py(), 'manage.py', 'makemigrations', 'shop', 'orders', '--noinput'])
    run([py(), 'manage.py', 'migrate', '--noinput'])
    run([py(), 'manage.py', 'seed_demo'])

    code = ("from django.contrib.auth import get_user_model as g\n"
            "U=g()\n"
            "if not U.objects.filter(username=%r).exists():\n"
            "    U.objects.create_superuser(%r,None,%r);print('CREATED')\n" % (ADMIN_USER, ADMIN_USER, ADMIN_PASS))
    r = subprocess.run([py(), 'manage.py', 'shell', '-c', code], capture_output=True, text=True, env=ENV)
    created = 'CREATED' in (r.stdout or '')

    lan = os.environ.get('YP_LAN') == '1'
    port = free_port(int(os.environ.get('PORT', '8000')))
    ip = lan_ip() if lan else None
    print('\n' + '=' * 62)
    print('  The shop is READY')
    print('  Website      : http://localhost:%d/' % port)
    print('  Admin panel  : http://localhost:%d/admin/' % port)
    print('  Staff login  : http://localhost:%d/login/  -> small link "ورود کاربر" (or open /worker/ , /driver/)' % port)
    print('  Warehouse demo: anbar / anbar123      Driver demo: driver / driver123')
    print('  Admin login  : user "%s"  password "%s"%s' % (ADMIN_USER, ADMIN_PASS, '' if created else '  (unless you changed it)'))
    if ip:
        print('  Phone (same Wi-Fi): http://%s:%d/' % (ip, port))
    print('  To stop: close this window or press Ctrl+C')
    print('=' * 62 + '\n', flush=True)
    threading.Timer(3.0, lambda: webbrowser.open('http://localhost:%d/' % port)).start()
    try:
        subprocess.call([py(), 'manage.py', 'runserver', ('0.0.0.0:%d' if lan else '127.0.0.1:%d') % port, '--noreload'], env=ENV)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

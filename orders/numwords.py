"""تبدیل عدد به حروف فارسی (برای مبلغ فاکتور)."""
ONES = ['', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUND = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
SCALES = ['', 'هزار', 'میلیون', 'میلیارد', 'هزار میلیارد']


def _three(n):
    parts = []
    h, r = divmod(n, 100)
    if h:
        parts.append(HUND[h])
    if r < 20:
        if r:
            parts.append(ONES[r])
    else:
        t, o = divmod(r, 10)
        parts.append(TENS[t])
        if o:
            parts.append(ONES[o])
    return ' و '.join(parts)


def number_to_words(n):
    n = int(n)
    if n == 0:
        return 'صفر'
    groups = []
    while n > 0:
        n, g = divmod(n, 1000)
        groups.append(g)
    out = []
    for idx in range(len(groups) - 1, -1, -1):
        g = groups[idx]
        if g == 0:
            continue
        w = _three(g)
        if idx:
            w += ' ' + SCALES[min(idx, len(SCALES) - 1)]
        out.append(w)
    return ' و '.join(out)

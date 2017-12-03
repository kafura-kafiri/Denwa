# it is very good to add comma to addads and numbers

numbers = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
]

adads = [
    '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰',
]


def fa(n):
    if type(n) is int:
        n = str(n)
    return n.replace(
        numbers, adads
    )


def en(n):
    return int(n.replace(
        adads, numbers
    ))

letters = {
    '1000000000': 'میلیارد',
    '1000000': 'میلیون',
    '1000': 'هزار',
    '900': 'نهصد',
    '800': 'هشتصد',
    '700': 'هفتصد',
    '600': 'ششصد',
    '500': 'پانصد',
    '400': 'چهارصد',
    '300': 'سیصد',
    '200': 'دویست',
    '100': 'صد',
    '90': 'نود',
    '80': 'هشتاد',
    '70': 'هفتاد',
    '60': 'شصت',
    '50': 'پنجاه',
    '40': 'چهل',
    '30': 'سی',
    '20': 'بیست',
    '19': 'نوزده',
    '18': 'هجده',
    '17': 'هفده',
    '16': 'شانزده',
    '15': 'پانزده',
    '14': 'چهارده',
    '13': 'سیزده',
    '12': 'دوازده',
    '11': 'یازده',
    '10': 'ده',
    '9': 'نه',
    '8': 'هشت',
    '7': 'هفت',
    '6': 'شش',
    '5': 'پنج',
    '4': 'چهار',
    '3': 'سه',
    '2': 'دو',
    '1': 'یک',
    '0': 'صفر',
}

_ = 'و'


def letterize(n):
    n = str(int(n))
    print('>{}'.format(n))
    if n in letters:
        return letters[n]
    if len(n) > 9:
        return '{head} {billion} {_}{tail}'.format(head=letterize(n[:-9]) if n[:-9] != '1' else '', billion=letters['1000000000'], _=_, tail=letterize(n[-9:]))
    if len(n) > 6:
        return '{head} {million} {_}{tail}'.format(head=letterize(n[:-6]) if n[:-6] != '1' else '', million=letters['1000000'], _=_, tail=letterize(n[-6:]))
    if len(n) > 3:
        return '{head} {thousand} {_}{tail}'.format(head=letterize(n[:-3]) if n[:-3] != '1' else '', thousand=letters['1000'], _=_, tail=letterize(n[-3:]))
    if len(n) > 2:
        return '{head} {_}{tail}'.format(head=letterize(n[:-2] + '00'), _=_, tail=letterize(n[-2:]))
    else:
        return '{head} {_}{tail}'.format(head=letterize(n[:-1] + '0'), _=_, tail=letterize(n[-1:]))


def check_price(new, old):
    if old == '':
        return True, 'we our data is not complete so we just trust u'
    try:
        new = en(new)
        old = en(old)
    except Exception:
        return False, 'format error try again give me another number'
    messages = [
        (.3, False, 'do u know the format'),
        (.5, False, 'are u kidding give me another price'),
        (.9, True, 'wow amazing if i have money i will buy it'),
        (1.1, True, "it is to much u moron u don't have any chance to sell your shit"),
        (1.5, False, 'are u kidding give me another price'),
        (float('inf'), False, 'do u know the format')
    ]
    for m in messages:
        if m[0] * old > new:
            return m[1:3]
from sukhoi import MinerBS4, core


class GSMMiner(MinerBS4):
    def __init__(self, url, last):
        super(GSMMiner, self).__init__(url)
        self._last = last

    def run(self, dom):
        _ = []
        try:
            h1 = dom.find('h1', {'class': 'brand-name-english'}).text.strip()
            _.append(h1)
        except: pass
        try:
            h2 = dom.find('h2', {'class': 'brand-name-farsi'}).text.strip()
            _.append(h2)
        except: pass
        try:
            span = dom.find('span', {'id': 'price-with-warranty'}).text.strip()
            _.append(span)
        except: pass
        self.append(_)

        current_url = self.url
        current_url = current_url.split('/')
        head = '/'.join(current_url[:-2])
        tail = current_url[-2]
        next_url = head + '/' + str(int(tail) + 1) + '/'
        if int(tail) + 1 < self._last:
            self.next(next_url)


def crawl(first, last):
    base_url = 'http://www.gsm.ir/item/mobile/show/'
    _page = first
    models = []
    while True:
        _ = GSMMiner(base_url + str(_page) + '/', last)
        core.gear.mainloop()
        models.extend(_)
        _url = _.url.split('/')
        _page = int(_url[-2]) + 1
        if _page > last:
            break
    return models

arr = crawl(26160, 26165)
with open('models.txt', 'w+') as _file:
    for model in arr:
        line = ', '.join(model) + '\n'
        _file.write(line)
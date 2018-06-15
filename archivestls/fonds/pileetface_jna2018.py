from collections import OrderedDict

from requests_html import HTMLSession, HTML

from archivestls.collection import CollectionBot, __is_class__


BASE_URL = 'http://basededonnees.archives.toulouse.fr{}'
INDEX_PAGE_URL = BASE_URL.format('/4DCGI/Web_Script_Lit_Requete/34_28/ILUMP99999')


class PileEtFace(CollectionBot):

    def description_urls(self):

        pages = self.__find_pages__(INDEX_PAGE_URL)
        urls = OrderedDict()
        for index_page in pages:
            self.__log__.info('Processing page: %s', index_page)
            r = self.__session__.get(index_page)
            doc = HTML(html=r.html.find('html', first=True).html)
            self.__log__.info('  -> start parsing HTML')
            for t in doc.find('.col_premierecondition'):
                spans = t.find('span')
                for s in spans:
                    if __is_class__(s, 'lien') and 'Fi' in s.text:
                        item = s.text.replace('-', '').strip()
                        url = s.find('a', first=True).attrs['href']
                        self.__log__.info('%s -> %s', item, url)
                        urls[item] = BASE_URL.format(url)

        return urls

    def __find_pages__(self, url):
        pages = [url]
        self.__log__.info('Searching for pages URLs')
        r = self.__session__.get(url)
        doc = HTML(html=r.html.find('html', first=True).html)
        links = doc.find('a')
        for l in links:
            if 'title' in l.attrs and l.attrs['title'] == 'page' and l.attrs['href'] not in pages:
                self.__log__.info('  -> Adding %s', l.attrs['href'])
                pages.append(BASE_URL.format(l.attrs['href']))
        self.__log__.info('  --> All pages to crawl: %s', pages)
        return pages


def main():
    fonds = PileEtFace(name='jna2018')
    fonds.run()


if __name__ == '__main__':
    main()

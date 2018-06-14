from requests_html import HTMLSession, HTML

from archivestls.collection import CollectionBot, __is_class__


PAGES = [
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_Script_Lit_Requete/34_28/ILUMP99999',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00020349561/h26165/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00030349561/h6775/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00040349561/h27168/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00050349561/h997/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00060349561/h3394/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00070349561/h26458/ILUMP9546',
    'http://basededonnees.archives.toulouse.fr/4DCGI/Web_changePageListe/00080349561/h7319/ILUMP9546',
]

class PileEtFace(CollectionBot):

    def description_urls(self):
        urls = []
        for index_page in PAGES:
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
                        urls.append({item: url})

        return urls


def main():
    fonds = PileEtFace()
    fonds.run()

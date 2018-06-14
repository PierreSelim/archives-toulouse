import logging
import sys

from requests_html import HTMLSession, HTML


def metadata(url, html_session=None):
    """Metadata from URL of an item description."""
    session = html_session
    if not session:
        session = HTMLSession()
    r = session.get(url)
    html_content = r.html.find('html', first=True).html
    return __metadata__(HTML(html=html_content))


def __metadata__(doc):
    tab = doc.find('.tab_premierecondition', first=True)
    spans = tab.find('span')

    field_count = 0

    infos = {}
    field = None
    for s in spans:
        if __is_class__(s, 'titre'):
            field = s.text.replace(':', '').strip()
            field_count = field_count + 1
        elif field_count > 0 and field:
            infos[field] = s.text.strip()
            field = None
    return infos


def __is_class__(element, class_name):
    if 'class' in element.attrs:
        classes = element.attrs['class']
        return class_name in classes
    return False


class CollectionBot(object):

    def __init__(self):
        self.__session__ = HTMLSession()
        self.__log__ = logging.getLogger('archivetls')
        self.__setup_logger__()

    def __setup_logger__(self):
        """Setting up the LOG."""
        consolehandler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s    %(levelname)s    %(message)s',
            '%Y-%m-%d %H:%M:%S')
        consolehandler.setFormatter(formatter)
        consolehandler.setLevel(logging.INFO)
        self.__log__.addHandler(consolehandler)
        self.__log__.setLevel(logging.DEBUG)

    def description_urls(self):
        raise NotImplementedError

    def run(self):
        urls = self.description_urls()
        self.__log__.debug('URLs: %s', urls)

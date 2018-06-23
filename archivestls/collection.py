import configparser
import logging
import json
import os
import re
import sys
from collections import OrderedDict


import mwclient
from requests_html import HTMLSession, HTML
from sickle import Sickle


CACHE_PATH = '.cache_archivetls'
USER_AGENT = 'Archives Toulouse Uploader'


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

    def __init__(self, name='default_tls'):
        self.__bot_name__ = name
        self.__session__ = HTMLSession()
        self.__log__ = logging.getLogger('archivetls')
        self.__setup_logger__()
        if not os.path.exists(CACHE_PATH):
            os.mkdir(CACHE_PATH)

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
        descriptions = {
            item: {'url_notice': urls[item],
                   'metadata': metadata(urls[item], html_session=self.__session__)}
            for item in urls
        }
        descr_cache = os.path.join(CACHE_PATH, '{}_descr.json'.format(self.__bot_name__))
        self.__log__.info('Writing metadata cache in %s', descr_cache)
        with open(descr_cache, 'w') as f:
            json.dump(descriptions, f, indent=2, ensure_ascii=False)


class DublinCoreCollectionBot(object):

    def __init__(self,
                 name='archivetls',
                 url=None,
                 category=None,
                 path=None):
        self.__bot_name__ = name
        self.__url_api__ = url

        # logger
        self.__log__ = logging.getLogger('archivetls')
        self.__setup_logger__()

        # cache
        if not os.path.exists(CACHE_PATH):
            os.mkdir(CACHE_PATH)
        self.__cache_meta__ = os.path.join(CACHE_PATH, '{}_meta.json'.format(self.__bot_name__))
        self.__cache_descr__ = os.path.join(CACHE_PATH, '{}_descr.json'.format(self.__bot_name__))

        # mwclient
        self.__site__ = mwclient.Site('commons.wikimedia.org',
            clients_useragent=USER_AGENT)
        config = configparser.RawConfigParser()
        config.read(os.path.join(os.environ['HOME'], '.mwclient_login_rc'))
        self.__site__.login(config.get('login', 'user'),
                            config.get('login', 'pass'))

        # category
        self.__category__ = category

        # images
        self.__images_path__ = path
        self.__images__ = os.listdir(self.__images_path__)

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

    def descriptions(self):
        """Retrive descriptions and dumps it in cache file"""
        s = Sickle(self.__url_api__)
        records = [record for record in s.ListRecords(metadataPrefix='oai_dc')]
        descr = OrderedDict()
        subjects = OrderedDict()
        cats = []
        for record in records:
            item = record.metadata['source'][0].split(',')[1].strip()
            descr[item] = record.metadata
            self.__log__.info('%s', item)
            if 'subject' in record.metadata:
                item_subjects = record.metadata['subject']
                for t in item_subjects:
                    if t in subjects:
                        subjects[t] = subjects[t] + 1
                    else:
                        subjects[t] = 1
                        cats.append(self.subject_to_category(t))
            else:
                self.__log__.warning('  no subject for %s', item)
        self.__log__.info('Parsed %s items', len(records))
        self.__log__.info('Subjects: %s', json.dumps(subjects, indent=2))
        for cat in cats:
            self.__log__.info('  [[%s]]', cat)
            page = self.__site__.pages[cat]
            if not page.exists:
                page.save('[[{}]]'.format(self.__category__), 'Upload cat')
        self.__log__.info('Dumping metadata %s', self.__cache_meta__)
        with open(self.__cache_meta__, 'w') as f:
            json.dump(descr, f, indent=4, ensure_ascii=False)

    def subject_to_category(self, subject):
        return '{} - {}'.format(self.__category__, subject)

    def mapping(self):
        """From descriptions generate mapping of descriptions and files."""
        with open(self.__cache_meta__, 'r') as f:
            items = json.load(f)
            descr = {
                item: self.item_mapping(item, items[item])
                for item in items
            }
            with open(self.__cache_descr__, 'w') as cache:
                self.__log__.info(
                    'Dumping descriptions %s',
                    self.__cache_descr__)
                json.dump(descr, cache, indent=4, ensure_ascii=False)

    def item_mapping(self):
        return None

    def upload_images(self):
        uploads = OrderedDict()
        with open(self.__cache_descr__, 'r') as f_descr, open(self.__cache_meta__, 'r') as f_meta:
            descriptions = json.load(f_descr)
            metadata = json.load(f_meta)
            for item in descriptions:
                fonds_number, file_number = item.split('Fi')
                self.__log__.info('%s %s', fonds_number, file_number)
                img = self.image(fonds_number, file_number)
                if img:
                    uploads[item] = {
                        'description': descriptions[item],
                        'title': ';'.join(
                            metadata[item]['title']) \
                                                    .replace('[', '') \
                                                    .replace(']', '') \
                                                    .replace('&quot;', '') \
                                                    .replace('&amp;', '')[0:200] + ' - ' + img,
                        'file': os.path.join(self.__images_path__, img)
                    }
        for item in uploads:
            upload = uploads[item]
            page = self.__site__.pages['File:' + upload['title']]
            if page.exists:
                self.__log__.info('Skipping %s', upload['title'])
            else:
                self.__log__.info('Uploading %s', upload['title'])
                img = open(upload['file'], 'rb')
                self.__site__.upload(img, filename=upload['title'], description=upload['description'])


    def image(self, fonds_number, file_number):
        regexp = 'FRAC31555_' + fonds_number + 'Fi' + '0*' + file_number.replace('/', '_0*') + '(\.|_)'
        for i in self.__images__:
            if re.match(regexp, i):
                self.__log__.info('  found %s for %sFi%s',
                    i,
                    fonds_number,
                    file_number)
                return i

    def run(self):
        if not os.path.exists(self.__cache_meta__):
            self.descriptions()
        self.mapping()
        self.upload_images()

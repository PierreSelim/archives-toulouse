from collections import OrderedDict

from archivestls.collection import DublinCoreCollectionBot, __is_class__


OAI_URL = 'http://basededonnees.archives.toulouse.fr:81/4DCGI/oaipmh?verb=listrecords&set=IMAGE:images_dp_archeologie'


description_template = """
{{{{Artwork
|ID={{{{Archives municipales de Toulouse - FET link|{item}}}}}
|artist={artist}
|credit line=
|date={date}
|location=
|description={description}
|dimensions=
|gallery={{{{Institution:Archives municipales de Toulouse}}}}
|medium={technique}
|object history=
|permission={{{{PD-old|PD-70}}}}
|references=
|source={{{{Pile et Face - Archives municipales de Toulouse}}}}
|title={{{{fr|{title}}}}}
}}}}
{cats}"""


def join_metadata(field):
    return '\n'.join(field)


def parse_format(fmt):
    techniques = [t for t in fmt if t != 'image/jpeg']
    return join_metadata(techniques)


def wiki_link(s):
    return '[[{}]]'.format(s)


class Jna2018Bot(DublinCoreCollectionBot):

    def item_mapping(self, item, metadata):
        title = join_metadata(metadata['title'])
        if '[' in title:
            title = title.replace('[', '').replace(']', '')
            title = 'Titre inconnu; {}'.format(title)
        cats = [wiki_link(self.__category__)]
        kwargs = {
            'item': item,
            'title': title,
            'date': '',
            'artist': 'Inconnu',
            'description': join_metadata(metadata['description']),
            'technique': parse_format(metadata['format']),
        }
        # author
        if 'creator' in metadata:
            kwargs['artist'] = join_metadata(metadata['creator'])
        # date
        if 'date' in metadata:
            kwargs['date'] = join_metadata(metadata['date'])
        if 'subject' in metadata:
            for s in metadata['subject']:
                cats.append(wiki_link(self.subject_to_category(s)))
        kwargs['cats'] = join_metadata(cats)
        return description_template.format(**kwargs)


def main():
    bot = Jna2018Bot(name='jna2018',
                     url=OAI_URL,
                     category='Category:Pile et Face - Archives municipales de Toulouse',
                     path='/home/pierre-selim/Images/jna2018/jpeg')
    bot.run()


if __name__ == '__main__':
    main()

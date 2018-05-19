import os
import unittest

from requests_html import HTML

from archivestls import collection


DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class TestCollection(unittest.TestCase):

    def test_metadata(self):
        response_html_file = os.path.join(DIRECTORY, 'response.html')
        with open(response_html_file, 'r') as f:
            content = HTML(html=f.read())
            metadata = collection.__metadata__(content)
            self.assertIn('Auteur(s)', metadata)
            self.assertEqual(
                metadata['Auteur(s)'],
                'JEANSOU, Henri JANSOU dit [ Auteur ]')


if __name__ == '__main__':
    unittest.main()

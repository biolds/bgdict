import json
import re
from django.core.management.base import BaseCommand, CommandError

from ui.models import Word
from ui.views import unaccentify


class Command(BaseCommand):
    help = 'Import a dictionary in json format'

    def add_arguments(self, parser):
        parser.add_argument('json_dict', type=str)

    def handle(self, *args, **options):
        with open(options['json_dict'], 'r') as f:
            buf = json.load(f)

        Word.objects.all().delete()
        i = 0
        for word, trans in buf.items():
            if word.startswith('#'):
                continue
            # strip html headers
            trans = re.sub('<html>.*<body>', '', trans)
            trans = trans.replace('</body></html>', '')
            match = re.finditer(r'<li class="quote">([^<]+)', trans)
            text = []
            for t in match:
                text += [t.group(1)]
            trans_text = unaccentify(' '.join(text))
            Word.objects.create(word=word, trans_html=trans, trans_text=trans_text)

            i += 1
            if i % 100 == 0:
                print('%0.02f %%' % (float(i) / len(buf) * 100))
        self.stdout.write(self.style.SUCCESS('%s words imported successfuly' % Word.objects.count()))

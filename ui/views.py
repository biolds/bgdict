from datetime import datetime
import unicodedata
from urllib.parse import quote

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django import forms

from .models import Word


class SearchForm(forms.Form):
    search = forms.CharField(max_length=1024)



# based on https://stackoverflow.com/questions/35942129/remove-accent-marks-from-characters-while-preserving-other-diacritics
ACCENT_MAPPING = {
    'а́': 'а',
    'а̀': 'а',
    'е́': 'е',
    'ѐ': 'е',
    'и́': 'и',
    'ѝ': 'и',
    'о́': 'о',
    'о̀': 'о',
    'у́': 'у',
    'у̀': 'у',
    'ы́': 'ы',
    'ы̀': 'ы',
    'э́': 'э',
    'э̀': 'э',
    'ю́': 'ю',
    '̀ю': 'ю',
    'я́́': 'я',
    'я̀': 'я',
}
ACCENT_MAPPING = {unicodedata.normalize('NFKC', i): j for i, j in ACCENT_MAPPING.items()}


def unaccentify(s):
    source = unicodedata.normalize('NFKC', s)
    for old, new in ACCENT_MAPPING.items():
        source = source.replace(old, new)
    return source


def index(request):
    form = SearchForm(request.GET)
    full = request.GET.get('full') != 'false'
    nostat = request.GET.get('nostat') == 'true'

    context = {
        'form': form,
        'full': full
    }

    if form.is_valid():
        search = unaccentify(form.cleaned_data['search'])
        vectors = SearchVector('trans_text', config='bulgarian') + SearchVector('word', config='bulgarian')
        query = SearchQuery(search, config='bulgarian')
        words = Word.objects.annotate(rank=SearchRank(vectors, query)).filter(rank__gt=0.05).order_by('-rank')[:5]

        if len(words) == 0:
            words = Word.objects.annotate(rank=SearchRank(vectors, query)).exclude(rank=0).order_by('-rank')[:5]

        if len(words) == 0:
            words = Word.objects.filter(trans_text__iregex=r'\y%s\y' % search)[:5]

        count = words.count()
        if count:
            msg = '%i match.' % count
        else:
            msg = 'No result.'

        if not nostat:
            for w in words:
                if w.last_seen is None or w.last_seen.date() != datetime.today():
                    w.views += 1
                w.last_seen = timezone.now()
                w.save()

        if unicodedata.name(search.strip()[0]).startswith('CYRILLIC'):
            dict_link = 'https://www.dict.com/?t=bg&set=_bgen&w='
        else:
            dict_link = 'https://www.dict.com/?t=bg&set=_enbg&w='
        dict_link += quote(search)

        context.update({
            'results': words,
            'msg': msg,
            'search': search,
            'dict_link': dict_link
        })
    else:
        last_seen = Word.objects.exclude(last_seen__isnull=True).order_by('-last_seen')[:5]
        top = Word.objects.exclude(views=0).order_by('-views', '-last_seen')[:5]
        favorite = Word.objects.exclude(last_seen__isnull=True).filter(favorite=True).order_by('-last_seen')[:5]
        context['panels'] = [{
            'title': 'Last seen',
            'words': last_seen
        }, {
            'title': 'Favorite',
            'words': favorite
        }, {
            'title': 'Top',
            'words': top
        }]

    return render(request, 'ui/index.html', context)


def favorite(request, fav_id):
    w = get_object_or_404(Word, pk=fav_id)
    w.favorite = not w.favorite
    w.save()
    
    to = request.META.get('HTTP_REFERER', None)
    if to:
        if not 'nostat=true' in to:
            if '?' in to:
                to += '&'
            else:
                to += '?'
            to += 'nostat=true'
    else:
        to = '/'
    return redirect(to)

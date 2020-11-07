from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django import forms

from .models import Word


class SearchForm(forms.Form):
    search = forms.CharField(max_length=1024)


def index(request):
    form = SearchForm(request.GET)
    full = request.GET.get('full') != 'false'
    nostat = request.GET.get('nostat') == 'true'

    context = {
        'form': form,
        'full': full
    }

    if form.is_valid():
        search = form.cleaned_data['search']
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
                w.last_seen = timezone.now()
                w.views += 1
                w.save()

        context.update({
            'results': words,
            'msg': msg,
            'search': search
        })
    else:
        last_seen = Word.objects.exclude(last_seen__isnull=True).order_by('-last_seen')[:5]
        top = Word.objects.order_by('-views', '-last_seen')[:5]
        favorite = Word.objects.filter(favorite=True).order_by('-last_seen')[:5]
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

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
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
        words = Word.objects.filter(trans_text__search=search)
        words = words | Word.objects.filter(word__search=search)
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
            'msg': msg
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

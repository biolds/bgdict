from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe


class Word(models.Model):
    word = models.CharField(max_length=255)
    trans_html = models.TextField()
    trans_text = models.TextField()

    last_seen = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    favorite = models.BooleanField(default=False)

    def to_html(self):
        html = '<a class="favorite" style="color: #f00; float: right;" href="%s">' % reverse('favorite', args=(self.pk,))
        if hasattr(self, 'rank'):
            html += '%0.1f' %  self.rank + ' '
        if self.favorite:
            html += '♥'
        else:
            html += '♡'
        html += '</a>'
        html += self.trans_html
        return mark_safe(html)

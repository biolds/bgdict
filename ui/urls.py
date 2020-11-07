from django.conf.urls import url
from .views import index

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ui/', include('ui.urls'),
]

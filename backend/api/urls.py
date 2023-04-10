from django.urls import include, path
from django.views.generic import TemplateView

from .v1 import urls as v1_urls

urlpatterns = [
    path('v1/', include(v1_urls)),
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='docs'
    ),
]

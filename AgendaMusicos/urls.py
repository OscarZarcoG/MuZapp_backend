from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/user/', include('AUTH.urls')),
    path('api/agenda/', include('GIGS.urls')),
    path('api/mexico/', include('MEXICO.urls')),
]

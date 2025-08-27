from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'MEXICO'

router = DefaultRouter()
router.register(r'colonias', views.ColoniaViewSet)
router.register(r'estados', views.EstadoViewSet)
router.register(r'municipios', views.MunicipioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('colonias/codigo_postal/<str:codigo_postal>/', views.buscar_por_codigo_postal, name='buscar-por-codigo-postal'),
    path('colonias/municipio/<int:municipio_id>/', views.buscar_colonias_por_municipio, name='buscar-colonias-por-municipio'),
]
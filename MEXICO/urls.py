from django.urls import path
from . import views

app_name = 'MEXICO'

urlpatterns = [
    # Endpoint principal para buscar por código postal
    path('codigo-postal/<str:codigo_postal>/', 
         views.buscar_por_codigo_postal, 
         name='buscar_codigo_postal'),
    
    # Endpoints para colonias
    path('colonias/', 
         views.ColoniaListView.as_view(), 
         name='colonia_list'),
    
    path('colonias/<int:pk>/', 
         views.ColoniaDetailView.as_view(), 
         name='colonia_detail'),
    
    path('colonias/municipio/<int:municipio_id>/', 
         views.buscar_colonias_por_municipio, 
         name='colonias_por_municipio'),
    
    # Endpoints para estados
    path('estados/', 
         views.EstadoListView.as_view(), 
         name='estado_list'),
    
    # Endpoints para municipios
    path('municipios/', 
         views.MunicipioListView.as_view(), 
         name='municipio_list'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    path('panel-control/', views.panel_control, name='panel_control'),

    # Racks
    path('crear-rack/', views.crear_rack, name='crear_rack'),
    path('editar-rack/', views.editar_rack, name='editar_rack'),
    path('eliminar-rack/', views.eliminar_rack, name='eliminar_rack'),

    # Niveles
    path('crear-nivel/', views.crear_nivel, name='crear_nivel'),
    path('editar-nivel/', views.editar_nivel, name='editar_nivel'),
    path('eliminar-nivel/', views.eliminar_nivel, name='eliminar_nivel'),

    # Secciones y ubicaciones
    path('crear-seccion/', views.crear_seccion, name='crear_seccion'),
    path('eliminar-seccion/', views.eliminar_seccion, name='eliminar_seccion'),
    path('crear-ubicacion/', views.crear_ubicacion, name='crear_ubicacion'),

    # Proveedores
    path('crear-proveedor/', views.crear_proveedor, name='crear_proveedor'),

    # AJAX
    path('get-niveles-por-rack/', views.get_niveles_por_rack, name='get_niveles_por_rack'),
    path('get-secciones-por-nivel/', views.get_secciones_por_nivel, name='get_secciones_por_nivel'),
    path('get-info-rack/<int:rack_id>/', views.get_info_rack, name='get_info_rack'),
    # Proxy backend para OpenRouter: evita exponer la API key en el frontend
    path('api/openrouter_proxy/', views.openrouter_proxy, name='openrouter_proxy'),

    # Eliminar todo
    path('eliminar-todo/', views.eliminar_todo, name='eliminar_todo'),
    

]

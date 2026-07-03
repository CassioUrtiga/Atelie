from django.urls import path

from .views import (
    inicial_view, dashboard_view, cadastrar_usuario_view, login_view, 
    logout_view, cadastrar_pedido_view, excluir_pedido_view, album_view,
)

urlpatterns = [
    path('', inicial_view, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='deslogar'),
    path('cadastrar/', cadastrar_usuario_view, name= 'cadastrar'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('pedido/', cadastrar_pedido_view, name='pedido'),
    path('excluir-pedido/<int:id>/', excluir_pedido_view, name='excluir-pedido'),
    path('album/<int:id>/', album_view, name='album'),
]

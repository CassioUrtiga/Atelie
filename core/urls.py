from django.urls import path

from .views import (
    inicial_view, dashboard_view, cadastrar_usuario_view, login_view, 
    logout_view, cadastrar_pedido_view, excluir_pedido_view, album_pedido_view,
    gerenciador_view, editar_pedido_view, cancelar_pedido_view, 
    gerar_relatorio 
)

urlpatterns = [
    path('', inicial_view, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='deslogar'),
    path('cadastrar/', cadastrar_usuario_view, name= 'cadastrar'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('pedido/', cadastrar_pedido_view, name='pedido'),
    path('excluir-pedido/<int:id>/', excluir_pedido_view, name='excluir-pedido'),
    path('album/<int:id>/', album_pedido_view, name='album'),
    path('gerenciar/', gerenciador_view, name='gerenciar'),
    path('editar-pedido/<int:id>/', editar_pedido_view, name='editar-pedido'),
    path('cancelar-pedido/<int:id>/', cancelar_pedido_view, name='cancelar-pedido'),
    path('relatorio/', gerar_relatorio, name='relatorio'),
]

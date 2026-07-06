import base64
import re
import requests
import tempfile
from functools import reduce
from io import BytesIO
from datetime import datetime, date, timedelta
from PIL import Image

from django.http import HttpResponseNotFound
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile

from .forms import CadastroCliente, CadastroPedido
from .models import Cliente, Administrador, Servico, Pedido, ImagemPedido


# Views
def inicial_view(request):
    return render(request, 'inicial.html')
    
def login_view(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorreta')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('inicio')

def cadastrar_usuario_view(request):
    if request.method == "POST":
        form_cliente = CadastroCliente(request.POST)
        
        if form_cliente.is_valid():
            username = form_cliente.data['username']
            senha = form_cliente.data['senha']
            
            if User.objects.filter(username=username).exists():

                messages.warning(request, f'Usuário {username} já existe!')

                return render(request, 'cadastro_usuario.html', {'form': form_cliente})
            else:
                user = User.objects.create_user(username=username, password=senha)
                cliente = form_cliente.save(commit=False)

                cliente.user = user
                cliente.nome = form_cliente.data['nome']
                cliente.sexo = form_cliente.data['sexo']
                cliente.telefone = form_cliente.data['telefone']

                user.save()
                cliente.save()
                
                messages.success(request, 'Cadastro realizado com sucesso!')
                return redirect('login') 
        else:
            messages.error(request, 'Formulário inválido!')

            return render(request, 'cadastro_usuario.html', {'form': CadastroCliente()})     
    else:
        return render(request, 'cadastro_usuario.html', {'form': CadastroCliente()})

@login_required(login_url='login')
def dashboard_view(request):
    is_cliente = hasattr(request.user, 'cliente')

    if is_cliente:
        nome_completo = request.user.cliente.nome.lower()
        pedidos = Pedido.objects.filter(cliente=request.user.cliente)
        pedidos_filtrados = {'isEmpty': True, 'dados': ''}

        # Filtro de pedidos
        if request.method == "POST":
            filtro_pedidos = [int(valor) for valor in request.POST.getlist('status_filtros')]
            
            if filtro_pedidos:
                request.session['filtros_pedidos'] = filtro_pedidos
            else:
                request.session.pop('filtros_pedidos', None)
            
            return redirect('dashboard')
    
        filtros_salvos = request.session.get('filtros_pedidos')
        
        if filtros_salvos and (10 not in filtros_salvos):
            pedidos_filtrados['isEmpty'] = False
            pedidos_filtrados['dados'] = Pedido.objects.filter(
                cliente=request.user.cliente, 
                status__in=filtros_salvos
            )
        else:
            # Marcar o checkbox (todos)
            filtros_salvos = [10]
            request.session['filtros_pedidos'] = [10]
            pedidos_filtrados['isEmpty'] = True
        
        # Formatação do nome
        partes = nome_completo.split()
        conectores = ['de', 'da', 'do', 'das', 'dos', 'e']

        if len(partes) > 2 and partes[1].lower() in conectores:
            nome_resumido = " ".join(partes[:3])
        else:
            nome_resumido = " ".join(partes[:2])

        context = {
            'isCliente': is_cliente,
            'nome': nome_resumido,
            'telefone': request.user.cliente.telefone,
            'sexo': request.user.cliente.sexo,
            'qtde_servico': Servico.objects.count(),
            'form': CadastroPedido(),
            'pedidos': pedidos if pedidos_filtrados['isEmpty'] else pedidos_filtrados['dados'],
            'filtros_salvos': filtros_salvos,
        }
    else:
        context = {
            'isCliente': is_cliente,
            'nome': request.user.administrador.nome,
            'telefone': request.user.administrador.telefone
        }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def cadastrar_pedido_view(request):   
    form_pedido = CadastroPedido(request.POST)
    
    if form_pedido.is_valid():
        pedido = form_pedido.save(commit=False)
        pedido.cliente = request.user.cliente
        pedido.save()

        # Salva as imagens
        imagens_invalidas = 0
        total_imagens = 0

        try:
            imagens_lista = request.FILES.getlist('image')
            for index, imagem in enumerate(imagens_lista):
                total_imagens += 1
                try:
                    # Validação de tamanho: 1MB = 1024 * 1024 bytes
                    if imagem.size > 1048576:
                        imagens_invalidas += 1
                        continue

                    with Image.open(imagem) as img_teste:
                        img_teste.verify()
                    
                    nova_imagem_objeto = ImagemPedido()
                    nova_imagem_objeto.img.save(imagem.name, imagem)
                
                    pedido.img.add(nova_imagem_objeto)
                except Exception:
                    imagens_invalidas += 1
        except Exception as e:
            messages.error(request, 'Problema no envio da imagem!')
            return redirect('dashboard')
        
        # Cenário A: Todas as imagens enviadas eram inválidas
        if total_imagens == imagens_invalidas > 0:
            if imagens_invalidas == 1:
                msg = "Pedido realizado, mas a imagem enviada era inválida!"
            else:
                msg = "Pedido realizado, mas as imagens enviadas eram inválidas!"

            messages.info(request, msg)
            return redirect('dashboard')
        
        # Cenário B: Teve mistura (algumas válidas, algumas inválidas)
        if imagens_invalidas > 0:
            form_pedido.save_m2m()
            imagens_validas = total_imagens - imagens_invalidas

            msg_validas = pluralizar(imagens_validas, "imagem aceita", "imagens aceitas")
            msg_invalidas = pluralizar(imagens_invalidas, "inválida", "inválidas")

            messages.info(request, f'Pedido realizado! {msg_validas} e {msg_invalidas}.')
            return redirect('dashboard')
        
        # Cenário C: 100% de sucesso (todas válidas)
        if imagens_invalidas == 0:
            form_pedido.save_m2m()
        
        messages.success(request, 'Novo pedido realizado!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Dados inválidos ou incompletos!')
        return redirect('dashboard')

@login_required(login_url='login')
def excluir_pedido_view(request, id):
    cliente = request.user.cliente

    pedido = get_object_or_404(Pedido, id=id, cliente=cliente)
    pedido.delete()

    messages.success(request, 'Pedido excluído!')
    return redirect('dashboard')

@login_required(login_url='login')
def album_pedido_view(request, id):
    cliente = request.user.cliente
    pedido = get_object_or_404(Pedido, id=id, cliente=cliente)

    context = {
        'nome': cliente.nome.split()[0],
        'sexo': cliente.sexo,
        'pedido_id': id,
        'fotos': pedido.img.all,
    }

    return render(request, 'album.html', context)


def pluralizar(quantidade, singular, plural):
    return f"{quantidade} {singular}" if quantidade == 1 else f"{quantidade} {plural}"


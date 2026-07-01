import base64
import re
import requests
import tempfile
from functools import reduce
from io import BytesIO
from datetime import datetime, date, timedelta

from django.http import HttpResponseNotFound
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from PIL import Image

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
            
            # Realiza o cadastro do cliente 
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
        context = {
            'isCliente': is_cliente,
            'nome': request.user.cliente.nome,
            'telefone': request.user.cliente.telefone,
            'qtde_servico': Servico.objects.count(),
            'form': CadastroPedido(),
            'pedidos': Pedido.objects.filter(cliente=request.user.cliente)
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
        imagens_lista = request.POST.getlist('image')

        try:
            for index, imagem in enumerate(imagens_lista):
                if not imagem:
                    continue
                    
                imagem_decodificada = decode_base64_image(imagem)
                
                with tempfile.NamedTemporaryFile(suffix='.jpeg', delete=False) as temp_file:
                    imagem_decodificada.save(temp_file, format='JPEG')
                    temp_file.seek(0)
                    file_content = temp_file.read()
                
                content_file = ContentFile(file_content)
                nova_imagem_objeto = ImagemPedido()
                nova_imagem_objeto.img.save(temp_file.name, content_file)
                
                pedido.img.add(nova_imagem_objeto)
        except Exception as e:
            messages.error(request, 'ERRO! ao processar a imagem.')
            return redirect('dashboard')
        
        form_pedido.save_m2m()
        
        messages.success(request, 'Pedido realizado com sucesso!')
        return redirect('dashboard')
    else:
        messages.error(request, 'ERRO! dados inválidos ou incompletos')
        return redirect('dashboard')    


def decode_base64_image(base64_string):
    encoded_data = base64_string.split(',')[1]
    image_data = base64.b64decode(encoded_data)
    image = Image.open(BytesIO(image_data))
    return image

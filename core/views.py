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

from .forms import CadastroCliente
from .models import Cliente, Proprietario


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
        nome = request.user.cliente.nome
        telefone = request.user.cliente.telefone
    else:
        nome = request.user.proprietario.nome 
        telefone = request.user.proprietario.telefone

    context = {
        'isCliente': is_cliente,
        'nome': nome,
        'telefone': telefone
    }
    
    return render(request, 'dashboard.html', context)
        
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Case, Value, When
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .forms import CadastroCliente, CadastroPedido
from .models import Cliente, Administrador, Servico, Pedido, ImagemPedido, Roupa, Tecido


# Funções
def eh_cliente(user):
    if user.is_authenticated and hasattr(user, 'cliente'):
        return True
    raise PermissionDenied

def eh_administrador(user):
    if user.is_authenticated and hasattr(user, 'administrador'):
        return True
    raise PermissionDenied

def pluralizar(quantidade, singular, plural):
    return f"{quantidade} {singular}" if quantidade == 1 else f"{quantidade} {plural}"


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
    pedidos_filtrados = {'isEmpty': True, 'dados': ''}
    clientes_filtrados = {'isEmpty': True, 'dados': ''}

    if is_cliente:
        # Filtros
        if request.method == "POST":
            if "filtrar_pedidos" in request.POST:
                filtro_pedidos = request.POST.getlist('status_filtro_pedidos')
                
                if filtro_pedidos:
                    request.session['filtros_pedidos'] = filtro_pedidos
                else:
                    request.session.pop('filtros_pedidos', None)
            
            return redirect('dashboard')
        else:
            filtros_pedidos_salvos = request.session.get('filtros_pedidos')
            
            # lógica de filtro de pedidos
            if filtros_pedidos_salvos and ('todos' not in filtros_pedidos_salvos):
                pedidos_filtrados['isEmpty'] = False
                pedidos_filtrados['dados'] = Pedido.objects.filter(
                    cliente=request.user.cliente, 
                    status__in=filtros_pedidos_salvos
                )
            else:
                filtros_pedidos_salvos = ['todos']
                request.session['filtros_pedidos'] = ['todos']
                pedidos_filtrados['isEmpty'] = True
        
        # Formatação do nome
        partes = request.user.cliente.nome.lower().split()
        conectores = ['de', 'da', 'do', 'das', 'dos', 'e']

        if len(partes) > 2 and partes[1].lower() in conectores:
            nome_resumido = " ".join(partes[:3])
        else:
            nome_resumido = " ".join(partes[:2])

        # Base de pedidos (filtrados ou todos)
        if pedidos_filtrados['isEmpty']:
            pedidos_base = Pedido.objects.filter(cliente=request.user.cliente)
        else:
            pedidos_base = pedidos_filtrados['dados']

        context = {
            'isCliente': is_cliente,
            'nome': nome_resumido,
            'telefone': request.user.cliente.telefone,
            'sexo': request.user.cliente.sexo,
            'qtd_servicos': Servico.objects.filter(disponivel=True).count(),
            'qtd_roupas': Roupa.objects.filter(disponivel=True).count(),
            'qtd_tecidos': Tecido.objects.filter(disponivel=True).count(),
            'form': CadastroPedido(),
            'pedidos': pedidos_base.order_by(Case(
                When(status='andamento', then=Value(1)),
                When(status='recebido', then=Value(2)),
                When(status='pago', then=Value(3)),
                When(status='concluido', then=Value(4)),
                When(status='cancelado', then=Value(5)),
                default=Value(6)
            )),
            'filtros_pedidos': filtros_pedidos_salvos,
            'pedidos_com_servicos_indisponiveis': list(Pedido.objects.filter(servico__disponivel=False).distinct().values_list('id', flat=True)),
        }
    else:
        # Filtros
        if request.method == "POST":
            if "filtrar_pedidos" in request.POST:
                filtro_pedidos = request.POST.getlist('status_filtro_pedidos')
                
                if filtro_pedidos:
                    request.session['filtros_pedidos'] = filtro_pedidos
                else:
                    request.session.pop('filtros_pedidos', None)
            
            if "filtrar_clientes" in request.POST:
                filtro_clientes = request.POST.getlist('status_filtro_clientes')
                
                if filtro_clientes:
                    request.session['filtros_clientes'] = filtro_clientes
                else:
                    request.session.pop('filtros_clientes', None)
            
            return redirect('dashboard')
        else:
            filtros_pedidos_salvos = request.session.get('filtros_pedidos')
            filtros_clientes_salvos = request.session.get('filtros_clientes')
            
            # lógica de filtro de pedidos
            if filtros_pedidos_salvos and ('todos' not in filtros_pedidos_salvos):
                pedidos_filtrados['isEmpty'] = False
                pedidos_filtrados['dados'] = Pedido.objects.filter(
                    status__in=filtros_pedidos_salvos
                )
            else:
                filtros_pedidos_salvos = ['todos']
                request.session['filtros_pedidos'] = ['todos']
                pedidos_filtrados['isEmpty'] = True
            
            # lógica de filtro de clientes
            if filtros_clientes_salvos and ('todos' not in filtros_clientes_salvos):
                ids_inteiros = [int(id_str) for id_str in filtros_clientes_salvos]
                clientes_filtrados['isEmpty'] = False
                clientes_filtrados['dados'] = Cliente.objects.filter(
                    id__in=ids_inteiros
                )
            else:
                filtros_clientes_salvos = ['todos']
                request.session['filtros_clientes'] = ['todos']
                clientes_filtrados['isEmpty'] = True

        # Base de pedidos (filtrados ou todos)
        if pedidos_filtrados['isEmpty']:
            pedidos_base = Pedido.objects.all()
        else:
            pedidos_base = pedidos_filtrados['dados']

        # Se houver clientes filtrados, refina a base de pedidos
        if not clientes_filtrados['isEmpty']:
            pedidos_base = pedidos_base.filter(cliente__in=clientes_filtrados['dados'])

        context = {
            'isCliente': is_cliente,
            'nome': request.user.administrador.nome,
            'telefone': request.user.administrador.telefone,
            'pedidos': pedidos_base.order_by(Case(
                When(status='recebido', then=Value(1)),
                When(status='andamento', then=Value(2)),
                When(status='pago', then=Value(3)),
                When(status='concluido', then=Value(4)),
                When(status='cancelado', then=Value(5)),
                default=Value(6)
            )),
            'clientes': Cliente.objects.all().order_by('nome'),
            'filtros_pedidos': filtros_pedidos_salvos,
            'filtros_clientes': filtros_clientes_salvos,
            'servicos': Servico.objects.all(),
            'servicos_indisponiveis': Servico.objects.filter(disponivel=False),
            'roupas': Roupa.objects.all(),
            'roupas_indisponiveis': Roupa.objects.filter(disponivel=False),
            'tecidos': Tecido.objects.all(),
            'tecidos_indisponiveis': Tecido.objects.filter(disponivel=False),
            'pedidos_com_servicos_indisponiveis': list(Pedido.objects.filter(servico__disponivel=False).distinct().values_list('id', flat=True)),
        }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
@user_passes_test(eh_cliente)
def cadastrar_pedido_view(request):   
    form_pedido = CadastroPedido(request.POST)
    
    if form_pedido.is_valid():
        pedido = form_pedido.save(commit=False)
        pedido.cliente = request.user.cliente
        pedido.save()

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
    is_cliente = hasattr(request.user, 'cliente')

    if is_cliente:
        cliente = request.user.cliente
        pedido = get_object_or_404(Pedido, id=id, cliente=cliente)
    else:
        pedido = get_object_or_404(Pedido, id=id)
        cliente = pedido.cliente

    context = {
        'nome': cliente.nome.split()[0],
        'sexo': cliente.sexo,
        'pedido_id': id,
        'fotos': pedido.img.all,
    }

    return render(request, 'album.html', context)

@login_required(login_url='login')
@user_passes_test(eh_administrador)
def gerenciador_view(request):
    lista_servicos = [s.strip().capitalize() for s in request.POST.get('servicos').split(',') if s.strip()]

    lista_roupas = [s.strip().capitalize() for s in request.POST.get('roupas').split(',') if s.strip()]

    lista_tecidos = [s.strip().capitalize() for s in request.POST.get('tecidos').split(',') if s.strip()]

    # ------------SERVIÇO---------------
    Servico.objects.filter(servico__in=lista_servicos).update(disponivel=True)
    Servico.objects.exclude(servico__in=lista_servicos).update(disponivel=False)
    servicos_existentes = Servico.objects.filter(servico__in=lista_servicos).values_list('servico', flat=True)

    for novo_servico in lista_servicos:
        if novo_servico not in servicos_existentes:
            Servico.objects.create(servico=novo_servico, disponivel=True)
    
    # ------------ROUPA---------------
    Roupa.objects.filter(roupa__in=lista_roupas).update(disponivel=True)
    Roupa.objects.exclude(roupa__in=lista_roupas).update(disponivel=False)
    roupas_existentes = Roupa.objects.filter(roupa__in=lista_roupas).values_list('roupa', flat=True)

    for nova_roupa in lista_roupas:
        if nova_roupa not in roupas_existentes:
            Roupa.objects.create(roupa=nova_roupa, disponivel=True)
    
    # ------------TECIDO---------------
    Tecido.objects.filter(tecido__in=lista_tecidos).update(disponivel=True)
    Tecido.objects.exclude(tecido__in=lista_tecidos).update(disponivel=False)
    tecidos_existentes = Tecido.objects.filter(tecido__in=lista_tecidos).values_list('tecido', flat=True)

    for novo_tecido in lista_tecidos:
        if novo_tecido not in tecidos_existentes:
            Tecido.objects.create(tecido=novo_tecido, disponivel=True)


    messages.success(request, "Alterações aplicadas!")
    
    return redirect('dashboard')

@login_required(login_url='login')
@user_passes_test(eh_administrador)
def editar_pedido_view(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    
    try:
        status = request.POST.get('status')
        preco = request.POST.get('preco')
        obs = request.POST.get('observacao')

        pedido.status = status

        if obs:
            pedido.observacao = obs 

        if preco:
            pedido.preco = preco
                
        pedido.save()
        messages.success(request, f"Pedido (Nº{id}) foi atualizado!")
    except:
        messages.error(request, "Ocorreu um erro ao editar o pedido!")
    
    return redirect('dashboard')
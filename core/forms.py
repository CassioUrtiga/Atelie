from django import forms
from .models import Cliente, Pedido, Servico, Roupa, Tecido


class CadastroCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nome', 'username', 'senha', 'sexo', 'telefone')

    nome = forms.CharField(
        required=True, 
        max_length=100, 
        widget=forms.TextInput(attrs={
            'id': 'nome',
            'name': 'nome',
            'class': 'form-control',
            'placeholder': 'Nome completo',
        })
    )

    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'id': 'username',
        'class': 'form-control',
        'name': 'username',
        'placeholder': 'Nome de usuário'
    }))

    senha = forms.CharField(
        min_length=5, 
        max_length=12, 
        required=True, 
        widget=forms.PasswordInput(attrs={
            'id': 'input-senha',
            'type': 'password',
            'name': 'senha',
            'class': 'form-control',
            'placeholder': 'Sua senha'
        })
    )

    sexo = forms.ChoiceField(
        choices=[
            ('', 'Selecione o sexo'),
            ('F', 'Feminino'),
            ('M', 'Masculino'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'id': 'sexo',
            'class': 'form-control',
        })
    )

    telefone = forms.CharField(
        required=True,
        max_length=15,
        min_length=14,
        widget=forms.TextInput(attrs={
            'id': 'telefone',
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
        })
    )

class CadastroPedido(forms.ModelForm):

    servico = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.filter(disponivel=True),
        widget=forms.CheckboxSelectMultiple(),
        label="Serviços",
    )

    roupa = forms.ModelChoiceField(
        queryset=Roupa.objects.filter(disponivel=True),
        widget=forms.Select(attrs={'class': 'form-select w-auto'}),
        label="Roupas"
    )

    tecido = forms.ModelChoiceField(
        queryset=Tecido.objects.filter(disponivel=True),
        widget=forms.Select(attrs={'class': 'form-select w-auto'}),
        label="Tecidos"
    )
    
    class Meta:
        model = Pedido
        fields = ['servico', 'roupa', 'tecido', 'data_conclusao', 'detalhes']
    
        widgets = {
            'data_conclusao': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control w-auto'
            }),
            'detalhes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control', 
                'placeholder': 'Detalhes do pedido...'
            })
        }

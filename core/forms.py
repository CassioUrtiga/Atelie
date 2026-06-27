from django import forms
from .models import Cliente


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
            'placeholder': 'Seu nome',
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
            'id': 'senha',
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
        max_length=20,
        widget=forms.TextInput(attrs={
            'id': 'telefone',
            'class': 'form-control',
            'placeholder': '(xx) x-xxxxx-xxxx',
        })
    )
        
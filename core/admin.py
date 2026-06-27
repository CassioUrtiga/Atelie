from django.contrib import admin
from .models import Cliente, Proprietario

# Register your models here.
@admin.register(Cliente)
class ClienteModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'sexo', 'telefone')

    def username(self, obj):
        return obj.user.username
    
    username.short_description = 'Username'

@admin.register(Proprietario)
class ProprietarioModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'telefone')

    def username(self, obj):
        return obj.user.username
    
    username.short_description = 'Username'

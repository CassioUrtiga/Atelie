import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from stdimage.models import StdImageField
from django.dispatch import receiver
from django.db.models.signals import pre_delete


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, null=False)
    sexo = models.CharField(max_length=1, choices=[('F', 'Feminino'),('M', 'Masculino')], default='F')
    telefone = models.CharField(max_length=20, default='(xx) x-xxxxx-xxxx')

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    def __str__(self) -> str:
        return self.nome

class Proprietario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, null=False)
    telefone = models.CharField(max_length=20, default='(xx) x-xxxxx-xxxx')

    class Meta:
        verbose_name = 'proprietario'
        verbose_name_plural = 'proprietario'

    def __str__(self) -> str:
        return self.nome


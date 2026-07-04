import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from stdimage.models import StdImageField
from django.dispatch import receiver
from django.db.models.signals import pre_delete

def get_file_path_pedido(instance, filename):
    return os.path.join("img_pedidos", f"{uuid.uuid4()}.{filename.split('.')[-1]}")


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, null=False)
    sexo = models.CharField(max_length=1, choices=[('F', "Feminino"), ('M', "Masculino")], default='F')
    telefone = models.CharField(max_length=15, blank=False)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self) -> str:
        return self.nome

class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, null=False)
    telefone = models.CharField(max_length=15, blank=False)

    class Meta:
        verbose_name = "administrador"
        verbose_name_plural = "administradores"

    def __str__(self) -> str:
        return self.nome

class ImagemPedido(models.Model):
    img = StdImageField('Imagem do pedido', upload_to=get_file_path_pedido, blank=True, null=True, default=None)

    class Meta:
        verbose_name = "imagem"
        verbose_name_plural = "imagens"

    def __str__(self) -> str:
        return f"Imagem {self.id}"

class Servico(models.Model):
    servico = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "servico"
        verbose_name_plural = "servicos"

    def __str__(self) -> str:
        return self.servico

class Tecido(models.Model):
    tecido = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "tecido"
        verbose_name_plural = "tecidos"

    def __str__(self) -> str:
        return self.tecido

class Roupa(models.Model):
    roupa = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "roupa"
        verbose_name_plural = "roupas"

    def __str__(self) -> str:
        return self.roupa

class Pedido(models.Model):
    # Status Recebido  = 1
    # Status Andamento = 2
    # Status Concluído = 3
    # Status Cancelado = 4
    # Status Pago      = 11
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servico = models.ManyToManyField(Servico)
    roupa = models.ForeignKey(Roupa, on_delete=models.CASCADE)
    tecido = models.ForeignKey(Tecido, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField()
    detalhes = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True, default="")
    preco = models.CharField(max_length=10, default="")
    status = models.SmallIntegerField(default=1)
    img = models.ManyToManyField(ImagemPedido)
    
    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self) -> str:
        return f"Pedido {self.id} - {self.cliente.nome}"


@receiver(pre_delete, sender=Pedido)
def pedido_delete_img(sender, instance, **kwargs):
    imagens = list(instance.img.all())

    for imagem_obj in imagens:
        if imagem_obj.img and imagem_obj.img.path:
            if os.path.isfile(imagem_obj.img.path):
                try:
                    os.remove(imagem_obj.img.path)
                except OSError:
                    pass
        imagem_obj.delete()


from django.contrib import admin

from .models import Aluno, Cardapio, Fila, Atendimento

admin.site.register(Aluno)
admin.site.register(Cardapio)
admin.site.register(Fila)
admin.site.register(Atendimento)
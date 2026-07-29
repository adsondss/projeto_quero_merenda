from django.db import models


class Aluno(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome"
    )

    matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Matrícula"
    )

    turma = models.CharField(
        max_length=30,
        verbose_name="Turma"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Aluno ativo"
    )

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Cardapio(models.Model):
    data = models.DateField()

    descricao = models.CharField(
        max_length=200
    )

    observacao = models.TextField(
        blank=True
    )

    ativo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.data} - {self.descricao}"

class Fila(models.Model):

    STATUS_CHOICES = [
        ('AGUARDANDO', 'Aguardando'),
        ('ATENDIDO', 'Atendido'),
        ('DESISTIU', 'Desistiu'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        verbose_name="Aluno"
    )

    cardapio = models.ForeignKey(
    Cardapio,
    on_delete=models.CASCADE,
    verbose_name="Cardápio",
    null=True,
    blank=True
    )

    data = models.DateField(
        auto_now_add=True,
        verbose_name="Data"
    )

    horario_entrada = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Horário de entrada"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGUARDANDO',
        verbose_name="Status"
    )

    class Meta:
        verbose_name = "Fila"
        verbose_name_plural = "Fila"
        ordering = ["horario_entrada"]

    def __str__(self):
        return f"{self.aluno.nome} - {self.status}"

class Atendimento(models.Model):

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        verbose_name="Aluno"
    )

    cardapio = models.ForeignKey(
        Cardapio,
        on_delete=models.CASCADE,
        verbose_name="Cardápio"
    )

    horario_atendimento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Horário do atendimento"
    )

    class Meta:
        verbose_name = "Atendimento"
        verbose_name_plural = "Atendimentos"
        ordering = ["-horario_atendimento"]

    def __str__(self):
        return f"{self.aluno.nome} - {self.horario_atendimento.strftime('%d/%m/%Y %H:%M')}"
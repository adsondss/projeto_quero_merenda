import re

from datetime import date, timedelta, datetime

from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Aluno, Cardapio, Fila

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from datetime import timedelta

from django.http import HttpResponse

def pagina_inicial(request):

    # Busca o cardápio ativo
    hoje = date.today()

    # Define o padrão de matrícula do IFBA
    padrao_matricula = r"\d{5}[A-Z]+\d{4}"

    while True:

        # Verifica se o cardápio ativo é do dia de hoje
        cardapio = Cardapio.objects.filter(ativo=True).first()

        if cardapio != None and hoje > cardapio.data:
            cardapio.ativo = False
            cardapio.save()

        if cardapio == None or cardapio.ativo:
            break

    # Verifica se o formulário foi enviado
    if request.method == "POST":

        # Recebe os dados do formulário
        nome = request.POST.get("nome")
        turma = request.POST.get("turma")
        matricula = request.POST.get("matricula")

        # Verifica se todos os campos foram preenchidos
        if not nome or not turma or not matricula:
            messages.error(
                request,
                "Preencha todos os campos."
            )
            return redirect("inicio")

        # Verifica se a matrícula está no padrão do IFBA
        if not re.match(padrao_matricula, matricula):
            messages.error(
                request,
                "A matrícula está incorreta."
            )
            return redirect("inicio")

        # Remove espaços em branco
        nome = nome.strip()
        turma = turma.strip()
        matricula = matricula.strip()

        # Verifica se existe um cardápio ativo
        if cardapio is None:
            messages.error(
                request,
                "Não existe um cardápio ativo cadastrado para hoje."
            )
            return redirect("inicio")

        # Procura o aluno pela matrícula
        aluno, criado = Aluno.objects.get_or_create(
            matricula=matricula,
            defaults={
                "nome": nome,
                "turma": turma,
                "ativo": True
            }
        )

        # Atualiza os dados do aluno caso ele já exista
        if not criado:
            aluno.nome = nome
            aluno.turma = turma
            aluno.save()

        # Verifica se o aluno já está na fila hoje
        fila_existente = Fila.objects.filter(
            aluno=aluno,
            data=date.today(),
            status="AGUARDANDO"
        ).exists()

        if fila_existente:
            messages.error(
                request,
                "Você já está na fila da merenda hoje."
            )
            return redirect("inicio")

        # Cria a entrada na fila
        nova_fila = Fila.objects.create(
            aluno=aluno,
            cardapio=cardapio,
            status="AGUARDANDO"
        )

        messages.success(
            request,
            "Você entrou na fila com sucesso!"
        )

        # Redireciona para a tela de sucesso,
        # enviando o ID da entrada criada
        return redirect(
            "sucesso",
            fila_id=nova_fila.id
        )

    contexto = {
        "cardapio": cardapio,
        "padrao_matricula": padrao_matricula
    }

    return render(
        request,
        "merenda/index.html",
        contexto
    )


def sucesso(request, fila_id):

    fila = Fila.objects.get(
        id=fila_id
    )

    pessoas_na_frente = Fila.objects.filter(
        data=fila.data,
        status="AGUARDANDO",
        horario_entrada__lt=fila.horario_entrada
    ).count()

    contexto = {
        "fila": fila,
        "posicao": pessoas_na_frente + 1,
        "pessoas_na_frente": pessoas_na_frente
    }

    return render(
        request,
        "merenda/sucesso.html",
        contexto
    )

@login_required
def fila(request):

    alunos_fila = Fila.objects.filter(
        status="AGUARDANDO"
    ).order_by("horario_entrada")

    contexto = {
        "alunos_fila": alunos_fila
    }

    return render(
        request,
        "merenda/fila.html",
        contexto
    )

def atender(request, fila_id):

    fila = Fila.objects.get(id=fila_id)

    fila.status = "ATENDIDO"

    fila.save()

    return redirect("fila")

@login_required
def fila_json(request):

    alunos = Fila.objects.filter(
        status="AGUARDANDO"
    ).order_by("horario_entrada")

    dados = []

    for posicao, fila in enumerate(alunos, start=1):

        dados.append({

            "id": fila.id,
            "posicao": posicao,
            "nome": fila.aluno.nome,
            "turma": fila.aluno.turma,
            "hora": fila.horario_entrada.strftime("%H:%M")

        })

    return JsonResponse(dados, safe=False)

@login_required
def cardapio(request):

    hoje = date.today()

    if request.method == "POST":

        cardapio_id = request.POST.get("cardapio_id")
        
        data = request.POST.get("data")
        descricao = request.POST.get("descricao")
        observacao = request.POST.get("observacao")

        ativo = request.POST.get("ativo") == "on"

        if not data or not descricao:

            messages.error(
                request,
                "Preencha a data e a descrição."
            )

            return redirect("cardapio")

# ===================================
# EDITAR CARDÁPIO
# ===================================

        if cardapio_id:

            cardapio = Cardapio.objects.get(id=cardapio_id)

            cardapio.data = data
            cardapio.descricao = descricao
            cardapio.observacao = observacao
            cardapio.ativo = ativo

            cardapio.save()

            messages.success(
            request,
            "Cardápio atualizado com sucesso!"
            )

# ===================================
# NOVO CARDÁPIO
# ===================================

        else:

            cardapio, criado = Cardapio.objects.update_or_create(

                data=data,

                defaults={
                    "descricao": descricao,
                    "observacao": observacao,
                    "ativo": ativo,
                }

            )

            if criado:

                messages.success(
                    request,
                    "Cardápio cadastrado com sucesso!"
                )

            else:

                messages.success(
                    request,
                    "Cardápio atualizado com sucesso!"
                )

        return redirect("cardapio")

    ultimos_cardapios = Cardapio.objects.filter(
        data__gte=hoje - timedelta(days=6)
    ).order_by("-data")

    contexto = {

        "hoje": hoje,
        "ultimos_cardapios": ultimos_cardapios

    }

    return render(
        request,
        "merenda/cardapio.html",
        contexto
    )

@login_required
def painel(request):

    fila = Fila.objects.filter(

        status="AGUARDANDO"

    ).order_by(

        "horario_entrada"

    ).first()

    if fila is None:

        return render(

            request,

            "merenda/painel.html",

            {

                "fila": None,

                "cardapio": None,

                "posicao": 0,

                "total_aguardando": 0,

                "hora_atual": datetime.now()

            }

        )

    cardapio = fila.cardapio

    pessoas_na_frente = Fila.objects.filter(

        data=fila.data,

        status="AGUARDANDO",

        horario_entrada__lt=fila.horario_entrada

    ).count()

    total_aguardando = Fila.objects.filter(

        status="AGUARDANDO"

    ).count()

    return render(

        request,

        "merenda/painel.html",

        {

            "fila": fila,

            "cardapio": cardapio,

            "posicao": pessoas_na_frente + 1,

            "total_aguardando": total_aguardando,

            "hora_atual": datetime.now()

        }

    )

@login_required
def administracao(request):

    return render(
        request,
        "merenda/administracao.html"
    )
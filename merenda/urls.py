from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.pagina_inicial,
        name="inicio"
    ),

    path(
        "sucesso/<int:fila_id>/",
        views.sucesso,
        name="sucesso"
    ),

    path(
        "fila/",
        views.fila,
        name="fila"
    ),

    path(
        "atender/<int:fila_id>/",
        views.atender,
        name="atender"
    ),


    path(
        "fila/json/",
        views.fila_json,
        name="fila_json"
    ),

]
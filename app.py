import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime

from flask import Flask, abort, redirect, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect

app = Flask(__name__)
app.config["DATABASE"] = "petcare.db"

# A chave vem da variável de ambiente PETCARE_SECRET_KEY. Sem ela, uma chave
# aleatória é gerada a cada execução: funciona, mas formulários abertos antes
# de reiniciar o servidor deixam de ser aceitos.
app.config["SECRET_KEY"] = os.environ.get("PETCARE_SECRET_KEY") or secrets.token_hex(32)

csrf = CSRFProtect(app)

MSG_CSRF = (
    "Não foi possível confirmar a origem do formulário. "
    "Volte para a agenda e tente novamente."
)

TIPOS_CUIDADO = ("Vacina", "Consulta", "Medicamento", "Outro")
LIMITE_NOME_PET = 100
LIMITE_DESCRICAO = 500
FORMATO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


@contextmanager
def conectar_banco():
    """Abre a conexão com o banco e garante o fechamento.

    Se o bloco terminar sem erro, as alterações são gravadas (commit); se
    ocorrer uma exceção, são desfeitas (rollback). Em qualquer caso a
    conexão é fechada.
    """
    conexao = sqlite3.connect(app.config["DATABASE"])
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def criar_banco():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS cuidados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_pet TEXT NOT NULL,
                tipo_cuidado TEXT NOT NULL,
                descricao TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)


def listar_cuidados():
    """Cuidados da agenda, ordenados por data."""
    with conectar_banco() as conexao:
        return conexao.execute("""
            SELECT * FROM cuidados
            ORDER BY data ASC
        """).fetchall()


def inserir_cuidado(nome_pet, tipo_cuidado, descricao, data_banco):
    with conectar_banco() as conexao:
        conexao.execute("""
            INSERT INTO cuidados
            (nome_pet, tipo_cuidado, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_pet, tipo_cuidado, descricao, data_banco, "Pendente"))


def alterar_cuidado(sql, id_cuidado):
    """Executa um UPDATE ou DELETE pelo id e retorna quantos registros mudaram."""
    with conectar_banco() as conexao:
        return conexao.execute(sql, (id_cuidado,)).rowcount


def pagina_inicial(erros=(), dados=None):
    return render_template(
        "index.html",
        cuidados=listar_cuidados(),
        erros=erros,
        dados=dados
    )


def converter_data(data_digitada):
    """Converte DD/MM/AAAA para date, ou retorna None se a data for inválida."""
    if not FORMATO_DATA.fullmatch(data_digitada):
        return None

    try:
        return datetime.strptime(data_digitada, "%d/%m/%Y").date()
    except ValueError:
        return None


def validar_cuidado(nome_pet, tipo_cuidado, descricao, data_digitada):
    """Retorna a lista de mensagens de erro do cadastro (vazia se estiver tudo certo)."""
    erros = []

    if not nome_pet.strip():
        erros.append("Informe o nome do pet.")
    elif len(nome_pet) > LIMITE_NOME_PET:
        erros.append(f"O nome do pet pode ter no máximo {LIMITE_NOME_PET} caracteres.")

    if tipo_cuidado not in TIPOS_CUIDADO:
        erros.append("Selecione um tipo de cuidado válido.")

    if not descricao.strip():
        erros.append("Informe a descrição do cuidado.")
    elif len(descricao) > LIMITE_DESCRICAO:
        erros.append(f"A descrição pode ter no máximo {LIMITE_DESCRICAO} caracteres.")

    data_convertida = converter_data(data_digitada)

    if data_convertida is None:
        erros.append("Data inválida. Digite uma data válida no formato DD/MM/AAAA.")
    elif data_convertida < date.today():
        erros.append("A data não pode ser anterior a hoje.")

    return erros


@app.route("/", methods=["GET", "POST"])
def inicio():

    if request.method != "POST":
        return pagina_inicial()

    nome_pet = request.form.get("nome_pet", "")
    tipo_cuidado = request.form.get("tipo_cuidado", "")
    descricao = request.form.get("descricao", "")
    data_digitada = request.form.get("data", "")

    erros = validar_cuidado(nome_pet, tipo_cuidado, descricao, data_digitada)

    if erros:
        return pagina_inicial(erros, request.form)

    data_banco = converter_data(data_digitada).strftime("%Y-%m-%d")
    inserir_cuidado(nome_pet, tipo_cuidado, descricao, data_banco)

    return redirect("/")


@app.route("/concluir/<int:id_cuidado>", methods=["POST"])
def concluir(id_cuidado):

    alterados = alterar_cuidado("""
        UPDATE cuidados
        SET status = 'Concluído'
        WHERE id = ?
    """, id_cuidado)

    if alterados == 0:
        abort(404)

    return redirect("/")


@app.route("/excluir/<int:id_cuidado>", methods=["POST"])
def excluir(id_cuidado):

    alterados = alterar_cuidado("""
        DELETE FROM cuidados
        WHERE id = ?
    """, id_cuidado)

    if alterados == 0:
        abort(404)

    return redirect("/")


@app.errorhandler(CSRFError)
def erro_csrf(erro):
    pagina = (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head><meta charset="UTF-8">'
        "<title>PetCare</title></head>\n"
        f'<body>\n<p>{MSG_CSRF}</p>\n<p><a href="/">Voltar para a agenda</a></p>\n'
        "</body>\n</html>\n"
    )
    return pagina, 400


@app.template_filter("data_br")
def data_br(data):

    try:
        data_convertida = datetime.strptime(
            data,
            "%Y-%m-%d"
        )

        return data_convertida.strftime("%d/%m/%Y")

    except ValueError:
        return data


def modo_debug():
    """O modo debug fica desligado, a não ser que PETCARE_DEBUG seja "1"."""
    return os.environ.get("PETCARE_DEBUG") == "1"


if __name__ == "__main__":
    criar_banco()
    app.run(debug=modo_debug())

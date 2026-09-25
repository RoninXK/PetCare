from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


def conectar_banco():
    conexao = sqlite3.connect("petcare.db")
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = conectar_banco()

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

    conexao.commit()
    conexao.close()


@app.route("/", methods=["GET", "POST"])
def inicio():

    mensagem = ""

    if request.method == "POST":

        nome_pet = request.form["nome_pet"]
        tipo_cuidado = request.form["tipo_cuidado"]
        descricao = request.form["descricao"]
        data_digitada = request.form["data"]

        try:
            data_convertida = datetime.strptime(
                data_digitada,
                "%d/%m/%Y"
            )

            data_banco = data_convertida.strftime("%Y-%m-%d")

        except ValueError:

            mensagem = "Data inválida. Digite uma data válida no formato DD/MM/AAAA."

            conexao = conectar_banco()

            cuidados = conexao.execute("""
                SELECT * FROM cuidados
                ORDER BY data ASC
            """).fetchall()

            conexao.close()

            return render_template(
                "index.html",
                cuidados=cuidados,
                mensagem=mensagem
            )

        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO cuidados
            (nome_pet, tipo_cuidado, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome_pet,
            tipo_cuidado,
            descricao,
            data_banco,
            "Pendente"
        ))

        conexao.commit()
        conexao.close()

        return redirect("/")

    conexao = conectar_banco()

    cuidados = conexao.execute("""
        SELECT * FROM cuidados
        ORDER BY data ASC
    """).fetchall()

    conexao.close()

    return render_template(
        "index.html",
        cuidados=cuidados,
        mensagem=mensagem
    )


@app.route("/concluir/<int:id>")
def concluir(id):

    conexao = conectar_banco()

    conexao.execute("""
        UPDATE cuidados
        SET status = 'Concluído'
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/")


@app.route("/excluir/<int:id>")
def excluir(id):

    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM cuidados
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect("/")


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


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
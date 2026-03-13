from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "zenlifecrm"


def conectar():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# LOGIN
# ======================

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()

        user = conn.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
            (usuario,senha)
        ).fetchone()

        conn.close()

        if user:

            session["usuario"] = usuario
            return redirect("/")

        else:

            return "Usuário ou senha inválidos"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ======================
# DASHBOARD
# ======================

@app.route("/")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()

    total_clientes = conn.execute(
        "SELECT COUNT(*) FROM clientes"
    ).fetchone()[0]

    total_leads = conn.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]

    total_apolices = conn.execute(
        "SELECT COUNT(*) FROM apolices"
    ).fetchone()[0]

    leads_novos = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Lead Novo'"
    ).fetchone()[0]

    propostas = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Proposta Enviada'"
    ).fetchone()[0]

    fechados = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE status='Fechado'"
    ).fetchone()[0]

    if leads_novos > 0:
        conversao = round((fechados / leads_novos) * 100,1)
    else:
        conversao = 0

    vendas = conn.execute("""
        SELECT seguro, COUNT(*)
        FROM leads
        GROUP BY seguro
    """).fetchall()

    tipos = [v[0] for v in vendas]
    quantidades = [v[1] for v in vendas]

    conn.close()

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_leads=total_leads,
        total_apolices=total_apolices,
        leads_novos=leads_novos,
        propostas=propostas,
        fechados=fechados,
        conversao=conversao,
        tipos=tipos,
        quantidades=quantidades
    )


# ======================
# CLIENTES
# ======================

@app.route("/clientes")
def clientes():

    conn = conectar()
    lista = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()

    return render_template("clientes.html",clientes=lista)


@app.route("/novo_cliente", methods=["POST"])
def novo_cliente():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    email = request.form["email"]

    conn = conectar()

    conn.execute(
        "INSERT INTO clientes (nome,telefone,email) VALUES (?,?,?)",
        (nome,telefone,email)
    )

    conn.commit()
    conn.close()

    return redirect("/clientes")


# ======================
# LEADS
# ======================

@app.route("/leads")
def leads():

    conn = conectar()
    lista = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()

    return render_template("leads.html",leads=lista)


@app.route("/novo_lead", methods=["POST"])
def novo_lead():

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    seguro = request.form["seguro"]
    origem = request.form["origem"]
    status = request.form["status"]

    conn = conectar()

    conn.execute("""
        INSERT INTO leads
        (nome,telefone,seguro,origem,status)
        VALUES (?,?,?,?,?)
    """,(nome,telefone,seguro,origem,status))

    conn.commit()
    conn.close()

    return redirect("/leads")
    
#=================
#Excluir e Editar Lead
#=================
@app.route("/excluir_lead/<int:id>")
def excluir_lead(id):
    conn = sqlite3.connect("database.db")
    conn.execute("DELETE FROM leads WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/leads")
    
@app.route("/editar_lead/<int:id>", methods=["GET","POST"])
def editar_lead(id):
    conn = sqlite3.connect("database.db")

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        seguro = request.form["seguro"]
        origem = request.form["origem"]
        status = request.form["status"]

        conn.execute(
            "UPDATE leads SET nome=?, telefone=?, seguro=?, origem=?, status=? WHERE id=?",
            (nome, telefone, seguro, origem, status, id)
        )

        conn.commit()
        conn.close()
        return redirect("/leads")

    lead = conn.execute("SELECT * FROM leads WHERE id=?", (id,)).fetchone()
    conn.close()
    
    return render_template("editar_lead.html", lead=lead)
    
    
#=========================
# Excluir e Editar Apoloices
#=========================

@app.route("/excluir_apolice/<int:id>")
def excluir_apolice(id):
    conn = sqlite3.connect("database.db")
    conn.execute("DELETE FROM apolices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/apolices")
    
@app.route("/editar_apolice/<int:id>", methods=["GET", "POST"])
def editar_apolice(id):
    conn = conectar()
    
    # Pega a apólice pelo ID
    apolice = conn.execute("SELECT * FROM apolices WHERE id=?", (id,)).fetchone()
    
    if not apolice:
        conn.close()
        return "Apólice não encontrada", 404

    if request.method == "POST":
        # Campos do formulário
        cliente = request.form["cliente"]
        seguradora = request.form["seguradora"]
        tipo_seguro = request.form["tipo_seguro"]
        
        # Trata valor e comissão para float seguro
        valor_str = request.form.get("valor", "0").replace(",", ".")
        try:
            valor = float(valor_str)
        except ValueError:
            valor = 0

        comissao_str = request.form.get("comissao", "0").replace(",", ".")
        try:
            comissao = float(comissao_str)
        except ValueError:
            comissao = 0

        data_inicio = request.form["data_inicio"]
        data_renovacao = request.form["data_renovacao"]
        status = request.form.get("status", "Ativa")
        seguro = request.form.get("seguro", "")

        # Atualiza no banco
        conn.execute("""
            UPDATE apolices
            SET cliente=?, seguradora=?, tipo_seguro=?, valor=?, comissao=?, data_inicio=?, data_renovacao=?, status=?, seguro=?
            WHERE id=?
        """, (cliente, seguradora, tipo_seguro, valor, comissao, data_inicio, data_renovacao, status, seguro, id))

        conn.commit()
        conn.close()
        return redirect("/apolices")

    conn.close()
    return render_template("editar_apolice.html", apolice=apolice)

# ======================
# AGENDA
# ======================

@app.route("/agenda")
def agenda():

    conn = conectar()

    tarefas = conn.execute(
        "SELECT * FROM agenda ORDER BY data_contato"
    ).fetchall()

    conn.close()

    return render_template("agenda.html",tarefas=tarefas)


@app.route("/nova_tarefa", methods=["POST"])
def nova_tarefa():

    cliente = request.form["cliente"]
    descricao = request.form["descricao"]
    data = request.form["data"]

    conn = conectar()

    conn.execute("""
        INSERT INTO agenda
        (cliente,descricao,data_contato)
        VALUES (?,?,?)
    """,(cliente,descricao,data))

    conn.commit()
    conn.close()

    return redirect("/agenda")
    
# ======================
# APOLICES
# ======================

@app.route("/apolices")
def apolices():

    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()

    lista = conn.execute(
        "SELECT * FROM apolices"
    ).fetchall()

    conn.close()

    return render_template("apolices.html", apolices=lista)


@app.route("/nova_apolice", methods=["POST"])
def nova_apolice():
    # Pegando os valores do formulário
    cliente = request.form["cliente"]
    seguradora = request.form["seguradora"]
    tipo_seguro = request.form["tipo_seguro"]
    valor = request.form["valor"]
    comissao = request.form.get("comissao", 0)  # opcional
    data_inicio = request.form["data_inicio"]
    data_renovacao = request.form["data_renovacao"]
    status = request.form.get("status", "Ativa")  # padrão Ativa
    seguro = request.form.get("seguro", "")

    # Conecta ao banco
    conn = conectar()

    # Insere no banco
    conn.execute("""
        INSERT INTO apolices
        (cliente, seguradora, tipo_seguro, valor, comissao, data_inicio, data_renovacao, status, seguro)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (cliente, seguradora, tipo_seguro, valor, comissao, data_inicio, data_renovacao, status, seguro))

    conn.commit()
    conn.close()

    return redirect("/apolices")
    
    #==================
    # Exluir Cliente 
    # ==================
    
@app.route("/excluir_cliente/<int:id>")
def excluir_cliente(id):

    conn = sqlite3.connect("database.db")

    conn.execute("DELETE FROM clientes WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/clientes")
    
    
 #=====================
 # Editar Clientes
 #=====================
 
@app.route("/editar_cliente/<int:id>", methods=["GET","POST"])
def editar_cliente(id):

    conn = sqlite3.connect("database.db")

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        conn.execute(
        "UPDATE clientes SET nome=?, telefone=?, email=? WHERE id=?",
        (nome, telefone, email, id)
        )

        conn.commit()
        conn.close()

        return redirect("/clientes")

    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("editar_cliente.html", cliente=cliente)
    

if __name__ == "__main__":
    app.run(debug=True)
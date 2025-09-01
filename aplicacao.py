from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import webbrowser
from threading import Timer
import sys
import os
from datetime import date, timedelta
import socket
import qrcode
import math

if getattr(sys, 'frozen', False):
    # Está rodando no exe criado pelo PyInstaller/auto-py-to-exe
    BASE_DIR = sys._MEIPASS
else:
    # Está rodando no script python normal\
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
db = os.path.join(DATA_DIR, 'banco.db')

print(db)
app = Flask(__name__)


# Página inicial
@app.route('/')
def home():
    return render_template('home.html')

# Listar pacientes
@app.route('/pacientes')
def listar_pacientes():
    nome = request.args.get('nome')
    id = request.args.get('id')
    if nome == 'None':
        nome = None
    if id == 'None':
        id = None
    pagina = request.args.get('pagina', 1, type=int)  # pega o parâmetro pagina (padrão 1)
    por_pagina = 40  # quantos registros por página (ajuste o número que quiser)

    filtros = []
    params = []

    if nome:
        filtros.append("nome like ?")
        params.append(f"%{nome}%")
    if id:
        filtros.append("id = ?")
        params.append(id)

    where = ""
    if filtros:
        where = " WHERE " + " AND ".join(filtros)

    # Primeiro, conta o total de pacientes para paginação
    query_count = "SELECT COUNT(*) FROM pacientes" + where
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(query_count, params)
        total = cursor.fetchone()[0]

    # Calcula offset
    offset = (pagina - 1) * por_pagina

    query = f"""
    SELECT 
        id,
        nome,
        strftime('%d/%m/%Y', data_nascimento) AS data_nascimento_formatada,
        telefone,
        email,
        endereco,
        bairro,
        cidade,
        uf,
        cep,
        naturalidade,
        sexo,
        estado_civil,
        profissao,
        altura,
        peso,
        indicado_por,
        CASE WHEN onicomicose = 1 THEN 'SIM' ELSE 'NÃO' END AS onicomicose,
        CASE WHEN onicocriptose = 1 THEN 'SIM' ELSE 'NÃO' END AS onicocriptose,
        CASE WHEN onicogrifose = 1 THEN 'SIM' ELSE 'NÃO' END AS onicogrifose,
        CASE WHEN onicoatrofia = 1 THEN 'SIM' ELSE 'NÃO' END AS onicoatrofia,
        CASE WHEN verruga_plantar = 1 THEN 'SIM' ELSE 'NÃO' END AS verruga_plantar,
        CASE WHEN hiperidrose = 1 THEN 'SIM' ELSE 'NÃO' END AS hiperidrose,
        CASE WHEN anidrose = 1 THEN 'SIM' ELSE 'NÃO' END AS anidrose,
        CASE WHEN bromidrose = 1 THEN 'SIM' ELSE 'NÃO' END AS bromidrose,
        CASE WHEN cromidrose = 1 THEN 'SIM' ELSE 'NÃO' END AS cromidrose,
        halux,
        tipo_pe,
        tipo_unha,
        anamnese,
        responsavel_cadastro
    FROM pacientes
    {where}
    LIMIT ? OFFSET ?
    """

    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params + [por_pagina, offset])
        pacientes = cursor.fetchall()

    total_paginas = (total + por_pagina - 1) // por_pagina  # arredonda pra cima

    return render_template(
        'pacientes.html',
        pacientes=pacientes,
        pagina=pagina,
        total_paginas=total_paginas,
        nome=nome,
        id=id
    )


# Adicionar paciente
@app.route('/paciente/novo', methods=['GET', 'POST'])
def novo_paciente():
    if request.method == 'POST':
        # Dados pessoais
        nome = request.form['nome']
        telefone = request.form['telefone']
        data_nascimento = request.form['data_nascimento']
        email = request.form['email']
        endereco = request.form['endereco']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        cep = request.form['cep']
        sexo = request.form['sexo']
        estado_civil = request.form['estado_civil']
        cidade_naturalidade = request.form['cidade_naturalidade']
        profissao = request.form['profissao']
        altura = request.form['altura']
        peso = request.form['peso']
        indicacao = request.form['indicacao']

        # Patologias Ungueais (checkboxes) — se não marcados, causariam erro se não tratados
        onicomicose = request.form['onicomicose'] if 'onicomicose' in request.form else '0'
        onicocriptose = request.form['onicocriptose'] if 'onicocriptose' in request.form else '0'
        onicogrifose = request.form['onicogrifose'] if 'onicogrifose' in request.form else '0'
        onicoatrofia = request.form['onicotrofia'] if 'onicotrofia' in request.form else '0'
        verruga_plantar = request.form['verruga_plantar'] if 'verruga_plantar' in request.form else '0'
        hiperidrose = request.form['Hiperidrose'] if 'Hiperidrose' in request.form else '0'
        anidrose = request.form['Anidrose'] if 'Anidrose' in request.form else '0'
        bromidrose = request.form['Bromidrose'] if 'Bromidrose' in request.form else '0'
        cromidrose = request.form['Cromidose'] if 'Cromidose' in request.form else '0'

        # Hálux (radio)
        halux = request.form['halux']

        # Tipo de Pé (radio)
        tipo_pe = request.form['tipo_pe']

        # Diabetes (checkbox com apenas uma opção)
        tipo_unha = request.form['tipo_unha'] if 'tipo_unha' in request.form else '0'

        # Observações da anamnese
        anamnese = request.form['anamnese']
        #responsavel
        resp = request.form['responsavel_cadastro']

        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pacientes (nome, telefone,data_nascimento, email, endereco,bairro,cidade,uf,cep,naturalidade,sexo,estado_civil,
                                    profissao,altura,peso,indicado_por,onicomicose,onicocriptose,onicogrifose,onicoatrofia,
                                    verruga_plantar,hiperidrose,anidrose,bromidrose,cromidrose,halux,tipo_pe,tipo_unha,
                                    anamnese,responsavel_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
            (nome, telefone, data_nascimento, email, endereco, bairro, cidade, estado, cep,
                cidade_naturalidade, sexo, estado_civil, profissao, altura, peso, indicacao,
                onicomicose, onicocriptose, onicogrifose, onicoatrofia, verruga_plantar,
                hiperidrose, anidrose, bromidrose, cromidrose, halux, tipo_pe, tipo_unha, anamnese,resp))

        conn.commit()
        conn.close()
        return redirect(url_for('listar_pacientes'))
    return render_template('paciente_form.html')

# Deletar paciente
@app.route('/paciente/deletar/<int:id>')
def deletar_paciente(id):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_pacientes'))


# Definição da função - coloca no topo, junto com outros imports e funções auxiliares
def get_datas_da_semana(ano, semana_iso):
    primeiro_dia = date.fromisocalendar(ano, semana_iso, 1)
    ultimo_dia = primeiro_dia + timedelta(days=6)
    return primeiro_dia, ultimo_dia

#LISTA PAGAMENTOS:

@app.route("/pagamentos")
def listar_pagamentos():
    nome = request.args.get("nome")
    id = request.args.get("id")
    if nome == 'None':
        nome = None
    if id == 'None':
        id = None
    pagina = int(request.args.get("pagina", 1))
    por_pagina = 50  # quantidade de registros por página

    filtros = []
    params = []

    # Filtros
    if nome:
        filtros.append("nome LIKE ?")
        params.append(f"%{nome}%")
    if id:
        filtros.append("id = ?")
        params.append(id)

    where_clause = "WHERE " + " AND ".join(filtros) if filtros else ""

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # KPIs
    kpi_query = f"""
                SELECT
                    COUNT(*) AS total_registros,
                    COALESCE(SUM(valor_numerico),0) AS soma_total_formatada,
                    COALESCE(AVG(valor_numerico), 0)AS media_valores_formatada
                FROM registros_pgto
                {where_clause}
    """
    cursor.execute(kpi_query, params)
    kpis = cursor.fetchone()

    # Total de registros (para paginação)
    total_registros = kpis[0]
    total_paginas = math.ceil(total_registros / por_pagina)

    # Paginação
    offset = (pagina - 1) * por_pagina
    query = f"""
         SELECT 
            a.id_pagamento, 
            b.nome, 
            strftime('%d/%m/%Y',a.data_pagamento) as data_pagamento, 
            a.evolucao_conduta, 
            a.valor_numerico
        FROM registros_pgto a
        LEFT JOIN pacientes b	
            on a.id = b.id
        {where_clause}
        ORDER BY id_pagamento DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [por_pagina, offset])
    pagamentos = cursor.fetchall()

    conn.close()

    return render_template(
        "pagamentos.html",
        pagamentos=pagamentos,
        total_registros=kpis[0],
        soma_total=kpis[1],
        media_valores=kpis[2],
        pagina=pagina,
        total_paginas=total_paginas,
        nome=nome,
        aluno_id=id
    )


@app.route('/pagamento/deletar/<int:id>')
def deletar_pagamentos(id):
    print(f"Tentando deletar pagamento com id: {id}")
    print(f"id: {id}, tipo: {type(id)}")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros_pgto WHERE id_pagamento = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_pagamentos'))

@app.route('/pagamento/novo', methods=['GET', 'POST'])
def novo_pagamento():
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        data_pagamento = request.form['data_pagamento']
        conduta = request.form['conduta']
        valor = request.form['valor']
        responsavel = request.form['responsavel_pgto']

        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO registros_pgto(id,data_pagamento,evolucao_conduta,valor_numerico, responsavel_pelo_cadastro)
                values(?,?,?,?,?)""",(paciente_id,data_pagamento,conduta,valor,responsavel))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_pagamentos'))
    # para preencher o select
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()
    return render_template('novo_pagamento_form.html', pacientes=pacientes)
#lista agenda
@app.route('/agenda')
def listar_agenda():
        data = request.args.get('data')
        mes = request.args.get('mes')
        semana = request.args.get('semana')

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = """
            SELECT 
                a.id,
                strftime('%d/%m/%Y', a.data) as data_formatada,
                a.horario,
                p.nome,
                a.observacoes,
                a.responsavel_cadastro
            FROM 
                agenda a
            JOIN 
                pacientes p ON a.paciente_id = p.id
        """

        filtros = []
        params = []


        # 🎯 Filtro por dia
        if data:
            filtros.append("a.data = ?")
            params.append(data)

        # 🎯 Filtro por mês
        elif mes:
            filtros.append("strftime('%Y-%m', a.data) = ?")
            params.append(mes)

        # 🎯 Filtro por semana (ano-semana no formato %Y-%W)
        elif semana:
            ano_str, semana_w_str = semana.split('-')
            ano = int(ano_str)
            semana_num = int(semana_w_str.replace('W', ''))
            data_inicio, data_fim = get_datas_da_semana(ano, semana_num)
            filtros.append("a.data BETWEEN ? AND ?")
            params.extend([data_inicio.isoformat(), data_fim.isoformat()])

        # 🔧 Monta a query final
        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        query += " ORDER BY a.data, a.horario"

        cursor.execute(query, params)
        agenda = cursor.fetchall()
        conn.close()


        return render_template('agenda.html', agenda=agenda)

@app.route('/agenda/novo', methods=['GET', 'POST'])
def novo_agenda():
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        data = request.form['data']
        horario = request.form['horario']
        observacoes = request.form['observacoes']
        resp = request.form['responsavel']

        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agenda (paciente_id, data, horario, observacoes,responsavel_cadastro)
            VALUES (?, ?, ?, ?,?)
        """, (paciente_id, data, horario, observacoes,resp))

        conn.commit()
        conn.close()
        return redirect(url_for('listar_agenda'))

    # Se for GET → Buscar pacientes para preencher o select
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()

    return render_template('agenda_form.html', pacientes=pacientes)

@app.route('/agenda/deletar/<int:id>')
def deletar_agenda(id):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agenda WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_agenda'))


@app.route('/aniversariantes')
def aniversariantes():

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("""
                  SELECT 
                    id,
                    nome,
                    strftime('%d/%m/%Y', data_nascimento) AS data_nascimento_formatada,
                    telefone
                FROM pacientes
                WHERE
                (
                    (
                        CAST(strftime('%m%d', data_nascimento) AS INTEGER) >= CAST(strftime('%m%d', 'now') AS INTEGER)
                        AND
                        CAST(strftime('%m%d', data_nascimento) AS INTEGER) <= CAST(strftime('%m%d', date('now', '+14 days')) AS INTEGER)
                    )
                    OR
                    (
                        strftime('%m%d', 'now') > strftime('%m%d', date('now', '+14 days'))
                        AND
                        (
                            CAST(strftime('%m%d', data_nascimento) AS INTEGER) >= CAST(strftime('%m%d', 'now') AS INTEGER)
                            OR
                            CAST(strftime('%m%d', data_nascimento) AS INTEGER) <= CAST(strftime('%m%d', date('now', '+14 days')) AS INTEGER)
                        )
                    )
                )
                AND telefone IS NOT NULL
                ORDER BY strftime('%m%d', data_nascimento);
        """)

        pacientes = cursor.fetchall()
        conn.close()

        return render_template('aniversariantes.html', pacientes=pacientes)


def abrir_navegador():
    webbrowser.open_new('http://127.0.0.1:5000/')

def get_ip_local():
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except:
        return '127.0.0.1'

def gerar_qrcode_e_mostrar(url):
    img = qrcode.make(url)
    img.save("qrcode_flask.png")
    print("QR Code gerado e salvo como qrcode_flask.png")
    img.show()

if __name__ == "__main__":
    Timer(1, abrir_navegador).start()
    ip = get_ip_local()
    url = f"http://{ip}:5000"
    print(f"Acesse pelo navegador: {url}")
    gerar_qrcode_e_mostrar(url)
    app.run(host="0.0.0.0", port=5000)


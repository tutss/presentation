import flask
import json
from flask import request, jsonify, render_template, redirect
from funcionalidades import product_logic as pl

# salva o upload em json
UPLOAD_FOLDER = 'data/upload/'
ALLOWED_EXTENSIONS = set('json')

# configurações do flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# todo: quando cancelar, tirar do json do usuario


@app.route('/', methods=['GET'])
def home():
    """
    Home - renderiza a tela inicial
    """
    return render_template('home.html')


@app.route('/products', methods=['GET'])
def products():
    """
    Retorna todos os produtos da base interna
    """
    return jsonify(json.load(open('data/products.json', 'r')))


@app.route('/products/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    Cadastra um produto na base
    """
    if request.method == 'GET':
        return render_template('cadastro.html')
    elif request.method == 'POST':
        fields = ['nome', 'parceiro', 'categoria', 'descricao']
        pl.check_fields(fields)
        produto_info = pl.parse_cadastro_produto()

        if produto_info == 'parceiro':
            return 'Error: Parceiro não encontrado'
        if produto_info == 'categoria':
            return 'Error: Categoria não encontrada'
        if produto_info == 'id_ex':
            return 'Error: Produto já cadastrado'

        pl.log_cadastro(produto_info)
        pl.write_products(produto_info)
        return redirect('/products/cadastro/confirmacao')


@app.route('/products/cadastro/confirmacao', methods=['GET', 'POST'])
def confirma_produto():
    """
    Confirma o cadastro de um produto na base
    """
    if request.method == 'GET':
        return render_template('confirma_produto.html')
    elif request.method == 'POST':
        return redirect('/products/cadastro')


@app.route('/products/<ident>', methods=['GET'])
def product_by_id(ident):
    """
    Retorna o produto especificado pelo ID da base interna

    :param: id: o id do produto no request
    """
    return jsonify(pl.find_in_db(ident))


@app.route('/parceiros', methods=['GET'])
def partners():
    """
    Retorna todos os parceiros da base
    """
    return jsonify(json.load(open('data/partners.json', 'r')))


@app.route('/parceiros/cadastro', methods=['GET', 'POST'])
def cadastro_parceiro():
    """
    Cadastra um parceiro no banco
    """
    if request.method == 'GET':
        return render_template('cadastro_parceiro.html')
    elif request.method == 'POST':
        fields = ['nome', 'descricao']
        pl.check_fields(fields)
        dados = pl.parse_parceiro()
        pl.log_parceiro(dados)
        pl.write_parceiro(dados)
        return redirect('/parceiros/cadastro/confirmacao')


@app.route('/parceiros/cadastro/confirmacao', methods=['GET', 'POST'])
def confirma_parceiro():
    """
    Confirma o cadastro de um produto na base
    """
    if request.method == 'GET':
        return render_template('confirma_parceiro.html')
    elif request.method == 'POST':
        return redirect('/parceiros/cadastro')


@app.route('/categorias', methods=['GET'])
def categories():
    """
    Retorna todas as categorias da base
    """
    return jsonify(json.load(open('data/categories.json', 'r')))


@app.route('/categorias/cadastro', methods=['GET', 'POST'])
def cadastro_categoria():
    if request.method == 'GET':
        return render_template('cadastro_categoria.html')
    elif request.method == 'POST':
        fields = ['nome', 'descricao']
        pl.check_fields(fields)
        dados = pl.parse_categoria()
        pl.log_categoria(dados)
        pl.write_categoria(dados)
        return redirect('/categorias/cadastro/confirmacao')


@app.route('/categorias/cadastro/confirmacao', methods=['GET', 'POST'])
def confirma_categoria():
    """
    Confirma o cadastro de um produto na base
    """
    if request.method == 'GET':
        return render_template('confirma_categoria.html')
    elif request.method == 'POST':
        return redirect('/categorias/cadastro')


@app.route('/products/categorias/<ident>', methods=['GET'])
def products_by_categ(ident):
    """
    Retorna os produtos de determinada categoria
    :param: id: o id da categoria no request
    """
    return pl.find_in_db(ident, 'id_categoria')


@app.route('/products/parceiros/<ident>', methods=['GET'])
def products_by_partner(ident):
    """
    Retorna todos os produtos de determinado parceiro
    :param: id: o id do parceiro no request
    """
    return pl.find_in_db(ident, 'id_parceiro')


@app.route('/products/<ident>/caract', methods=['GET'])
def product_caract(ident):
    """
    Retorna a característica de um produto específico
    :param: id: o id do produto no request
    """
    produto = pl.find_in_db(ident)
    return jsonify(produto['caracteristicas'])


# Método para exemplo
@app.route('/oferta/recebe', methods=['GET'])
def param_necessarios():
    """
    Recebe os parâmetros para repassar para o parceiro
    """
    json_received = json.load(open('data/params.json', 'r'))
    return jsonify(json_received)


# Método para exemplo
@app.route('/oferta/envia', methods=['GET', 'POST'])
def required_for_logic():
    """
    Manda para o parceiro os parâmetros necessários
    """
    if request.method == 'GET':
        return render_template('envia.html')
    elif request.method == 'POST':
        pl.upload_for_partner()
        return redirect('/')
    return ''


# Método de exemplo
@app.route('/products/recebe/listar_inverso', methods=['GET'])
def updated_listing_inverse():
    """
    Lista os novos produtos que chegariam do parceiro

    Esse método recebe os produtos nos quais não deve disponibilizar.
    """
    new_products = json.load(open('data/updated_products.json', 'r'))
    ids = pl.return_ids(new_products)
    show = pl.del_upd_inverse(ids, json.load(open('data/products.json', 'r')))
    return show


@app.route('/products/recebe/listar_ordem', methods=['GET'])
def updated_listing_order():
    """
    Lista os novos produtos que chegariam do parceiro

    Esse método recebe os produtos nos quais  deve disponibilizar.
    """
    new_products = json.load(open('data/order_updated_products.json', 'r'))
    ids = pl.return_ids(new_products)
    show = pl.del_upd_order(ids, json.load(open('data/products.json', 'r')))
    return show


@app.route('/cotacao', methods=['GET', 'POST'])
def cotacao():
    """
    Simula o envio dos dados do cliente para o parceiro,
    para que este realize sua lógica e retorne o valor.
    """
    if request.method == 'GET':
        return render_template('form.html')
    elif request.method == 'POST':
        fields = ['name', 'age', 'cpf', 'rg', 'profissao']
        pl.check_fields(fields)

        cliente_info = pl.parse_user_data()

        # Lê da entrada
        id_produto = int(request.form['id_p'])
        rg_user = int(request.form['rg'])
        show_products = json.load(open('data/show_products.json', 'r'))

        pl.cotar_produto(show_products, id_produto, rg_user, cliente_info)

        pl.assert_user(rg_user, id_produto)

        s = '/contrata/%s/%s' % (str(rg_user), str(id_produto))

        return redirect(s)

    return ''


@app.route('/contrata/<user>/<prod_id>', methods=['GET', 'POST'])
def contrata_produto(user, prod_id):
    """
    Simula a confirmação de contrato de um produto,
    feita pelo cliente
    """
    if request.method == 'GET':
        return render_template('confirmacao.html')
    elif request.method == 'POST':
        if 'submit_form' in request.form:
            option = int(request.form['activity'])
            if not option:
                pl.produtos_cliente[pl.usuario].pop()
            pl.log_confirmation(user, prod_id)
            return redirect('/cotacao')


@app.route('/usuarios/<ident>/consulta_produtos', methods=['GET'])
def consulta_produtos_cliente(ident):
    """
    Confere os produtos contratados pelo cliente
    """
    cliente = int(ident)
    return jsonify(pl.produtos_cliente[cliente])


@app.route('/usuarios/cancelar_produto', methods=['GET', 'POST'])
def cancelar_produto():
    """
    Cancela um produto previamente contratado pelo cliente
    """
    if request.method == 'GET':
        return render_template('cancela.html')
    elif request.method == 'POST':
        fields = ['id_p', 'rg']
        pl.check_fields(fields)

        user = int(request.form['rg'])
        id_remover = int(request.form['id_p'])
        motivo = str(request.form['motivo'])

        pl.log_cancelamento(user, id_remover, motivo)
        pl.cancelamento_produto(user, id_remover)
        return redirect('/usuarios/cancelar_produto/confirmado')
    return ''


@app.route('/usuarios/cancelar_produto/confirmado', methods=['GET', 'POST'])
def confirmar_cancelamento():
    if request.method == 'GET':
        return render_template('confirma_cancelamento.html')
    elif request.method == 'POST':
        return redirect('/cotacao')


app.run(threaded=True)

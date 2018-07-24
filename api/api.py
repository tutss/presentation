import flask
import json
import os
from datetime import datetime
from flask import request, jsonify, render_template, redirect
from werkzeug.utils import secure_filename

# salva o upload em json
UPLOAD_FOLDER = 'data/upload/'
ALLOWED_EXTENSIONS = set('json')

# configurações do flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# lê do nosso banco
json_products = json.load(open('data/products.json', 'r'))
json_partners = json.load(open('data/partners.json', 'r'))
json_categories = json.load(open('data/categories.json', 'r'))

# Exemplifica os produtos de um usuário
produtos_cliente = {}
usuario = 0
id_para_checar = 0


# todo: mover metodos auxiliares para outra classe
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
    return jsonify(json_products)


@app.route('/products/<ident>', methods=['GET'])
def product_by_id(ident):
    """
    Retorna o produto especificado pelo ID da base interna

    :param: id: o id do produto no request
    """
    return jsonify(find_in_db(ident))


@app.route('/products/parceiros', methods=['GET'])
def partners():
    """
    Retorna todos os parceiros da base
    """
    return jsonify(json_partners)


@app.route('/products/categorias', methods=['GET'])
def categories():
    """
    Retorna todas as categorias da base
    """
    return jsonify(json_categories)


@app.route('/products/categorias/<ident>', methods=['GET'])
def products_by_categ(ident):
    """
    Retorna os produtos de determinada categoria
    :param: id: o id da categoria no request
    """
    return find_in_db(ident, 'id_categoria')


@app.route('/products/parceiros/<ident>', methods=['GET'])
def products_by_partner(ident):
    """
    Retorna todos os produtos de determinado parceiro
    :param: id: o id do parceiro no request
    """
    return find_in_db(ident, 'id_parceiro')


@app.route('/products/<ident>/caract', methods=['GET'])
def product_caract(ident):
    """
    Retorna a característica de um produto específico
    :param: id: o id do produto no request
    """
    produto = find_in_db(ident)
    return jsonify(produto['caracteristicas'])


# Método para exemplo
@app.route('/recebe_param', methods=['GET'])
def param_necessarios():
    """
    Recebe os parâmetros para repassar para o parceiro
    """
    json_received = json.load(open('data/params.json', 'r'))
    return jsonify(json_received)


# Método para exemplo
@app.route('/envia_parceiro', methods=['GET', 'POST'])
def required_for_logic():
    """
    Manda para o parceiro os parâmetros necessários
    """
    if request.method == 'GET':
        return render_template('envia.html')
    elif request.method == 'POST':
        upload_for_partner()
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
    ids = return_ids(new_products)
    show = del_upd_inverse(ids, json_products)
    return show


@app.route('/products/recebe/listar_ordem', methods=['GET'])
def updated_listing_order():
    """
    Lista os novos produtos que chegariam do parceiro

    Esse método recebe os produtos nos quais  deve disponibilizar.
    """
    new_products = json.load(open('data/order_updated_products.json', 'r'))
    ids = return_ids(new_products)
    show = del_upd_order(ids, json_products)
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
        check_fields(fields)

        cliente_info = parse_user_data()

        # Lê da entrada
        id_produto = int(request.form['id_p'])
        rg_user = int(request.form['rg'])
        show_products = json.load(open('data/show_products.json', 'r'))

        cotar_produto(show_products, id_produto, rg_user, cliente_info)

        assert_user(rg_user, id_produto)

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
                produtos_cliente[usuario].pop()
            log_confirmation(user, prod_id)
            return redirect('/cotacao')


@app.route('/usuarios/<ident>/consulta_produtos', methods=['GET'])
def consulta_produtos_cliente(ident):
    """
    Confere os produtos contratados pelo cliente
    """
    cliente = int(ident)
    return jsonify(produtos_cliente[cliente])


@app.route('/usuarios/cancelar_produto', methods=['GET', 'POST'])
def cancelar_produto():
    """
    Cancela um produto previamente contratado pelo cliente
    """
    if request.method == 'GET':
        return render_template('cancela.html')
    elif request.method == 'POST':
        fields = ['id_p', 'rg']
        check_fields(fields)

        user = int(request.form['rg'])
        id_remover = int(request.form['id_p'])
        motivo = str(request.form['motivo'])

        log_cancelamento(user, id_remover, motivo)
        cancelamento_produto(user, id_remover)
        return redirect('/usuarios/cancelar_produto/confirmado')
    return ''


@app.route('/usuarios/cancelar_produto/confirmado', methods=['GET', 'POST'])
def confirmar_cancelamento():
    if request.method == 'GET':
        return render_template('confirma_cancelamento.html')
    elif request.method == 'POST':
        return redirect('/cotacao')


#########################################
#                                       #
#  MÉTODOS AUXILIARES AS ROTAS          #
#                                       #
#########################################

def remove_duplicates(li):
    """
    Remove duplicatas de uma lista
    :param li: lista a remover elementos duplicados
    """
    clean_list = []
    [clean_list.append(x) for x in li if x not in clean_list]
    return clean_list


def contains_id(li, ident):
    """
    Verifica se a identificação está na lista
    :param li: lista com produtos
    :param ident: identificação do produto
    :return: True or False
    """
    for i in range(len(li)):
        elem = li[i]
        if elem['id'] == ident:
            return True
        if i == len(li) - 1 and elem['id'] != ident:
            return False

    return True


def verify_bounds(n, size):
    """
    Verifica os bounds do index do ID de entrada
    :param n: o id
    :param size: tamanho da lista de produtor
    """
    if n < 0 or n >= size:
        return 'Error: id out of bounds'


def verify_product_kvs(produtos_entrada):
    """
    Verifica as chaves e valores de retorno do parceiro,
    para assim, verificar possíveis adulterações e/ou quebras
    de contrato
    :param produtos_entrada: lista de produtos
    """
    for elem in produtos_entrada:
        id_elem = elem['id']
        produto_para_checar = json_products[id_elem]
        for key, value in elem.items():
            valor_esperado = produto_para_checar[key]
            if valor_esperado is not None:
                if valor_esperado == value:
                    pass
                else:
                    log_file = open('data/logs/log.txt', 'a')
                    string_log = '%s com valores adulterados pelo parceiro %d\n' % \
                                 (produto_para_checar['nome'], produto_para_checar['id_parceiro'])

                    string_log_expected = 'Esperado: {valor_esperado}\nRecebido: {value}\n\n'\
                        .format(valor_esperado=valor_esperado, value=value)

                    log_file.write(string_log)
                    log_file.write(string_log_expected)
                    log_file.close()
    return


def log_confirmation(user, produto):
    """
    Log para confirmações

    :param user: identificação do usuário
    :param produto: identificação do produto
    """
    log_file = open('data/logs/confirmacoes.txt', 'a')
    s = 'Usuário %s contratou o produto %s - %s\n' % (user, produto, str(datetime.now()))
    log_file.write(s)
    log_file.close()


def log_cancelamento(user, produto, motivo):
    """
    Log para identificação do cancelamento

    :param user: identificação do usuário
    :param produto: identificação do produto
    :param motivo: motivação para cancelamento
    """
    log_file = open('data/logs/cancelamentos.txt', 'a')
    s = 'Usuário %d fez o cancelamento do produto %d - %s\nMotivo: %s' % (user, produto, str(datetime.now()), motivo)
    log_file.write(s)
    log_file.close()


def allowed_file(filename):
    """
    Checa e salva em um arquivo dado nome do arquivo
    :param filename: nome do arquivo
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def return_produto_id(n_id):
    """
    Retorna um produto, dado um id
    :param n_id: identificação do produto
    """
    for elem in json_products:
        if elem['id'] == n_id:
            produto_especifico = elem
            return produto_especifico


def return_by_filter(n_id, prod_json, search_for):
    """
    Retorna uma lista de produtos, dado o parâmetro de busca,
    tanto para o tipo de identificação quanto para a string de busca

    :param n_id: parâmetro para identificação
    :param prod_json: lista de produtos
    :param search_for: string para busca
    """
    produtos = []
    for elem in prod_json:
        if elem[search_for] == n_id:
            produtos.append(elem)
    return produtos


def find_in_db(ident, s=''):
    """
    Procura dentro dos produtos, dado um identificador e uma string.
    Caso a string seja vazia, procura pelo id. Caso ela seja não vazia,
    a utiliza como busca

    :param ident: identificação do produto
    :param s: parâmetro de busca
    """
    num = int(ident)
    verify_bounds(num, len(json_products))
    if s != '':
        return jsonify(return_by_filter(num, json_products, s))
    else:
        return return_produto_id(num)


def upload_for_partner():
    """
    Faz o upload da file localmente (como simulação)
    """
    if 'file' not in request.files:
        print('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        print('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def del_upd_inverse(ids, json_produtos):
    """
    Faz as deleções ou updates na lista de produtos a ser exibida para o usuário.
    Recebe na forma: produtos a não exibir

    :param ids: lista de ids dos produtos
    :param json_produtos: lista de produtos
    """
    show = json_produtos.copy()
    copy_ids = ids.copy()
    for i in range(len(ids)):
        del show[copy_ids[i]]
        copy_ids[:] = [x - 1 for x in copy_ids]
    with open('data/show_products.json', 'w') as f:
        json.dump(show, f)
    return jsonify(show)


def del_upd_order(ids, produtos):
    """
    Faz as deleções ou updates na lista de produtos a ser exibida para o usuário
    Recebe na forma: produtos a exibir

    :param ids: lista de ids dos produtos
    :param produtos: lista de produtos
    """
    show = produtos.copy()
    first_to_remove = ids[0]
    partner = show[first_to_remove]['id_parceiro']

    produtos_filtered = []
    for product in show:
        if product['id_parceiro'] == partner:
            if product['id'] in ids:
                produtos_filtered.append(product)
        else:
            produtos_filtered.append(product)

    with open('data/show_products.json', 'w') as f:
        json.dump(produtos_filtered, f)

    return jsonify(produtos_filtered)


def return_ids(new_prod):
    """
    Retorna os ids presentes na lista de produtos
    :param new_prod: lista de produtos
    """
    ids = []
    verify_product_kvs(new_prod)
    for elem in new_prod:
        ids.append(elem['id'])
    return ids


def assert_user(user, produto):
    """
    Torna os valores de usuário e do id para os certos
    :param user: identificação do usuário
    :param produto: identificação do produto
    """
    usuario = user
    id_para_checar = produto
    return


def check_fields(fields):
    """
    Checa se cada campo está na lista de campos
    :param fields: lista de campos
    """
    for field in fields:
        if field not in request.form:
            print('Missing fields')
            return redirect(request.url)


def parse_user_data():
    """
    Forma um dicionário (dict) com as informações do usuário
    """
    data = {
            "nome": str(request.form['name']),
            "age": int(request.form['age']),
            "cpf": int(request.form['cpf']),
            "rg": int(request.form['rg']),
            "profissao": str(request.form['profissao']),
            "id_produto": list(request.form['id_p'])
        }
    return data


def check_for_product(id_produto, user, produtos):
    """
    Adiciona um produto a lista de produtos contratados pelo usuário

    :param id_produto: identificação do produto
    :param user: identificação do usuário
    :param produtos: lista de produtos
    """
    for elem in produtos:
        if elem['id'] == id_produto:
            produtos_cliente.setdefault(user, []).append(elem)
            break
    return


def save_products(user_info, produto):
    """
    Salva o produto contratado pelo usuário

    :param user_info: informações do usuário
    :param produto: identificação do produto
    """
    if user_info:
        file_name = 'users/%d.json' % user_info['rg']
        with open(file_name, 'r+') as f:
            if os.path.getsize(file_name) <= 0:
                json.dump(user_info, f)
            else:
                data = f.read()
                dict_data = json.loads(data)
                if bool(dict_data):
                    dict_data['id_produto'].append(str(produto))
                dict_data['id_produto'] = remove_duplicates(dict_data['id_produto'])
                f.seek(0)
                f.truncate()
                json.dump(dict_data, f)
    else:
        return 'Error: os dados não foram enviados'
    return


def cancelamento_produto(user, produto_id):
    """
    Cancela um produto

    :param user: identificação do usuário
    :param produto_id: identificação do produto
    """
    if user in produtos_cliente.keys():
        produtos = produtos_cliente[user]
        if contains_id(produtos, produto_id):
            for i in range(len(produtos)):
                produto = produtos[i]
                if produto['id'] == produto_id:
                    produtos.remove(produto)
                    break
        else:
            return 'Invalid ID'
    else:
        return 'User unavailable'


def cotar_produto(produtos, produto_id, user, user_info):
    """
    Cota um produto para um usuário

    :param produtos: lista de produtos
    :param produto_id: id do produto
    :param user: identificação do usuário
    :param user_info: informações do usuário
    """
    if contains_id(produtos, produto_id):
        check_for_product(produto_id, user, produtos)

        produtos_cliente[user] = remove_duplicates(produtos_cliente[user])

        save_products(user_info, produto_id)
        # DEBUG
        # for key, value in produtos_cliente.items():
        #     print('\ncliente: {key} e o valor: {valor}\n'.format(key=key, valor=value))
    else:
        return 'Error: Product not available'


app.run(threaded=True)

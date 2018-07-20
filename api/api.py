import flask
import json
import os
import requests
from flask import request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

# salva o upload em json
UPLOAD_FOLDER = 'data/upload/'
ALLOWED_EXTENSIONS = set(['json'])

# configurações do flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# lê do nosso banco
json_products = json.load(open('data/products.json', 'r'))
json_partners = json.load(open('data/partners.json', 'r'))
json_categories = json.load(open('data/categories.json', 'r'))

# Exemplifica os produtos de um usuário
produtos_cliente = { }
usuario = 0
id_para_checar = 0


# TODOS
# TODO: Formatar o código
# TODO: Debugar lógica da cotacao
# TODO: Retirar prints
# todo: melhoras comentários
# todo: melhorar o display


@app.route('/', methods=['GET'])
def home():
    """
    Home
    """
    return render_template('home.html')


@app.route('/products', methods=['GET'])
def products():
    """
    Retorna todos os produtos
    """
    return jsonify(json_products)


@app.route('/product_id', methods=['GET'])
def product_by_id():
    """
    Retorna o produto especificado pelo ID
    """
    if 'id' in request.args:
        n_id = int(request.args['id'])
    else:
        return 'Error: No ID provided'

    verify_bounds(n_id, len(json_products))

    for elem in json_products:
        if elem['id'] == n_id:
            produto_especifico = elem

    return jsonify(produto_especifico)


@app.route('/products_categ', methods=['GET'])
def products_by_categ():
    """
    Retorna os produtos de determinada categoria
    """
    if 'id_categoria' in request.args:
        n_categoria = int(request.args['id_categoria'])
    else:
        return 'Error: No id_categoria provided'

    verify_bounds(n_categoria, len(json_products))

    produtos_categoria = []
    for elem in json_products:
        if elem['id_categoria'] == n_categoria:
            produtos_categoria.append(elem)

    return jsonify(produtos_categoria)


@app.route('/products_parceiro', methods=['GET'])
def products_by_partner():
    """
    Retorna todos os produtos de determinado parceiro
    """
    if 'id_parceiro' in request.args:
        n_parceiro = int(request.args['id_parceiro'])
    else:
        return 'Error: No id_parceiro provided'

    produtos_parceiro = []
    for elem in json_products:
        if elem['id_parceiro'] == n_parceiro:
            produtos_parceiro.append(elem)

    return jsonify(produtos_parceiro)


@app.route('/product_caract', methods=['GET'])
def product_caract():
    """
    Retorna a característica de um produto específico
    """
    if 'id' in request.args:
        n_id = int(request.args['id'])
    else :
        return 'Error: No id provided'

    verify_bounds(n_id, len(json_products))

    for elem in json_products:
        if elem['id'] == n_id:
            produto_especifico = elem['caracteristicas']

    return jsonify(produto_especifico)


@app.route('/parceiros', methods=['GET'])
def partners():
    """
    Retorna todos os parceiros da plataforma
    """
    return jsonify(json_partners)


@app.route('/categorias', methods=['GET'])
def categories():
    """
    Retorna todas as categorias do sistema
    """
    return jsonify(json_categories)


@app.route('/recebe_param', methods=['GET'])
def param_necessarios():
    """
    Recebe os parâmetros para realizar a lógica
    """
    json_received = json.load(open('data/params.json','r'))
    return jsonify(json_received)


@app.route('/envia_parceiro', methods=['GET','POST'])
def required_for_logic():
    """
    Manda para o parceiro os parâmetros
    """
    if request.method == 'GET':
        return render_template('envia.html')
    elif request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/')

    return ''


@app.route('/recebe_produtos_inverse', methods=['GET'])
def updated_listing_inverse():
    """
    Lista os novos produtos
    """
#     Ler só os ids
#     Parceiro passa quais não irá mostrar
    ids = []
    new_products = json.load(open('data/updated_products.json', 'r'))
    verify_product_kvs(new_products)
    for elem in new_products:
        ids.append(elem['id'])

    show_products = json_products.copy()
    for i in range(len(ids)):
        del show_products[ids[i]]
        ids[:] = [x - 1 for x in ids]

    with open('data/show_products.json', 'w') as f:
        json.dump(show_products, f)

    return jsonify(show_products)


@app.route('/recebe_produtos_order', methods=['GET'])
def updated_listing_order():
    ids = []
    new_products = json.load(open('data/order_updated_products.json', 'r'))
    verify_product_kvs(new_products)
    for elem in new_products:
        ids.append(elem['id'])

    show_products = json_products.copy()
    first_to_remove = ids[0]
    partner = show_products[first_to_remove]['id_parceiro']
    filtered_products = []
    for product in show_products:
        if product['id_parceiro'] == partner:
            if product['id'] in ids:
                filtered_products.append(product)
        else:
            filtered_products.append(product)

    with open('data/show_products.json', 'w') as f:
            json.dump(filtered_products, f)

    return jsonify(filtered_products)


@app.route('/cotacao', methods=['GET', 'POST'])
def cotacao():
    if request.method == 'GET':
        return render_template('form.html')
    elif request.method == 'POST':
        check_fields = 'name' or 'age' or 'cpf' or 'rg' or 'profissao'
        if check_fields not in request.form:
            flash('Missing fields')
            return redirect(request.url)

        cliente_info = {
            "nome": request.form['name'],
            "age": request.form['age'],
            "cpf": request.form['cpf'],
            "rg": request.form['rg'],
            "profissao": request.form['profissao'],
            "id_produto": request.form['id_p']
        }

        id_produto = int(request.form['id_p'])
        file_num = int(request.form['rg'])
        show_products = json.load(open('data/show_products.json', 'r'))

        if contains_id(show_products, id_produto):
            for elem in show_products:
                if elem['id'] == id_produto:
                    produtos_cliente.setdefault(file_num, []).append(elem)
                    break

            produtos_cliente[file_num] = remove_duplicates(produtos_cliente[file_num])

            # TODO: arrumar o update, adicionar apenas o novo id produto pro usuario
            if cliente_info:
                file_name = 'users/%d.json' % file_num
                with open(file_name, 'a') as f:
                    json.dump(cliente_info, f)

            # DEBUG
            # for key, value in produtos_cliente.items():
            #     print('\ncliente: {key} e o valor: {valor}\n'.format(key=key, valor=value))
        else:
            return 'Error: Product not available'

        usuario = file_num
        id_para_checar = id_produto

        return redirect('/contrata')
    return ''


@app.route('/contrata', methods=['GET', 'POST'])
def contrata_produto():
    if request.method == 'GET':
        return render_template('confirmacao.html')
    elif request.method == 'POST':
        if 'submit_form' in request.form:
            option = int(request.form['activity'])
            print('Opção: ', option)
            print('Tipo: ', type(option))
            if not option:
                produtos_cliente[usuario].pop()
                print('Produto removido')
            return redirect('/cotacao')


@app.route('/consulta_produtos', methods=['GET'])
def consulta_produtos_cliente():
    if request.args.get('cliente') is None:
        return 'Error: missing cliente argument'
    cliente = int(request.args.get('cliente'))
    print('Verificando os produtos do cliente na base')
    return jsonify(produtos_cliente[cliente])


@app.route('/cancelar_produto', methods=['GET', 'POST'])
def cancelar_produto():
    if request.method == 'GET':
        return render_template('cancela.html')
    elif request.method == 'POST':
        print('Iniciando o cancelamento')
        check_fields = 'id_p' or 'rg'
        if check_fields not in request.form:
            print('Missing fields')
            return redirect(request.url)

        user = int(request.form['rg'])
        id_remover = int(request.form['id_p'])

        if user in produtos_cliente.keys():
            produtos = produtos_cliente[user]
            if contains_id(produtos, id_remover):
                for i in range(len(produtos)):
                    produto = produtos[i]
                    if produto['id'] == id_remover:
                        produtos.remove(produto)
                        print('Produto removido')
                        break
            else:
                return 'Invalid ID'
        else:
            return 'User unavailable'
        return redirect('/cotacao')
    return ''


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
        if i == len(li) -1 and elem['id'] != ident:
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
    for elem in produtos_entrada:
        id_elem = elem['id']
        produto_para_checar = json_products[id_elem]
        for key, value in elem.items():
            valor_esperado = produto_para_checar[key]
            if valor_esperado is not None:
                if valor_esperado == value:
                    pass
                else:
                    log_file = open('log.txt', 'a')
                    string_log = '%s com valores adulterados pelo parceiro %d\n' % (produto_para_checar['nome'],
                                                                                  produto_para_checar['id_parceiro'])
                    string_log_expected = 'Esperado: {valor_esperado}\nRecebido: {value}\n\n'.format(valor_esperado=valor_esperado,
                                                                                                   value=value)
                    log_file.write(string_log)
                    log_file.write(string_log_expected)
                    log_file.close()
    return


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.run(threaded=True)

import json
import os
import flask
from datetime import datetime
from flask import request, jsonify, redirect
from werkzeug.utils import secure_filename

# salva o upload em json
UPLOAD_FOLDER = 'data/upload/'
ALLOWED_EXTENSIONS = set('json')

app = flask.Flask(__name__)
# app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# lê do nosso banco
json_products = json.load(open('data/products.json', 'r'))
json_partners = json.load(open('data/partners.json', 'r'))
json_categories = json.load(open('data/categories.json', 'r'))

produtos_cliente = {}
usuario = 0
id_para_checar = 0

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
        return False
    return True


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
    s = 'Usuário %d fez o cancelamento do produto %d - %s\nMotivo: %s\n' % (user, produto, str(datetime.now()), motivo)
    log_file.write(s)
    log_file.close()


def log_cadastro(produto):
    """
    Log do cadastro de um produto
    :param produto: Informações do produto
    """
    p = str(produto)
    s = 'Produto cadastrado %s\n%s\n\n' % (str(datetime.now()), p)
    log_file = open('data/logs/cadastros.txt', 'a')
    log_file.write(s)
    log_file.close()
    return


def log_categoria(info):
    log_file = open('data/logs/categorias.txt', 'a')
    s = 'Categoria cadastrada - %s \n' % str(info)
    log_file.write(s)
    log_file.close()
    return


def log_parceiro(info):
    log_file = open('data/logs/parceiros.txt', 'a')
    s = 'Parceiro cadastrado - %s \n' % str(info)
    log_file.write(s)
    log_file.close()
    return


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
    if not verify_bounds(num, len(json_products)):
        return 'Error: produto não existe'
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


def write_products(informacoes):
    """
    Escreve as informações do novo produto na base
    :param informacoes: dicionário com informações
    """
    json_products.append(informacoes)
    with open('data/products.json', 'w') as f:
        json.dump(json_products, f)
    return


def parse_cadastro_produto():
    """
    Usado, na demonstração, a entrada de um produto.
    Sendo genérico, os campos de característica teriam que
    ser modificados com base na necessidade do parceiro.
    """
    nome = str(request.form['nome'])
    parceiro = str(request.form['parceiro'])
    categoria = str(request.form['categoria'])
    id_externo = int(request.form['id_ex'])
    descricao = str(request.form['descricao'])
    chave_1 = str(request.form['chave_1'])
    valor_1 = str(request.form['valor_1'])
    chave_2 = str(request.form['chave_2'])
    valor_2 = str(request.form['valor_2'])
    chave_3 = str(request.form['chave_3'])
    valor_3 = str(request.form['valor_3'])
    chave_4 = str(request.form['chave_4'])
    valor_4 = str(request.form['valor_4'])
    chave_5 = str(request.form['chave_5'])
    valor_5 = str(request.form['valor_5'])

    dict_caract = {chave_1: valor_1, chave_2: valor_2, chave_3: valor_3, chave_4: valor_4, chave_5: valor_5}

    a = [nome, parceiro, categoria, id_externo, dict_caract, descricao]

    dict_data = make_dict(a)
    return dict_data


def make_dict(li):
    """
    Forma o dicionário para um produto
    :param li: lista com parâmetros
    """
    dict_input = {}
    dict_input["nome"] = li[0]
    dict_input["id"] = len(json_products)
    for i in range(len(json_partners)):
        elem = json_partners[i]
        if li[1] == elem["nome"]:
            dict_input["id_parceiro"] = elem["id"]
            break
        if i == len(json_partners) - 1:
            return 'parceiro'

    for i in range(len(json_categories)):
        elem = json_categories[i]
        if li[2] == elem["nome"]:
            dict_input["id_categoria"] = elem["id"]
            break
        if i == len(json_categories) - 1:
            return 'categoria'

    for elem in json_products:
        if elem['id_parceiro'] == dict_input["id_parceiro"]:
            if elem['id_externo'] == li[3]:
                return 'id_ex'

    dict_input["id_externo"] = li[3]
    dict_input["caracteristicas"] = li[4]
    dict_input["descricao"] = li[5]

    return dict_input




def write_parceiro(info):
    """
    Cadastra o parceiro no banco
    :param info: informações sobre o parceiro
    """
    json_partners.append(info)
    with open('data/partners.json', 'w') as f:
        json.dump(json_partners, f)
    return


def parse_parceiro():
    """
    Executa o parse dos dados do parceiro
    """
    data = {
        "id": len(json_partners),
        "nome": str(request.form['nome']),
        "descricao": str(request.form['descricao'])
    }
    return data



def parse_categoria():
    """
    Executa o parse das informações da categoria
    """
    data = {
        "id": len(json_categories),
        "nome": str(request.form['nome'])
    }
    return data


def write_categoria(info):
    """
    Escreve no banco o cadastro de uma nova categoria
    :param info: informações da categoria
    """
    json_partners.append(info)
    with open('data/categories.json', 'w') as f:
        json.dump(json_partners, f)
    return

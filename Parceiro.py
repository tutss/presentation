# TODO: ajustar verificação de id's
from Produto import Produto
class Parceiro:

    def __init__(self, nome, id_parc, products, descr):
        """
        Construtor do objeto
        :param nome: Nome do parceiro
        :param id_parc: Identificação do parceiro
        :param products: Lista de produtos do parceiro
        :param descr: Descrição do parceiro
        """
        # Verificando os tipos
        assert type(nome) == str, 'deve ser uma string'
        assert type(id_parc) == int, 'deve ser um int'
        assert type(products) == list, 'deve ser uma lista'
        assert type(descr) == str, 'deve ser uma string'
        # Verificando se é do mesmo parceiro
        elem_0 = products[0]
        for i in range(1, len(products)):
            if (elem_0.from_partner() != products[i].from_partner()):
                raise ValueError('Produtos de parceiros diferentes')
            else:
                elem_0 = products[i]

        # Devemos verificar: se o id do parceiro já não existe na base (se o id está repetido)
        self.nome  = nome
        self.id    = id_parc
        self.prod  = products
        self.descr = descr

    # TODO: fazer __str__

    def internal_id(self):
        """
        Retorna o id do parceiro
        """
        return self.id

    def products(self):
        """
        Retorna os produtos relacionados ao parceiro
        """
        return self.prod

    def description(self):
        """
        Retorna a descrição do parceiro
        """
        return self.descr

    def add_prod(self, new_prod):
        """
        Adiciona um produto a um parceiro
        """
        n = new_prod.internal_id()
        assert self.id == n, 'deve ser do mesmo parceiro'
        self.prod.append(new_prod)

    def atributtes(self):
        return {'id': self.id, 'parceiro': self.nome,
                'produtos': self.prod, 'descrição': self.descr}

def return_products():
    # Criação do produto A
    caract_a = {'Avaliação': 'Boa', 'Número': 8.5, 'Região': 'São Paulo', 'Válido': True}
    descr_a = 'Produto A'
    prod_a = Produto('Produto A', 1, 0, 0, 10, caract_a, descr_a)

    # Criação do produto B
    caract_b = {'Avaliação': 'Média', 'Número': 8.5, 'Região': 'São Paulo', 'Válido': True}
    descr_b = 'Produto B'
    prod_b = Produto('Produto B', 1, 0, 1, 14, caract_b, descr_b)

    # Criação do produto C
    caract_c = {'Avaliação': 'Boa', 'Número': 8.5, 'Região': 'São Paulo', 'Válido': True}
    descr_c = 'Produto C'
    prod_c = Produto('Produto C', 0, 1, 0, 10, caract_c, descr_c)

    # Criação do produto D
    caract_d = {'Avaliação': 'Boa', 'Número': 8.5, 'Região': 'São Paulo', 'Válido': True}
    descr_d = 'Produto D'
    prod_d = Produto('Produto C', 0, 1, 0, 50, caract_d, descr_d)

    return [prod_a, prod_b], [prod_c, prod_d]

def main():
    prod_a, prod_b = return_products()
    desc_a = 'Empresa do bem'
    desc_b = 'Empresa legal'

    empresa_a = Parceiro('Empresa A', 1, prod_a, desc_a)
    empresa_b = Parceiro('Empresa B', 0, prod_b, desc_b)

    print(empresa_a.atributtes())
    print(empresa_b.atributtes())


main()
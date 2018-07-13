# TODO: ajustar verificação de id's
from Produto import Produto
class Categoria:

    def __init__(self, id_cat, products, desc):
        """
        Construtor do objeto

        :param id_cat: Identificação da categoria
        :param products: Produtos da categoria
        :param desc: Descrição da categoria
        """
        # TODO: analisar o que falta de verificaçao
        # Verificação dos tipos
        assert type(id_cat) == int, 'deve ser um int'
        assert type(products) == list, 'deve ser uma lista'
        assert type(desc) == str, 'deve ser uma string'
        # Verificando se é do mesmo parceiro
        elem_0 = products[0]
        for i in range(1, len(products)):
            if (elem_0.category() != products[i].category()):
                raise ValueError('Produtos de categorias diferentes')
            else:
                elem_0 = products[i]
        self.id = id_cat
        self.prod = products
        self.desc = desc

    # TODO: fazer __str__

    def internal_id(self):
        """
        Retorna o id da categoria
        """
        return self.id

    def products(self):
        """
        Retorna os produtos da categoria
        """
        return self.prod

    def description(self):
        """
        Retorna a descrição da categoria
        """
        return self.desc

    def add_prod(self, new_prod):
        """
        Adiciona um produto a categoria
        """
        n = new_prod.category()
        assert self.id == n, 'deve ser da mesma categoria'
        new_prod.append(new_prod)

    # TODO: função de atributos
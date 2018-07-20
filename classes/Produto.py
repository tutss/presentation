# TODO: ajustar verificação de id's
class Produto:

    def __init__(self, nome, id_interno, id_parceiro, id_categ, id_extern, segmentos, caract, descr):
        """
        Construtor da classe

        :param nome: Identificação interna para o produto
        :param id_interno: Identificação interna para o produto
        :param id_parceiro: Identificação interna do parceiro
        :param id_categ: Identificação da categoria
        :param id_extern: Identificação externa do produto
        :param caract: Dicionário de características do produto
        :param descr: Descrição do produto
        """
        # Verificando tipos
        assert type(nome) == str, 'deve ser uma string'
        assert (type(id_interno) == int) and (type(id_parceiro) == int), 'deve ser um int'
        assert (type(id_categ) == int) and (type(id_extern) == int), 'deve ser um int'
        assert type(caract) == dict or type(caract) == list, 'deve ser uma lista ou dicionário'
        assert type(descr) == str, 'deve ser uma string'

        # Devemos verificar: se um produto pertence a um parceiro existente, se a categoria existe,
        # e se esse novo produto já não é um produto existente na base.
        self.nome = nome
        self.id_interno = id_interno
        self.id_parc = id_parceiro
        self.categ = id_categ
        self.id_ex = id_extern
        self.segm = segmentos
        self.caract = caract
        self.descr = descr

    def __str__(self):
        return 'Produto: {self.nome}, ID: {self.id_interno}'.format(self=self)

    def internal_id(self):
        """
        Retorna o id do produto na base interna
        """
        return self.id_interno

    def external_id(self):
        """
        Retorna o id do produto da base externa
        """
        return self.id_ex

    def carac(self):
        """
        Retorna o dicionário de características
        """
        return self.caract

    def category(self):
        """
        Retorna a categoria na qual o produto pertence
        """
        return self.categ

    def segment(self):
        """
        Retorna o(s) segmento(s) no qual o produto está presente
        :return:
        """
        return self.segm

    def description(self):
        """
        Retorna a descrição do produto
        """
        return self.descr

    def from_partner(self):
        """
        Retorna o id do parceiro
        """
        return self.id_parc

    def atributtes(self):
        return {'nome': self.nome, 'id': self.id_interno, 'parceiro': self.id_parc,
                'id_categoria': self.categ, 'id_produto_externo': self.id_ex, 'caracteristicas': self.caract,
                'descrição': self.descr}

# Testes unitários
def main():
    # Criação do produto A
    caract_a = {'Avaliação': 'Boa', 'Número': 8.5, 'Região': 'São Paulo', 'Válido': True}
    descr_a = 'Produto A'
    prod_a = Produto('Produto A', 0, 0, 0, 10, caract_a, descr_a)

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

    print(prod_a.atributtes())
    print()
    print(prod_b.atributtes())
    print()
    print(prod_c.atributtes())
    print()
    print(prod_d.atributtes())


if __name__ == '__main__':
    main()
from Parceiro import Parceiro
from Produto import Produto

class Oferta:

    def __init__(self, restricao, extra, filtro_extra=False):
        # TODO: verificar que restriçao é da classe propria
        self.seg        = restricao['segmento']
        self.filter       = extra
        self.has_filter = filtro_extra

    def __str__(self):
        if (self.has_filter):
            return 'Oferta para {self.seg} com filtro: {self.filter}'.format(self=self)
        else:
            return 'Oferta para {self.seg}'.format(self=self)

    def apply_filter(self, oferta):
        
        return products



#############################
# Métodos auxiliares        #
#############################
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


def return_partner():
    prod_a, prod_b = return_products()
    desc_a = 'Empresa do bem'
    desc_b = 'Empresa legal'

    empresa_a = Parceiro('Empresa A', 1, prod_a, desc_a)
    empresa_b = Parceiro('Empresa B', 0, prod_b, desc_b)

    return empresa_a, empresa_b


def main():
    pass

if __name__ == '__main__':
    main()
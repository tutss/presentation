from Interval import Interval
class Restricao:
    def __init__(self, tipo):
        assert type(tipo) == str, 'deve ser uma string'

        if (tipo == 'Uniclass'):
            self.restr = {'segmento': tipo, 'cartao': ['Básico'], 'plano_odonto': ['Básico'],
                          'limite_cred': Interval(1000, 4000)}
        elif (tipo == 'Varejo'):
            self.restr = {'segmento': tipo, 'cartao': ['Silver'], 'plano_odonto': ['Básico', 'Médio'],
                          'limite_cred': Interval(4000, 8000)}
        else:
            self.restr = {'segmento': tipo, 'cartao': ['Black', 'Platinum'], 'plano_odonto': ['Médio', 'Ouro'],
                          'limite_cred': Interval(8000, 50000)}

    def __str__(self):
        s = 'Restrições em: '
        for restr in self.restr:
            s += restr + '; '
        return s


def main():
    rest = Restricao('Uniclass')
    print(rest)


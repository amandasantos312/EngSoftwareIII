class ContaNaoEncontradaError(Exception):
    pass


class ContaService:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def _obter(self, conta_id):
        conta = self.repositorio.buscar_por_id(conta_id)
        if conta is None:
            raise ContaNaoEncontradaError(f"Conta {conta_id} nao encontrada")
        return conta

    def depositar(self, conta_id, valor):
        conta = self._obter(conta_id)
        conta.depositar(valor)
        self.repositorio.atualizar_saldo(conta_id, conta)

    def sacar(self, conta_id, valor):
        conta = self._obter(conta_id)
        conta.sacar(valor)  # lanca SaldoInsuficienteError antes de gravar
        self.repositorio.atualizar_saldo(conta_id, conta)

    def transferir(self, origem_id, destino_id, valor):
        origem = self._obter(origem_id)
        destino = self._obter(destino_id)
        origem.sacar(valor)  # se falhar, nada foi gravado ainda
        destino.depositar(valor)
        self.repositorio.atualizar_saldo(origem_id, origem)
        self.repositorio.atualizar_saldo(destino_id, destino)

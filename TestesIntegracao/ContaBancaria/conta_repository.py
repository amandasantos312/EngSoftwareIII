from conta_bancaria import ContaBancaria


class ContaRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    def salvar(self, conta_id, titular, conta):
        self.conexao.execute(
            "INSERT INTO contas (id, titular, saldo) VALUES (?, ?, ?)",
            (conta_id, titular, conta.saldo),
        )
        self.conexao.commit()

    def buscar_por_id(self, conta_id):
        cursor = self.conexao.execute(
            "SELECT saldo FROM contas WHERE id = ?", (conta_id,)
        )
        linha = cursor.fetchone()
        if linha is None:
            return None
        return ContaBancaria(linha[0])

    def atualizar_saldo(self, conta_id, conta):
        self.conexao.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (conta.saldo, conta_id),
        )
        self.conexao.commit()

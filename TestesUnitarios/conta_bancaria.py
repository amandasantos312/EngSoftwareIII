class SaldoInsuficienteError(Exception):
    pass

class ContaBancaria:
    def __init__(self, saldo_inicial=0.0):
        if saldo_inicial < 0:
            raise ValueError("Saldo inicial invalido")
        self._saldo = saldo_inicial
      
    def depositar(self, valor):
        if valor <= 0:
            raise ValueError("Valor de deposito invalido")
        self._saldo += valor    
        
    def sacar(self, valor):        
        if valor <= 0:
            raise ValueError("Valor de saque invalido")
        if valor > self._saldo:
            raise SaldoInsuficienteError("Saldo insuficiente")
        self._saldo -= valor
     
    @property
    def saldo(self):
        return self._saldo    
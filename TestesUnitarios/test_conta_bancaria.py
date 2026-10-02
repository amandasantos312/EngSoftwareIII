import pytest
from conta_bancaria import (ContaBancaria, SaldoInsuficienteError,)

@pytest.fixture
def conta():
    return ContaBancaria(100.0)

def test_deposito_aumenta_saldo(conta):
    conta.depositar(50.0)
    assert conta.saldo == 150.0    
    
def test_saque_com_saldo_suficiente(conta):
    conta.sacar(30.0)
    assert conta.saldo == 70.0

def test_saque_com_saldo_insuficiente(conta):
    with pytest.raises(SaldoInsuficienteError):
            conta.sacar(500.0)

@pytest.mark.parametrize("valor", [-10.0, 0.0])
def test_deposito_invalido(conta, valor):
    with pytest.raises(ValueError):
        conta.depositar(valor)                    
import pytest
from calculadora import (Calculadora, ZeroDivisionError)

@pytest.fixture
def calculadora():
    return Calculadora()

def test_somar(calculadora):
    resultado = calculadora.somar(5, 3)
    assert resultado == 8

def test_subtrair(calculadora):
    resultado = calculadora.subtrair(10, 3)
    assert resultado == 7

def test_multiplicar(calculadora):
    resultado = calculadora.multiplicar(5, 5)
    assert resultado == 25

def test_dividir_com_sucesso(calculadora): 
    resultado = calculadora.dividir(10, 2)
    assert resultado == 5

def test_dividir_por_zero(calculadora):
    with pytest.raises(ZeroDivisionError):
        calculadora.dividir(10, 0) 

@pytest.mark.parametrize("a, b, esperado", [
    (2 , 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (-2, -3, -5)
])
def test_somar_parametrizado(calculadora, a, b, esperado):
    assert calculadora.somar(a, b) == esperado
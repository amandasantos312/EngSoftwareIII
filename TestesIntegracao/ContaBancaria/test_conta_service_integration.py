import sqlite3
from pathlib import Path

import pytest

from conta_bancaria import SaldoInsuficienteError
from conta_repository import ContaRepository
from conta_service import ContaService, ContaNaoEncontradaError

SCHEMA = Path(__file__).with_name("schema_conta.sql").read_text(encoding="utf-8")

CONTA_A = 1   # saldo inicial 100.0
CONTA_B = 2   # saldo inicial 50.0


@pytest.fixture
def conexao():
    """Banco sqlite em memória novo para CADA teste, com duas contas."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.execute("INSERT INTO contas (id, titular, saldo) VALUES (1, 'Ana', 100.0)")
    conn.execute("INSERT INTO contas (id, titular, saldo) VALUES (2, 'Bruno', 50.0)")
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def service(conexao):
    # Tudo real: ContaService -> ContaRepository -> ContaBancaria -> sqlite
    return ContaService(ContaRepository(conexao))


def saldo_no_banco(conexao, conta_id):
    """Lê direto do banco (SQL puro), sem passar pelo service/repository."""
    return conexao.execute(
        "SELECT saldo FROM contas WHERE id = ?", (conta_id,)
    ).fetchone()[0]


def test_deposito_persiste_no_banco(service, conexao):
    service.depositar(CONTA_A, 50.0)
    assert saldo_no_banco(conexao, CONTA_A) == 150.0


def test_saque_persiste_no_banco(service, conexao):
    service.sacar(CONTA_A, 30.0)
    assert saldo_no_banco(conexao, CONTA_A) == 70.0


def test_saque_com_saldo_insuficiente_nao_altera_banco(service, conexao):
    # Caminho de erro
    with pytest.raises(SaldoInsuficienteError):
        service.sacar(CONTA_A, 500.0)
    assert saldo_no_banco(conexao, CONTA_A) == 100.0


def test_transferencia_atualiza_as_duas_contas(service, conexao):
    service.transferir(CONTA_A, CONTA_B, 40.0)
    assert saldo_no_banco(conexao, CONTA_A) == 60.0
    assert saldo_no_banco(conexao, CONTA_B) == 90.0


def test_transferencia_com_saldo_insuficiente_nao_altera_nenhuma_conta(service, conexao):
    # Caminho de erro
    with pytest.raises(SaldoInsuficienteError):
        service.transferir(CONTA_A, CONTA_B, 500.0)
    assert saldo_no_banco(conexao, CONTA_A) == 100.0
    assert saldo_no_banco(conexao, CONTA_B) == 50.0


def test_conta_inexistente_levanta_erro_e_nao_altera_banco(service, conexao):
    # Caminho de erro
    with pytest.raises(ContaNaoEncontradaError):
        service.transferir(CONTA_A, 999, 10.0)
    assert saldo_no_banco(conexao, CONTA_A) == 100.0


def test_transferencia_para_a_mesma_conta_levanta_erro_e_nao_altera_banco(service, conexao):
    # Caminho de erro
    with pytest.raises(ValueError):
        service.transferir(CONTA_A, CONTA_A, 40.0)
    assert saldo_no_banco(conexao, CONTA_A) == 100.0

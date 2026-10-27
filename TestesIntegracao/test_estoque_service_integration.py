import sqlite3
from pathlib import Path

import pytest

from estoque_service import EstoqueService, EstoqueInsuficienteError
from produto_repository import ProdutoRepository

SCHEMA = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")

PRODUTO_ID = 1
ESTOQUE_INICIAL = 10


@pytest.fixture
def conexao():
    """Arrange comum: banco sqlite em memória novo para CADA teste,
    com o schema criado e um produto inicial (10 unidades)."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT INTO produtos (id, nome, quantidade) VALUES (?, ?, ?)",
        (PRODUTO_ID, "Caneta", ESTOQUE_INICIAL),
    )
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def service(conexao):
    # Tudo real: Service -> Repository -> sqlite em memória (sem mocks)
    return EstoqueService(ProdutoRepository(conexao))


def quantidade_no_banco(conexao, produto_id=PRODUTO_ID):
    """Lê direto do banco (SQL puro), sem passar pelo service/repository."""
    linha = conexao.execute(
        "SELECT quantidade FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    return linha[0]


# Testes obrigatórios:

def test_adicionar_estoque_atualiza_banco(service, conexao):
    service.adicionar_estoque(PRODUTO_ID, 5)
    assert quantidade_no_banco(conexao) == 15


def test_vender_produto_com_estoque_suficiente(service, conexao):
    service.vender_produto(PRODUTO_ID, 3)
    assert quantidade_no_banco(conexao) == 7


def test_vender_produto_com_estoque_insuficiente_nao_altera_banco(service, conexao):
    with pytest.raises(EstoqueInsuficienteError):
        service.vender_produto(PRODUTO_ID, 11)
    assert quantidade_no_banco(conexao) == ESTOQUE_INICIAL


# Desafio extra:

def test_duas_vendas_seguidas_atualizam_saldo_final(service, conexao):
    service.vender_produto(PRODUTO_ID, 3)
    service.vender_produto(PRODUTO_ID, 4)
    assert quantidade_no_banco(conexao) == 3


@pytest.mark.parametrize(
    "quantidade, excecao",
    [
        (0, ValueError),                  # zero
        (-5, ValueError),                 # negativa
        (11, EstoqueInsuficienteError),   # maior que o estoque
    ],
)

def test_vender_quantidade_invalida_nao_altera_banco(
    service, conexao, quantidade, excecao
):
    with pytest.raises(excecao):
        service.vender_produto(PRODUTO_ID, quantidade)
    assert quantidade_no_banco(conexao) == ESTOQUE_INICIAL
## **Testes de Integração — Conta Bancária**

Trabalho complementar do roteiro de Teste de Integração (Engenharia de Software III): aplicar, em outro projeto, os mesmos princípios usados no Sistema de Controle de Estoque.

O projeto escolhido foi a `ContaBancaria` desenvolvida na atividade de testes unitários. Ela foi estendida com uma camada de serviço e uma camada de acesso a dados, para que existam componentes que se comunicam de verdade.

### **Camadas que se comunicam**

```
teste → ContaService → ContaRepository → banco sqlite em memória
                ↘ ContaBancaria (regra de negócio) ↙
```

| Arquivo | Camada | Responsabilidade |
|---|---|---|
| `conta_bancaria.py` | Domínio | `ContaBancaria`: valida depósito/saque e lança `SaldoInsuficienteError` ou `ValueError`. |
| `conta_repository.py` | Acesso a dados | `ContaRepository`: lê e grava contas no banco (`sqlite3`). |
| `conta_service.py` | Serviço | `ContaService`: `depositar`, `sacar` e `transferir`; lança `ContaNaoEncontradaError` para conta inexistente. |
| `schema_conta.sql` | Banco | Criação da tabela `contas` (`id`, `titular`, `saldo`). |
| `test_conta_service_integration.py` | Testes | Testes de integração com pytest. |

Os dois componentes integrados são o **`ContaService`** e o **`ContaRepository`**: o serviço busca a conta pelo repositório, aplica a regra de negócio da `ContaBancaria` e grava o novo saldo de volta no banco.

### **Por que é teste de integração (e não unitário)**

- No teste unitário, a `ContaBancaria` é testada **isolada**, e o saldo é conferido na própria variável do objeto.
- Aqui **nada é simulado (sem mocks)**: o `ContaService` real usa o `ContaRepository` real, que executa SQL real em um banco sqlite.
- As asserções leem o saldo **direto do banco** com SQL puro (`saldo_no_banco`), sem passar pelo service nem pelo repository. Assim o teste só passa se as peças funcionarem **juntas**, inclusive a persistência.

### **Princípios aplicados**

- **Dependência externa isolada:** cada teste abre um banco `sqlite3.connect(":memory:")` novo (fixture `conexao`), sem servidor e sem arquivo em disco.
- **Dados controlados:** a fixture cria a tabela e insere duas contas conhecidas — Ana (id 1, saldo 100.0) e Bruno (id 2, saldo 50.0).
- **Testes independentes:** a conexão é fechada ao final de cada teste (`conn.close()` após o `yield`), então nenhum teste depende do estado deixado por outro.

### **Testes**

| Teste | Cenário | Tipo |
|---|---|---|
| `test_deposito_persiste_no_banco` | Depósito de 50.0 na conta A → saldo 150.0 no banco | Sucesso |
| `test_saque_persiste_no_banco` | Saque de 30.0 na conta A → saldo 70.0 no banco | Sucesso |
| `test_saque_com_saldo_insuficiente_nao_altera_banco` | Saque de 500.0 lança `SaldoInsuficienteError` e o saldo continua 100.0 | Erro |
| `test_transferencia_atualiza_as_duas_contas` | Transferência de 40.0 de A para B → A = 60.0 e B = 90.0 | Sucesso |
| `test_transferencia_com_saldo_insuficiente_nao_altera_nenhuma_conta` | Transferência de 500.0 lança `SaldoInsuficienteError` e nenhuma das contas muda | Erro |
| `test_conta_inexistente_levanta_erro_e_nao_altera_banco` | Transferência para a conta 999 lança `ContaNaoEncontradaError` e a conta A continua com 100.0 | Erro |
| `test_transferencia_para_a_mesma_conta_levanta_erro_e_nao_altera_banco` | Transferência da conta A para ela mesma lança `ValueError` e o saldo continua 100.0 | Erro |

### **Como executar**

Requisitos: Python 3.10+ e pytest (`sqlite3` já vem na biblioteca padrão).

```bash
pip install pytest
cd TestesIntegracao/ContaBancaria
pytest -v
```

Resultado esperado:

```
test_conta_service_integration.py::test_deposito_persiste_no_banco PASSED
test_conta_service_integration.py::test_saque_persiste_no_banco PASSED
test_conta_service_integration.py::test_saque_com_saldo_insuficiente_nao_altera_banco PASSED
test_conta_service_integration.py::test_transferencia_atualiza_as_duas_contas PASSED
test_conta_service_integration.py::test_transferencia_com_saldo_insuficiente_nao_altera_nenhuma_conta PASSED
test_conta_service_integration.py::test_conta_inexistente_levanta_erro_e_nao_altera_banco PASSED
test_conta_service_integration.py::test_transferencia_para_a_mesma_conta_levanta_erro_e_nao_altera_banco PASSED

7 passed
```

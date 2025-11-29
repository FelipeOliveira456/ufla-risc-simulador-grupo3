# Simulador Funcional do Processador UFLA-RISC

Trabalho Prático 1 - Arquitetura de Computadores II  
Universidade Federal de Lavras - 2º Semestre 2025

**Autores:**

- Felipe Geraldo de Oliveira  
- Leonardo Elias Rodrigues  
- Orlando Leite Fernandes de Oliveira  
- Gabriel Marcos Lopes

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura do Processador](#arquitetura-do-processador)
- [Instalação e Uso](#instalação-e-uso)
- [Conjunto de Instruções](#conjunto-de-instruções)
- [Instruções Adicionais](#instruções-adicionais)
- [Formato de Arquivos](#formato-de-arquivos)
- [Exemplos](#exemplos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Decisões de Implementação](#decisões-de-implementação)
- [Testes Realizados](#testes-realizados)

---

## 🎯 Visão Geral

Este projeto implementa um **simulador funcional** completo para o processador RISC de 32 bits **UFLA-RISC**, incluindo:

1. **Interpretador (interpretador.py)**: Converte código assembly em binário  
2. **Simulador (simulador.py)**: Executa programas binários com pipeline de 4 estágios  

### Características Principais

- ✅ 32 registradores de uso geral (32 bits cada)  
- ✅ 64K palavras de memória (256KB total), sendo metade para instruções (128k) e metade para dados (128k)
- ✅ 30 instruções implementadas (22 básicas + 8 adicionais)  
- ✅ Pipeline de 4 estágios: IF → ID → EX/MEM → WB  
- ✅ Suporte a pilha (r30 = stack pointer)  
- ✅ Suporte a chamadas de função (r31 = return address)  

---

## 🏗️ Arquitetura do Processador

### Especificações Técnicas

| Componente | Especificação |
|------------|---------------|
| **Largura de dados** | 32 bits |
| **Largura de endereço** | 16 bits |
| **Registradores** | 32 × 32 bits (r0-r31) |
| **Memória** | 64K palavras (256KB) |
| **Endereçamento** | Por palavra (4 bytes) |
| **Pipeline** | 4 estágios |

### Estágios do Pipeline

1. **IF (Instruction Fetch)**: Busca instrução da memória  
2. **ID (Instruction Decode)**: Decodifica e lê registradores  
3. **EX/MEM (Execute/Memory)**: Executa ALU e acessa memória  
4. **WB (Write Back)**: Escreve resultado nos registradores  

---

## 🛠️ Instruções Adicionais

Além das instruções básicas, foram adicionadas **8 instruções extras** para manipulação de funções, pilha e operações matemáticas mais complexas:

| Código Binário | Nome  | Descrição |
|----------------|-------|-----------|
| `00011000`     | `mult` | Multiplica dois registradores e armazena o resultado em um registrador destino. |
| `00011001`     | `div`  | Divide um registrador pelo outro e armazena quociente e/ou resto em registradores. |
| `00011010`     | `cmp`  | Compara dois registradores e atualiza flags de zero, negativo ou carry para instruções condicionais. |
| `00011011`     | `inc`  | Incrementa em 1 o valor de um registrador. |
| `00011100`     | `dec`  | Decrementa em 1 o valor de um registrador. |
| `00011101`     | `push` | Empilha o valor de um registrador na pilha (endereço apontado por r30). |
| `00011111`     | `call` | Salva o endereço de retorno em r31 e realiza um jump para o endereço da função. |
| `00100000`     | `ret`  | Retorna de uma função usando o endereço salvo em r31. |

---

## 🧪 Testes Realizados

Nos testes 1, 2, 3 e 4, temos:

1. Operações de carregamento de constantes, cópia e operações aritméticas  
2. Loops envolvendo desvios condicionais  
3. Envolve jumps incondicionais, shifts, xor, negação (not) e load/store  
4. Envolve simulação de uma função, com jump and link salvando a instrução, operações lógicas (and, or, not, xor), operador de incremento e decremento, operador que recupera o link da função.


## 🚀 Instalação e Uso

### Requisitos

- Python 3.7 ou superior  
- Nenhuma biblioteca externa necessária  

### Como Usar

```bash
# 1. Executar programa assembly
python main.py <teste.asm>

# 2. Executar programa binário
python main.py <teste.bin>

```

> Ao executar um arquivo `.asm`, o simulador **gera um binário intermediário** automaticamente.  

Durante a execução, o simulador **printa detalhadamente**:

- As instruções binárias carregadas na memória em ordem  
- A **ordem de execução das instruções**, com o **buffer de saída da ALU**, a instrução decodificada, opcode e flags  
- O conteúdo dos **registradores** após cada operação  
- A **memória de dados** que não está vazia  

Exemplo de saída do simulador:

🔧 Convertendo ASM → BIN...

✅ Conversão concluída. BIN salvo em test4.bin

[ADDRESS] Carga agora começará em 0
[LOAD] mem_inst[0] = 00001111000000000000001000000000
[LOAD] mem_inst[1] = 00001111000000000000001100000001
[LOAD] mem_inst[2] = 00010010000000000000000000000100
[LOAD] mem_inst[3] = 11111111111111111111111111111111
[LOAD] mem_inst[4] = 00000110000000000000000000000010
...
[LOAD] mem_inst[23] = 00100000000000000000000000000000

Memória de instruções carregada. Início do PC: 0

PC=0 | Inst=00001111000000000000001000000000 | Op=lcl
Operação registrador: tmp_result=2

PC=1 | Inst=00001111000000000000001100000001 | Op=lcl
Operação registrador: tmp_result=3

PC=2 | Inst=00010010000000000000000000000100 | Op=jal
Branch executado: PC agora = 4

PC=4 | Inst=00000110000000000000000000000010 | Op=passnota
Operação registrador: tmp_result=4294967293

PC=5 | Inst=00000110000000010000000000000011 | Op=passnota
Operação registrador: tmp_result=4294967292

PC=6 | Inst=00000111000000100000000100000100 | Op=and
Operação registrador: tmp_result=1

PC=7 | Inst=00000111000000110000000000000101 | Op=and
Operação registrador: tmp_result=0

PC=8 | Inst=00000101000001000000010100000110 | Op=or
Operação registrador: tmp_result=1

...

PC=23 | Inst=00100000000000000000000000000000 | Op=ret
Branch executado: PC agora = 3

PC=3 | Inst=11111111111111111111111111111111 | Op=halt
HALT encontrado no PC=3

=== Registradores ===
R00: 00000000000000000000000000000000  (0)
R01: 00000000000000000000000000000011  (3)
R02: 11111111111111111111111111111101  (4294967293)
R03: 11111111111111111111111111111100  (4294967292)
R04: 00000000000000000000000000000001  (1)
R05: 00000000000000000000000000000000  (0)
...
R31: 00000000000000000000000000000011  (3)

=== Memória de Dados (não zero) ===
0: 00000000000000000000000000000011  (3)


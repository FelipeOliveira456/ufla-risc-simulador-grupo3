address 10   # Início do programa

# ======================
# Loop 1: soma de 1 até 10
# ======================

zeros r0               # R0 = 0 (inicial)
lcl r1, 1              # R1 = 1 (incremento)
lcl r2, 0              # R2 = 0 (endereço memória[0])
lcl r3, 10             # R3 = 10 (limite)

# loop1_start:
add r0, r0, r1         # R0 = R0 + R1
bne r0, r3, 4          # se R0 != R3, PC = 4 (continua loop1)
store r0, r2           # memória[R2] = R0

# ======================
# Loop 2: soma do valor salvo até 20
# ======================

load r6, r2            # R6 = memória[R2]
lcl r7, 2               # R7 = 2 (incremento)
lcl r8, 1               # R8 = 1 (endereço memória[1])
lcl r9, 20              # R9 = 20 (limite)

# loop2_start:
add r6, r6, r7         # R6 = R6 + R7
bne r6, r9, 11         # se R6 != R9, continua loop2
store r6, r8           # memória[R8] = R6

halt                   # termina execução

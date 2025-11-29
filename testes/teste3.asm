address 1000   # Início do programa

# ======================
# Inicialização de registradores
# ======================
lcl r0, 6       # parte baixa
lcl r1, 4       # parte baixa

# ======================
# Operação XOr
# ======================
xor r3, r0, r1

# ======================
# Jump incondicional para instrução 6 (jump para o lsl)
# ======================
j 6

# ======================
# NOT de r4 (não será executado agora devido ao jump)
# ======================
passnota r4, r4

# ======================
# Halt
# ======================
halt

# ======================
# Shift left r3 → r4
# ======================
lsl r4, r3, r0   # o shift usa r0=1 se quiser deslocar 1 bit

# ======================
# Jump para endereço em r4 (jump para o passnota)
# ======================
jr r4

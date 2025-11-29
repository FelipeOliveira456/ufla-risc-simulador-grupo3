address 0

# Carregando constantes
lch  r0, 1
lcl  r0, 10
lch  r1, 2
lcl  r1, 5
lch  r2, 3
lcl  r2, 6
lch  r3, 4
lcl  r3, 7

# Copiando valores
passa r4, r0
passa r5, r1
passa r6, r2
passa r7, r3

# Aritmética
add  r8,  r4, r5
sub  r9,  r6, r7
mult r10, r4, r5
div  r11, r6, r5

# Halt
halt

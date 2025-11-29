address 0

lcl r0, 2
lcl r1, 3

jal 4

halt

passnota r2, r0
passnota r3, r1
and r4, r2, r1
and r5, r3, r0
or  r6, r4, r5

xor r7, r0, r1
xor r10, r6, r7

inc r10
inc r10
inc r10
inc r10
inc r10
inc r10
inc r10
dec r10

lcl r0, 1
lsr r10, r10, r0

lcl r0, 0
store r10, r0

ret

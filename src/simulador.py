class Simulador:
    """
    Simulador/Executor para o processador UFLA-RISC.
    Recebe memória de instruções já carregada pelo interpretador e endereço inicial.
    """

    def __init__(self, mem_instr, pc_start=0):
        self.reg = [0] * 32
        self.mem_data = [0] * 32768
        self.mem_instr = mem_instr.copy()
        self.pc = pc_start
        self.base_adress = pc_start
        self.running = True
        self.tmp_result = None  # temporário para write-back

        # Todos os opcodes
        self.opcodes = {
            '00000001': 'add', '00000010': 'sub', '00000011': 'zeros',
            '00000100': 'xor', '00000101': 'or', '00000110': 'passnota',
            '00000111': 'and', '00001000': 'asl', '00001001': 'asr',
            '00001010': 'lsl', '00001011': 'lsr', '00001100': 'passa',
            '00001110': 'lch', '00001111': 'lcl', '00010000': 'load',
            '00010001': 'store', '00010010': 'jal', '00010011': 'jr',
            '00010100': 'beq', '00010101': 'bne', '00010110': 'j',
            '00011000': 'mult', '00011001': 'div', '00011010': 'cmp',
            '00011011': 'inc', '00011100': 'dec', '00011101': 'push',
            '00011111': 'call', '00100000': 'ret', '11111111': 'halt'
        }

        # Divisão das instruções
        self.branch_ops = {'j', 'jal', 'jr', 'beq', 'bne', 'ret'}        # instruções de desvio
        self.mem_ops    = {'load', 'store'}                        # instruções que acessam memória
        self.reg_ops    = {op for op in self.opcodes.values()} - self.branch_ops - self.mem_ops  # resto (aritméticas, lógicas, shifts, etc.)


    def fetch(self):
        if self.pc >= len(self.mem_instr):
            self.running = False
            return None
        inst_word = self.mem_instr[self.pc]
        return format(inst_word, '032b')

    def decode(self, inst_bin):
        opcode = inst_bin[0:8]
        op = self.opcodes.get(opcode, None)
        if op is None:
            raise ValueError(f"Instrução inválida no PC={self.pc}: {inst_bin}")

        # Extrai os registradores sempre que existirem
        ra = int(inst_bin[8:16], 2)
        rb = int(inst_bin[16:24], 2)
        rc = int(inst_bin[24:32], 2)

        # Se for branch/jump, extrai o endereço corretamente
        addr = None
        if op in self.branch_ops:
            if op in {'j', 'jal'}:
                # Endereço absoluto de 24 bits (bits 8-31)
                addr = int(inst_bin[8:32], 2)
            elif op in {'beq', 'bne'}:
                # Endereço relativo ou limitado a 8 bits (bits 24-31)
                addr = int(inst_bin[24:32], 2)
            elif op == 'jr':
                # Endereço vem de registrador, não da instrução
                addr = None

        return op, ra, rb, rc, addr

    def execute_register(self, op, ra, rb, rc):
        """Executa operações de registrador e aritméticas"""
        self.tmp_result = None  # reset
        if op == 'add':
            self.tmp_result = (self.reg[ra] + self.reg[rb]) & 0xFFFFFFFF
        elif op == 'sub':
            self.tmp_result = (self.reg[ra] - self.reg[rb]) & 0xFFFFFFFF
        elif op == 'xor':
            self.tmp_result = self.reg[ra] ^ self.reg[rb]
        elif op == 'or':
            self.tmp_result = self.reg[ra] | self.reg[rb]
        elif op == 'and':
            self.tmp_result = self.reg[ra] & self.reg[rb]
        elif op == 'mult':
            self.tmp_result = (self.reg[ra] * self.reg[rb]) & 0xFFFFFFFF
        elif op == 'div':
            self.tmp_result = 0 if self.reg[rb] == 0 else (self.reg[ra] // self.reg[rb]) & 0xFFFFFFFF
        elif op == 'inc':
            self.tmp_result = (self.reg[rc] + 1) & 0xFFFFFFFF
        elif op == 'dec':
            self.tmp_result = (self.reg[rc] - 1) & 0xFFFFFFFF
        elif op == 'zeros':
            self.tmp_result = 0
        elif op == 'passnota':
            self.tmp_result = (~self.reg[ra]) & 0xFFFFFFFF
        elif op == 'passa':
            self.tmp_result = self.reg[ra]
        elif op == 'lcl':
            const16 = (ra << 8) | rb  # concatena ra e rb
            self.tmp_result = (self.reg[rc] & 0xFFFF0000) | const16
        elif op == 'lch':
            const16 = (ra << 8) | rb
            self.tmp_result = (const16 << 16) | (self.reg[rc] & 0x0000FFFF)
        elif op == 'asl':  # arithmetic shift left
            self.tmp_result = (self.reg[ra] << 1) & 0xFFFFFFFF
        elif op == 'asr':  # arithmetic shift right
            self.tmp_result = (self.reg[ra] >> 1) & 0xFFFFFFFF
        elif op == 'lsl':  # logical shift left
            self.tmp_result = (self.reg[ra] << 1) & 0xFFFFFFFF
        elif op == 'lsr':  # logical shift right
            self.tmp_result = (self.reg[ra] >> 1) & 0xFFFFFFFF
        elif op == 'push':
            self.reg[31] -= 1
            self.mem_data[self.reg[31]] = self.reg[ra]
        elif op == 'pop':
            self.reg[ra] = self.mem_data[self.reg[31]]
            self.reg[31] += 1
        elif op == 'call':
            self.reg[31] -= 1
            self.mem_data[self.reg[31]] = self.pc + 1
            self.pc = self.reg[ra]
        else:
            raise ValueError(f"Instrução de registrador desconhecida: {op}")
    
    def execute_branch(self, op, ra, rb, rc, addr):
        """Executa instruções de branch/jump"""
        if op == 'j':
            self.pc = self.base_adress + addr
        elif op == 'jal':
            self.reg[31] = self.pc + 1
            self.pc = self.base_adress + addr
        elif op == 'jr':
            self.pc = self.base_adress + self.reg[ra]
        elif op == 'beq':
            if self.reg[ra] == self.reg[rb]:
                print("Igual: Ra:", self.reg[ra], "Rb:", self.reg[rb])
                self.pc = self.base_adress + addr
            else:
                print("Desvio: Ra:", self.reg[ra], "Rb:", self.reg[rb])
                self.pc += 1
        elif op == 'bne':
            if self.reg[ra] != self.reg[rb]:
                self.pc = self.base_adress + addr
                print("Diferente: Ra:", self.reg[ra], "Rb:", self.reg[rb])
            else:
                print("Igual: Ra:", self.reg[ra], "Rb:", self.reg[rb])
                self.pc += 1
        elif op == 'ret':
            self.pc = self.base_adress + self.reg[31]
    
    def execute_memory(self, op, ra, rc):
        """
        Executa instruções de acesso à memória (load/store).

        - op: 'load' ou 'store'
        - ra: registrador fonte para load/store
        - rc: registrador destino ou endereço, dependendo da instrução
        """
        self.tmp_result = None  # reset temporário

        if op == 'load':
            # Endereço vem de RA, valor vai para tmp_result para write-back no RC
            endereco = self.base_adress + self.reg[ra]
            self.tmp_result = self.mem_data[endereco]
        elif op == 'store':
            # Endereço vem de RC, valor vem de RA
            endereco = self.base_adress + self.reg[rc]
            self.mem_data[endereco] = self.reg[ra]
        else:
            raise ValueError(f"Operação de memória inválida: {op}")

    def writeback(self, op, rc):
        """
        Escreve resultado em rc (se houver) e atualiza PC.
        - Para instruções não-branch, PC += 1.
        - Branch/jump já atualizou o PC durante execução, então não mexemos.
        """
        # Escreve resultado temporário em rc
        if self.tmp_result is not None:
            self.reg[rc] = self.tmp_result & 0xFFFFFFFF  # garante 32 bits
            self.tmp_result = None

        # Incrementa PC apenas se não for branch/jump
        if op not in self.branch_ops:
            self.pc += 1

    def step(self):
        if not self.running:
            return

        inst_bin = self.fetch()
        if inst_bin is None:
            self.running = False
            return

        op, ra, rb, rc, addr = self.decode(inst_bin)

        # --- Debug: mostra a instrução e registradores ---
        print(f"\nPC={self.pc} | Inst={inst_bin} | Op={op}")

        # --------- Escolhe tipo de execução ---------
        if op == 'halt':
            self.running = False
            print(f"HALT encontrado no PC={self.pc}")
            return
        elif op in self.branch_ops:
            self.execute_branch(op, ra, rb, rc, addr)
            print(f"Branch executado: PC agora = {self.pc}")
        elif op in {'load', 'store'}:
            self.execute_memory(op, ra, rc)
            print(f"Memória executada: tmp_result={self.tmp_result}")
        else:
            self.execute_register(op, ra, rb, rc)
            print(f"Operação registrador: tmp_result={self.tmp_result}")

        # --- Debug: writeback ---
        self.writeback(op, rc)

    def run(self, max_steps=1000):
        steps = 0
        while self.running and steps < max_steps:
            self.step()
            steps += 1
        if steps >= max_steps:
            print(f"Máximo de {max_steps} steps atingido, execução interrompida.")

    def dump_regs(self):
        print("=== Registradores ===")
        for i, val in enumerate(self.reg):
            print(f"R{i:02}: {val:032b}  ({val})")

    def dump_mem_data(self):
        print("=== Memória de Dados (não zero) ===")
        for i, val in enumerate(self.mem_data):
            if val != 0:
                print(f"{i}: {val:032b}  ({val})")


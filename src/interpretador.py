class Interpretador:
    """
    Interpretador de instruções binárias para UFLA-RISC (não executa, não decodifica).
    Apenas carrega instruções na memória de instruções e registra diretivas `address`.
    """

    def __init__(self, verbose=True):
        # Memória de instruções reservada: metade da memória física
        # 32K words = 32768 endereços válidos para instruções (0..32767)
        self.mem_inst = [0] * 32768
        self.address = 0  # endereço atual de carga
        self.enderecos_definidos = []  # histórico das diretivas address usadas
        self.verbose = verbose

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

        # mnemonic -> opcode_bin (invertido)
        self.mnemonics = {v: k for k, v in self.opcodes.items()}

    def carregar_arquivo(self, texto):
        """
        Processa o texto do arquivo de instruções.
        Remove comentários iniciados por #.
        Mantém linhas em branco ou diretivas [ADDRESS] e binário.
        """
        linhas = texto.splitlines()
        linhas_sem_comentarios = []

        for linha in linhas:
            # Remove comentário
            linha = linha.split('#')[0].strip()
            if linha:  # ignora linhas vazias após remover comentário
                linhas_sem_comentarios.append(linha)

        # Agora 'linhas_sem_comentarios' contém apenas diretivas e códigos binários
        for linha in linhas_sem_comentarios:
            if linha.startswith('address'):
                # extrai o endereço se tiver
                partes = linha.split()
                if len(partes) > 1:
                    endereco_atual = int(partes[1])
                else:
                    endereco_atual = 0
                self.enderecos_definidos.append(endereco_atual)
                if self.verbose:
                    print(f"[ADDRESS] Carga agora começará em {endereco_atual}")
            else:
                # considera linha como código binário
                valor_bin = linha
                self.mem_inst[endereco_atual] = int(valor_bin, 2)
                if self.verbose:
                    print(f"[LOAD] mem_inst[{endereco_atual}] = {valor_bin}")
                endereco_atual += 1

    def exportar_memoria(self):
        """
        Retorna a memória de instruções e o endereço inicial real (primeiro endereço carregado).
        """
        if self.enderecos_definidos:
            endereco_inicio = self.enderecos_definidos[0]
        else:
            endereco_inicio = 0  # padrão se nenhuma diretiva address foi usada

        return {
            'mem_instr': self.mem_inst.copy(),
            'address_start': endereco_inicio
        }

    def dump_memoria(self, inicio=0, fim=16):
        """
        Exibe um trecho da memória de instruções (raw) para depuração.
        """
        print("\n=== DUMP memória de instruções (INST) ===")
        for i in range(inicio, min(fim, 32768)):
            print(f"{i:04X}: {self.mem_inst[i]:032b}")
    
    def asm_to_bin(self, texto):
        op_map = {v: k for k, v in self.opcodes.items()}

        linhas = texto.splitlines()
        limpas = []
        
        for linha in linhas:
            linha = linha.split('#')[0].strip()
            if linha:
                limpas.append(linha)

        program_bin = ''

        for linha in limpas:
            partes = [p.strip() for p in linha.replace(',', ' ').split()]
            instr = partes[0].lower()

            if instr == "address":
                if len(partes) < 2 or not partes[1].isdigit():
                    raise ValueError(f"Endereço inválido na instrução address: {linha}")
                program_bin += linha + '\n'
                continue 

            if instr not in op_map:
                raise ValueError(f"Instrução inválida: {instr}")

            opcode = op_map[instr].replace(' ','')
            bits = ['0'] * 32
            for i in range(8):
                bits[i] = opcode[i]

            # add/sub/xor/or/and/mult/div/cmp => 3 regs
            if instr in ['add', 'sub', 'xor', 'or', 'and', 'mult', 'div', 'cmp', 'lsl', 'lsr']:
                if len(partes) < 4:
                    raise ValueError(f"{instr} requer 3 registradores")

                rc = int(partes[1].replace('r',''))
                ra = int(partes[2].replace('r',''))
                rb = int(partes[3].replace('r',''))

                ra_bin = f"{ra:08b}"
                rb_bin = f"{rb:08b}"
                rc_bin = f"{rc:08b}"

                for i in range(8):
                    bits[8+i]  = ra_bin[i]
                    bits[16+i] = rb_bin[i]
                    bits[24+i] = rc_bin[i]

            # inc/dec => 2 regs (ra e rc)
            elif instr in ['inc', 'dec']:
                if len(partes) < 2:
                    raise ValueError(f"{instr} requer 1 registradores")

                rc = int(partes[1].replace('r',''))
                rc_bin = f"{rc:08b}"

                for i in range(8):
                    bits[24+i] = rc_bin[i]

            # push ra
            elif instr == 'push':
                if len(partes) < 2:
                    raise ValueError("push requer 1 registrador")
                ra = int(partes[1].replace('r',''))
                ra_bin = f"{ra:08b}"
                for i in range(8):
                    bits[8+i] = ra_bin[i]
            
            elif instr == 'ret':
                if len(partes) < 1:
                    raise ValueError("ret requer 0 registrador")

            # pop -> pop rc
            elif instr == 'pop':
                if len(partes) < 2:
                    raise ValueError("pop requer 1 registrador (rc)")
                rc = int(partes[1].replace('r',''))
                rc_bin = f"{rc:08b}"
                for i in range(8):
                    bits[16+i] = rc_bin[i]  # alguns ISAs usam 16, outros 8. Mantive assim pq seu padrão já usou esse campo

            # call/jal/j -> 24 bits de addr
            elif instr in ['call', 'jal', 'j']:
                if len(partes) < 2:
                    raise ValueError(f"{instr} requer endereço")
                addr = int(partes[1])
                addr_bin = f"{addr:024b}"
                for i in range(24):
                    bits[8+i] = addr_bin[i]

            # jr ra
            elif instr == 'jr':
                if len(partes) < 2:
                    raise ValueError("jr requer 1 registrador (ra)")
                ra = int(partes[1].replace('r',''))
                ra_bin = f"{ra:08b}"
                for i in range(8):
                    bits[8+i] = ra_bin[i]

            elif instr == 'passnota':
                if len(partes) < 3:
                    raise ValueError("passnota requer 2 registradores (ra) e (rc)")
                rc = int(partes[1].replace('r',''))
                ra = int(partes[2].replace('r',''))
                ra_bin = f"{ra:08b}"
                rc_bin = f"{rc:08b}"

                for i in range(8):
                    bits[8+i] = ra_bin[i]
                    bits[24+i] = rc_bin[i]

            # bne/beq -> 2 regs + endereço 8 bits final
            elif instr in ['bne', 'beq']:
                if len(partes) < 4:
                    raise ValueError(f"{instr} requer ra, rb, end")
                ra = int(partes[1].replace('r',''))
                rb = int(partes[2].replace('r',''))
                addr = int(partes[3])

                ra_bin = f"{ra:08b}"
                rb_bin = f"{rb:08b}"
                addr_bin = f"{addr:08b}"
                for i in range(8):
                    bits[8+i]  = ra_bin[i]
                    bits[16+i] = rb_bin[i]
                for i in range(8):
                    bits[24+i] = addr_bin[i]

            # halt -> 32 bits 1
            elif instr == 'halt':
                bits = ['1'] * 32

            # zeros (somente RC)
            elif instr == 'zeros':
                if len(partes) < 2:
                    raise ValueError("zeros requer 1 registrador (rc)")
                rc = int(partes[1].replace('r',''))
                rc_bin = f"{rc:08b}"
                for i in range(8):
                    bits[24+i] = rc_bin[i]

            # passa ra→rc (2 fields)
            elif instr == 'passa':
                if len(partes) < 3:
                    raise ValueError("passa requer rc, ra")
                rc = int(partes[1].replace('r',''))
                ra = int(partes[2].replace('r',''))

                ra_bin = f"{ra:08b}"
                rc_bin = f"{rc:08b}"

                for i in range(8):
                    bits[8+i]  = ra_bin[i]
                    bits[16+i] = '0'
                    bits[24+i] = rc_bin[i]

            # load rc, ra  -> rc = mem[ra]
            elif instr == 'load':
                if len(partes) < 3:
                    raise ValueError("load requer rc, ra")
                rc = int(partes[1].replace('r',''))
                ra = int(partes[2].replace('r',''))

                rc_bin = f"{rc:08b}"
                ra_bin = f"{ra:08b}"

                for i in range(8):
                    bits[8+i] = ra_bin[i]
                for i in range(8):
                    bits[24+i] = rc_bin[i]

            # store ra, Rb  -> mem[Rb] = Ra
            elif instr == 'store':
                if len(partes) < 3:
                    raise ValueError("store requer ra, rb")
                ra = int(partes[1].replace('r',''))
                rc = int(partes[2].replace('r',''))

                ra_bin = f"{ra:08b}"
                rc_bin = f"{rc:08b}"

                for i in range(8):
                    bits[8+i] = ra_bin[i]
                for i in range(8):
                    bits[24+i] = rc_bin[i]
            
            elif instr == "lch":
                rc = int(partes[1][1:])  # remove 'R'
                const16 = int(partes[2])

                # Converte para binário
                const16_bin = f"{const16:016b}"  # 16 bits
                rc_bin = f"{rc:08b}"             # 8 bits

                # opcode já deve estar nos bits 0–7
                for i in range(16):
                    bits[8 + i] = const16_bin[i]  # bits 8–23
                for i in range(8):
                    bits[24 + i] = rc_bin[i]      # bits 24–31

            elif instr == "lcl":
                rc = int(partes[1][1:])
                const16 = int(partes[2])

                const16_bin = f"{const16:016b}"
                rc_bin = f"{rc:08b}"

                for i in range(16):
                    bits[8 + i] = const16_bin[i]
                for i in range(8):
                    bits[24 + i] = rc_bin[i]

            else:
                raise ValueError(f"Instrução sem handler: {instr}")

            program_bin += ''.join(bits) + "\n"

        return program_bin

    

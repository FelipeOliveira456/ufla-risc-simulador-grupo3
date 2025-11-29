# main.py
import sys
import os
from interpretador import Interpretador
from simulador import Simulador

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.asm|arquivo.bin>")
        return

    arquivo = sys.argv[1]
    ext = os.path.splitext(arquivo)[1].lower()

    try:
        with open(arquivo, "r") as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {arquivo}")
        return

    interp = Interpretador(verbose=True)

    # Se for ASM, converte e salva bin
    if ext == '.asm':
        print("\n🔧 Convertendo ASM → BIN...\n")
        bin_text = interp.asm_to_bin(texto)

        out_file = arquivo.replace('.asm', '.bin')
        with open(out_file, "w") as f:
            f.write(bin_text)

        print(f"\n✅ Conversão concluída. BIN salvo em {out_file}\n")
        texto = bin_text  # passa para pipeline normal

    elif ext != '.bin':
        print("❌ Extensão não suportada! Use .asm ou .bin")
        return

    # Carrega instruções já em binário
    interp.carregar_arquivo(texto)

    mem_info = interp.exportar_memoria()
    mem_instr = mem_info['mem_instr']
    pc_start = mem_info['address_start']

    print(f"\nMemória de instruções carregada. Início do PC: {pc_start}\n")

    sim = Simulador(mem_instr, pc_start)
    sim.run(max_steps=1000)

    sim.dump_regs()
    sim.dump_mem_data()

    # Salva binário final se o usuário quiser atualizar

if __name__ == "__main__":
    main()

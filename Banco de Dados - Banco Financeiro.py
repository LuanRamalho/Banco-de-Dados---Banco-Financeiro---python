import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os

NOME_ARQUIVO = "clientes.json"

def carregar_dados():
    if not os.path.exists(NOME_ARQUIVO): return []
    with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []

def salvar_dados(dados):
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

class AppBanco:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Cliente")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f8ff")
        self.index_selecionado = None 
        self.criar_interface()

    def criar_interface(self):
        # --- CONTAINER PRINCIPAL ---
        self.main_container = tk.Frame(self.root, bg="#f0f8ff")
        self.main_container.pack(expand=True, fill="both", padx=50)

        # 1. Formulário de Cadastro (Centralizado)
        frame_form = tk.Frame(self.main_container, bg="#ffffff", padx=30, pady=20, bd=1, relief="groove")
        frame_form.pack(pady=20)

        labels = ["Nome do Cliente:", "Número da Agência:", "Número da Conta:", "Saldo Disponível:"]
        self.entries = []
        for i, text in enumerate(labels):
            tk.Label(frame_form, text=text, bg="#ffffff", font=("Arial", 10)).grid(row=i, column=0, sticky="e", pady=5)
            ent = tk.Entry(frame_form, width=35, font=("Arial", 10))
            ent.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(ent)
        
        self.entry_nome, self.entry_agencia, self.entry_conta, self.entry_saldo = self.entries

        btn_frame = tk.Frame(frame_form, bg="#ffffff")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Cadastrar Cliente", bg="#ff6347", fg="white", width=18, command=self.cadastrar_cliente).pack(side="left", padx=10)
        self.btn_salvar = tk.Button(btn_frame, text="Salvar Edição", bg="#32cd32", fg="white", width=18, state="disabled", command=self.salvar_edicao)
        self.btn_salvar.pack(side="left", padx=10)

        # 2. Barra de Busca (Centralizada)
        frame_busca = tk.Frame(self.main_container, bg="#f0f8ff")
        frame_busca.pack(fill="x", pady=10)
        
        inner_busca = tk.Frame(frame_busca, bg="#f0f8ff")
        inner_busca.pack()
        tk.Label(inner_busca, text="Buscar:", bg="#f0f8ff", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.entry_busca = tk.Entry(inner_busca, width=50, font=("Arial", 10))
        self.entry_busca.pack(side="left", padx=5)
        self.entry_busca.bind("<KeyRelease>", self.buscar_cliente)

        # 3. Área de Cartões com Scroll
        self.container_lista = tk.Frame(self.main_container, bg="#f0f8ff")
        self.container_lista.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(self.container_lista, bg="#f0f8ff", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container_lista, orient="vertical", command=self.canvas.yview)
        self.frame_cards = tk.Frame(self.canvas, bg="#f0f8ff")

        self.frame_cards.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((self.root.winfo_screenwidth()//4, 0), window=self.frame_cards, anchor="n")
        
        # Ajusta a largura dos cartões conforme o canvas muda
        self.canvas.bind("<Configure>", self.centralizar_canvas_window)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 4. Botões de Ação (Centralizados na Base)
        frame_acoes = tk.Frame(self.main_container, bg="#f0f8ff", pady=20)
        frame_acoes.pack(fill="x")
        
        inner_acoes = tk.Frame(frame_acoes, bg="#f0f8ff")
        inner_acoes.pack()
        
        botoes = [
            ("Saque", self.realizar_saque),
            ("Depósito", self.realizar_deposito),
            ("Editar", self.editar_cliente),
            ("Excluir", self.excluir_cliente)
        ]
        
        for texto, cmd in botoes:
            tk.Button(inner_acoes, text=texto, bg="#ff6347", fg="white", width=12, height=2, font=("Arial", 9, "bold"), command=cmd).pack(side="left", padx=10)

        self.carregar_tabela()

    def centralizar_canvas_window(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def carregar_tabela(self, lista_clientes=None):
        for widget in self.frame_cards.winfo_children(): widget.destroy()
        clientes = lista_clientes if lista_clientes is not None else carregar_dados()
        
        for idx, c in enumerate(clientes):
            cor_fundo = "#ffffff" if self.index_selecionado != idx else "#e1f5fe"
            card = tk.Frame(self.frame_cards, bg=cor_fundo, bd=1, relief="solid", padx=20, pady=15)
            card.pack(fill="x", pady=5, padx=100) # O padx aqui ajuda a manter o card centralizado e não muito largo
            
            card.bind("<Button-1>", lambda e, i=idx: self.selecionar_card(i))

            # Layout interno do card para ficar organizado
            tk.Label(card, text=f"Cliente: {c['nomeCliente']}", bg=cor_fundo, font=("Arial", 10, "bold"), width=25, anchor="w").grid(row=0, column=0)
            tk.Label(card, text=f"Agência: {c['agencia']}", bg=cor_fundo, width=15).grid(row=0, column=1)
            tk.Label(card, text=f"Conta: {c['conta']}", bg=cor_fundo, width=15).grid(row=0, column=2)
            tk.Label(card, text=f"Saldo: R$ {c['saldo']:.2f}", bg=cor_fundo, fg="#2e7d32", font=("Arial", 10, "bold"), width=15, anchor="e").grid(row=0, column=3)

            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, i=idx: self.selecionar_card(i))

    def selecionar_card(self, index):
        self.index_selecionado = index
        self.carregar_tabela()

    # --- Funções de Lógica (Mantidas e simplificadas) ---
    def cadastrar_cliente(self):
        try:
            dados = carregar_dados()
            dados.append({
                "nomeCliente": self.entry_nome.get(),
                "agencia": self.entry_agencia.get(),
                "conta": self.entry_conta.get(),
                "saldo": float(self.entry_saldo.get())
            })
            salvar_dados(dados)
            self.carregar_tabela()
            self.limpar_campos()
        except: messagebox.showerror("Erro", "Verifique os dados")

    def buscar_cliente(self, event=None):
        termo = self.entry_busca.get().lower()
        dados = carregar_dados()
        filtrados = [c for c in dados if termo in c["nomeCliente"].lower() or termo in c["agencia"] or termo in c["conta"]]
        self.carregar_tabela(filtrados)

    def realizar_saque(self):
        if self.index_selecionado is None: return
        valor = float(simpledialog.askstring("Saque", "Valor:"))
        dados = carregar_dados()
        if valor <= dados[self.index_selecionado]["saldo"]:
            dados[self.index_selecionado]["saldo"] -= valor
            salvar_dados(dados)
            self.carregar_tabela()
        else: messagebox.showerror("Erro", "Saldo insuficiente")

    def realizar_deposito(self):
        if self.index_selecionado is None: return
        valor = float(simpledialog.askstring("Depósito", "Valor:"))
        dados = carregar_dados()
        dados[self.index_selecionado]["saldo"] += valor
        salvar_dados(dados)
        self.carregar_tabela()

    def editar_cliente(self):
        if self.index_selecionado is None: return
        cliente = carregar_dados()[self.index_selecionado]
        self.limpar_campos()
        self.entry_nome.insert(0, cliente["nomeCliente"])
        self.entry_agencia.insert(0, cliente["agencia"])
        self.entry_conta.insert(0, cliente["conta"])
        self.entry_saldo.insert(0, cliente["saldo"])
        self.btn_salvar.config(state="normal")

    def salvar_edicao(self):
        dados = carregar_dados()
        dados[self.index_selecionado] = {
            "nomeCliente": self.entry_nome.get(),
            "agencia": self.entry_agencia.get(),
            "conta": self.entry_conta.get(),
            "saldo": float(self.entry_saldo.get())
        }
        salvar_dados(dados)
        self.btn_salvar.config(state="disabled")
        self.carregar_tabela()
        self.limpar_campos()

    def excluir_cliente(self):
        if self.index_selecionado is None: return
        dados = carregar_dados()
        del dados[self.index_selecionado]
        salvar_dados(dados)
        self.index_selecionado = None
        self.carregar_tabela()

    def limpar_campos(self):
        for ent in self.entries: ent.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppBanco(root)
    root.mainloop()

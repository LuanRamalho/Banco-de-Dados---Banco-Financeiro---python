import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os

# Nome do arquivo de banco de dados NoSQL
NOME_ARQUIVO = "clientes.json"

def carregar_dados():
    if not os.path.exists(NOME_ARQUIVO):
        return []
    with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_dados(dados):
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

class AppBanco:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Cliente")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f8ff")

        self.index_edicao = None 
        self.criar_interface()

    def criar_interface(self):
        # Formulário de Cadastro
        frame_form = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        frame_form.pack(pady=20)

        tk.Label(frame_form, text="Nome do Cliente:", bg="#ffffff").grid(row=0, column=0, sticky="e")
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Número da Agência:", bg="#ffffff").grid(row=1, column=0, sticky="e")
        self.entry_agencia = tk.Entry(frame_form, width=30)
        self.entry_agencia.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Número da Conta:", bg="#ffffff").grid(row=2, column=0, sticky="e")
        self.entry_conta = tk.Entry(frame_form, width=30)
        self.entry_conta.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame_form, text="Saldo Disponível:", bg="#ffffff").grid(row=3, column=0, sticky="e")
        self.entry_saldo = tk.Entry(frame_form, width=30)
        self.entry_saldo.grid(row=3, column=1, padx=10, pady=5)

        btn_cadastrar = tk.Button(frame_form, text="Cadastrar Cliente", bg="#ff6347", fg="white", command=self.cadastrar_cliente)
        btn_cadastrar.grid(row=4, column=0, pady=10, padx=5)

        self.btn_salvar = tk.Button(frame_form, text="Salvar Edição", bg="#32cd32", fg="white", command=self.salvar_edicao)
        self.btn_salvar.grid(row=4, column=1, pady=10, padx=5)
        self.btn_salvar.config(state="disabled")

        # Barra de Busca
        frame_busca = tk.Frame(self.root, bg="#f0f8ff")
        frame_busca.pack(pady=10)

        tk.Label(frame_busca, text="Buscar:", bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.entry_busca = tk.Entry(frame_busca, width=40)
        self.entry_busca.grid(row=0, column=1, padx=5)
        self.entry_busca.bind("<KeyRelease>", self.buscar_cliente)

        # Tabela (Sem a coluna ID)
        self.tabela = ttk.Treeview(self.root, columns=("Nome", "Agência", "Conta", "Saldo"), show="headings")
        self.tabela.heading("Nome", text="Nome do Cliente")
        self.tabela.heading("Agência", text="Número da Agência")
        self.tabela.heading("Conta", text="Número da Conta")
        self.tabela.heading("Saldo", text="Saldo Disponível")
        self.tabela.pack(pady=10)

        frame_acoes = tk.Frame(self.root, bg="#f0f8ff")
        frame_acoes.pack()

        tk.Button(frame_acoes, text="Saque", bg="#ff6347", fg="white", command=self.realizar_saque).grid(row=0, column=0, padx=10)
        tk.Button(frame_acoes, text="Depósito", bg="#ff6347", fg="white", command=self.realizar_deposito).grid(row=0, column=1, padx=10)
        tk.Button(frame_acoes, text="Editar", bg="#ff6347", fg="white", command=self.editar_cliente).grid(row=0, column=2, padx=10)
        tk.Button(frame_acoes, text="Excluir", bg="#ff6347", fg="white", command=self.excluir_cliente).grid(row=0, column=3, padx=10)

        self.carregar_tabela()

    def cadastrar_cliente(self):
        dados = carregar_dados()
        try:
            novo_cliente = {
                "nomeCliente": self.entry_nome.get(),
                "agencia": self.entry_agencia.get(),
                "conta": self.entry_conta.get(),
                "saldo": float(self.entry_saldo.get())
            }
            dados.append(novo_cliente)
            salvar_dados(dados)
            self.carregar_tabela()
            self.limpar_campos()
        except ValueError:
            messagebox.showerror("Erro", "Saldo deve ser numérico")

    def carregar_tabela(self, lista_clientes=None):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        clientes = lista_clientes if lista_clientes is not None else carregar_dados()
        for c in clientes:
            self.tabela.insert("", "end", values=(c["nomeCliente"], c["agencia"], c["conta"], f"R$ {c['saldo']:.2f}"))

    def buscar_cliente(self, event=None):
        termo = self.entry_busca.get().lower()
        dados = carregar_dados()
        filtrados = [c for c in dados if termo in c["nomeCliente"].lower() or termo in c["agencia"] or termo in c["conta"]]
        self.carregar_tabela(filtrados)

    def obter_index_selecionado(self):
        selecao = self.tabela.selection()
        if not selecao:
            return None
        # O Treeview não tem ID agora, então usamos o índice da linha na tabela
        item = selecao[0]
        return self.tabela.index(item)

    def realizar_saque(self):
        idx = self.obter_index_selecionado()
        if idx is None: return
        
        valor = float(simpledialog.askstring("Saque", "Valor:"))
        dados = carregar_dados()
        if valor <= dados[idx]["saldo"]:
            dados[idx]["saldo"] -= valor
            salvar_dados(dados)
            self.carregar_tabela()
        else:
            messagebox.showerror("Erro", "Saldo insuficiente")

    def realizar_deposito(self):
        idx = self.obter_index_selecionado()
        if idx is None: return
        
        valor = float(simpledialog.askstring("Depósito", "Valor:"))
        dados = carregar_dados()
        dados[idx]["saldo"] += valor
        salvar_dados(dados)
        self.carregar_tabela()

    def editar_cliente(self):
        idx = self.obter_index_selecionado()
        if idx is None: return
        
        dados = carregar_dados()
        cliente = dados[idx]
        
        self.limpar_campos()
        self.entry_nome.insert(0, cliente["nomeCliente"])
        self.entry_agencia.insert(0, cliente["agencia"])
        self.entry_conta.insert(0, cliente["conta"])
        self.entry_saldo.insert(0, cliente["saldo"])
        
        self.index_edicao = idx
        self.btn_salvar.config(state="normal")

    def salvar_edicao(self):
        dados = carregar_dados()
        try:
            dados[self.index_edicao] = {
                "nomeCliente": self.entry_nome.get(),
                "agencia": self.entry_agencia.get(),
                "conta": self.entry_conta.get(),
                "saldo": float(self.entry_saldo.get())
            }
            salvar_dados(dados)
            self.index_edicao = None
            self.btn_salvar.config(state="disabled")
            self.carregar_tabela()
            self.limpar_campos()
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos")

    def excluir_cliente(self):
        idx = self.obter_index_selecionado()
        if idx is None: return
        
        dados = carregar_dados()
        del dados[idx]
        salvar_dados(dados)
        self.carregar_tabela()

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_agencia.delete(0, tk.END)
        self.entry_conta.delete(0, tk.END)
        self.entry_saldo.delete(0, tk.END)

root = tk.Tk()
app = AppBanco(root)
root.mainloop()

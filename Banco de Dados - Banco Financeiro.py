import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

# Conexão com o banco de dados SQLite
conexao = sqlite3.connect("clientes_banco.db")
cursor = conexao.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nomeCliente TEXT NOT NULL,
                    agencia TEXT NOT NULL,
                    conta TEXT NOT NULL,
                    saldo REAL NOT NULL
                )''')
conexao.commit()

class AppBanco:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Cliente do Banco")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f8ff")

        self.cliente_id = None  # Armazena o ID do cliente em edição
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

        # Botão de Salvar Edição
        self.btn_salvar = tk.Button(frame_form, text="Salvar Edição", bg="#32cd32", fg="white", command=self.salvar_edicao)
        self.btn_salvar.grid(row=4, column=1, pady=10, padx=5)
        self.btn_salvar.config(state="disabled")  # Inicia desabilitado

        # Barra de Busca
        frame_busca = tk.Frame(self.root, bg="#f0f8ff")
        frame_busca.pack(pady=10)

        tk.Label(frame_busca, text="Buscar:", bg="#f0f8ff").grid(row=0, column=0, padx=5)
        self.entry_busca = tk.Entry(frame_busca, width=40)
        self.entry_busca.grid(row=0, column=1, padx=5)
        self.entry_busca.bind("<KeyRelease>", self.buscar_cliente)

        # Tabela de Clientes
        self.tabela = ttk.Treeview(self.root, columns=("ID", "Nome", "Agência", "Conta", "Saldo"), show="headings")
        self.tabela.heading("ID", text="ID")
        self.tabela.heading("Nome", text="Nome do Cliente")
        self.tabela.heading("Agência", text="Número da Agência")
        self.tabela.heading("Conta", text="Número da Conta")
        self.tabela.heading("Saldo", text="Saldo Disponível")
        self.tabela.column("ID", width=50)
        self.tabela.pack(pady=10)

        # Botões para ações em clientes
        frame_acoes = tk.Frame(self.root, bg="#f0f8ff")
        frame_acoes.pack()

        btn_saque = tk.Button(frame_acoes, text="Saque", bg="#ff6347", fg="white", command=self.realizar_saque)
        btn_saque.grid(row=0, column=0, padx=10)
        btn_deposito = tk.Button(frame_acoes, text="Depósito", bg="#ff6347", fg="white", command=self.realizar_deposito)
        btn_deposito.grid(row=0, column=1, padx=10)
        btn_editar = tk.Button(frame_acoes, text="Editar", bg="#ff6347", fg="white", command=self.editar_cliente)
        btn_editar.grid(row=0, column=2, padx=10)
        btn_excluir = tk.Button(frame_acoes, text="Excluir", bg="#ff6347", fg="white", command=self.excluir_cliente)
        btn_excluir.grid(row=0, column=3, padx=10)

        # Carregar dados iniciais
        self.carregar_clientes()

    def cadastrar_cliente(self):
        nome = self.entry_nome.get()
        agencia = self.entry_agencia.get()
        conta = self.entry_conta.get()
        try:
            saldo = float(self.entry_saldo.get())
        except ValueError:
            messagebox.showerror("Erro", "Saldo deve ser um valor numérico")
            return

        cursor.execute("INSERT INTO clientes (nomeCliente, agencia, conta, saldo) VALUES (?, ?, ?, ?)",
                       (nome, agencia, conta, saldo))
        conexao.commit()
        self.carregar_clientes()

    def carregar_clientes(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        cursor.execute("SELECT * FROM clientes")
        for row in cursor.fetchall():
            self.tabela.insert("", "end", values=(row[0], row[1], row[2], row[3], f"R$ {row[4]:.2f}"))

    def buscar_cliente(self, event=None):
        termo_busca = self.entry_busca.get()
        consulta = f"%{termo_busca}%"
        cursor.execute("SELECT * FROM clientes WHERE nomeCliente LIKE ? OR agencia LIKE ? OR conta LIKE ?", (consulta, consulta, consulta))
        self.carregar_clientes()

    def realizar_saque(self):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            messagebox.showwarning("Selecione um Cliente", "Por favor, selecione um cliente para realizar o saque.")
            return

        cliente_id = self.tabela.item(item_selecionado[0])["values"][0]
        valor_saque = float(tk.simpledialog.askstring("Saque", "Digite o valor do saque:"))

        cursor.execute("SELECT saldo FROM clientes WHERE id = ?", (cliente_id,))
        saldo_atual = cursor.fetchone()[0]

        if valor_saque > saldo_atual:
            messagebox.showerror("Erro", "Saldo insuficiente.")
            return

        novo_saldo = saldo_atual - valor_saque
        cursor.execute("UPDATE clientes SET saldo = ? WHERE id = ?", (novo_saldo, cliente_id))
        conexao.commit()
        self.carregar_clientes()
        messagebox.showinfo("Sucesso", "Saque realizado com sucesso!")

    def realizar_deposito(self):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            messagebox.showwarning("Selecione um Cliente", "Por favor, selecione um cliente para realizar o depósito.")
            return

        cliente_id = self.tabela.item(item_selecionado[0])["values"][0]
        valor_deposito = float(tk.simpledialog.askstring("Depósito", "Digite o valor do depósito:"))

        cursor.execute("SELECT saldo FROM clientes WHERE id = ?", (cliente_id,))
        saldo_atual = cursor.fetchone()[0]

        novo_saldo = saldo_atual + valor_deposito
        cursor.execute("UPDATE clientes SET saldo = ? WHERE id = ?", (novo_saldo, cliente_id))
        conexao.commit()
        self.carregar_clientes()
        messagebox.showinfo("Sucesso", "Depósito realizado com sucesso!")

    def editar_cliente(self):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            messagebox.showwarning("Selecione um Cliente", "Por favor, selecione um cliente para editar.")
            return

        cliente_id = self.tabela.item(item_selecionado[0])["values"][0]
        cliente_dados = self.tabela.item(item_selecionado[0])["values"]
        
        # Preenche os campos do formulário com os dados do cliente selecionado
        self.entry_nome.delete(0, tk.END)
        self.entry_agencia.delete(0, tk.END)
        self.entry_conta.delete(0, tk.END)
        self.entry_saldo.delete(0, tk.END)
        
        self.entry_nome.insert(0, cliente_dados[1])
        self.entry_agencia.insert(0, cliente_dados[2])
        self.entry_conta.insert(0, cliente_dados[3])
        self.entry_saldo.insert(0, cliente_dados[4])

        self.cliente_id = cliente_id  # Armazena o ID do cliente para edição
        self.btn_salvar.config(state="normal")

    def salvar_edicao(self):
        if not self.cliente_id:
            messagebox.showwarning("Nenhum Cliente em Edição", "Nenhum cliente está selecionado para edição.")
            return
        
        nome = self.entry_nome.get()
        agencia = self.entry_agencia.get()
        conta = self.entry_conta.get()
        try:
            saldo = float(self.entry_saldo.get())
        except ValueError:
            messagebox.showerror("Erro", "Saldo deve ser um valor numérico")
            return

        cursor.execute("UPDATE clientes SET nomeCliente = ?, agencia = ?, conta = ?, saldo = ? WHERE id = ?",
                       (nome, agencia, conta, saldo, self.cliente_id))
        conexao.commit()
        self.cliente_id = None
        self.btn_salvar.config(state="disabled")
        self.carregar_clientes()
        messagebox.showinfo("Sucesso", "Dados do cliente atualizados com sucesso!")

    def excluir_cliente(self):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            messagebox.showwarning("Selecione um Cliente", "Por favor, selecione um cliente para excluir.")
            return

        cliente_id = self.tabela.item(item_selecionado[0])["values"][0]
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conexao.commit()
        self.carregar_clientes()
        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

# Configuração da janela principal
root = tk.Tk()
app = AppBanco(root)
root.mainloop()

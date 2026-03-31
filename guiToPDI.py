import operator
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog


class ImageOperationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Operações")
        self.root.geometry("460x320")
        self.root.eval('tk::PlaceWindow . center')
        
        self.dicionario_operacoes = {
            "Soma": operator.add,
            "Subtração": operator.sub,
            "Multiplicação": operator.mul,
            "Divisão": operator.truediv,
            "AND": operator.and_,
            "OR": operator.or_,
            "XOR": operator.xor
        }
        
        self.imagem1 = None
        self.imagem2 = None
        
        self._criar_widgets()
    
    def _criar_widgets(self):
        """Cria todos os widgets da interface"""
        tk.Label(self.root, text="Escolha a operação:", font=("Arial", 11)).pack(pady=15)
        
        self.label_img1 = tk.Label(self.root, text="Imagem 1: nao selecionada", font=("Arial", 9))
        self.label_img1.pack()
        
        self.label_img2 = tk.Label(self.root, text="Imagem 2: nao selecionada", font=("Arial", 9))
        self.label_img2.pack(pady=(0, 8))
        
        frame_botoes = tk.Frame(self.root)
        frame_botoes.pack(pady=(0, 8))
        
        tk.Button(frame_botoes, text="Selecionar Imagem 1", command=lambda: self.selecionar_imagem(1)).pack(side="left", padx=6)
        tk.Button(frame_botoes, text="Selecionar Imagem 2", command=lambda: self.selecionar_imagem(2)).pack(side="left", padx=6)
        
        self.combo_operacoes = ttk.Combobox(self.root, values=list(self.dicionario_operacoes.keys()), state="readonly", width=20)
        self.combo_operacoes.set("Selecione...")
        self.combo_operacoes.pack(pady=5)
        
        btn_executar = tk.Button(self.root, text="Gerar Resultado", command=self.aplicar_operacao, bg="#212F22", fg="white", font=("Arial", 10, "bold"))
        btn_executar.pack(pady=15)
    
    def selecionar_imagem(self, alvo):
        """Seleciona uma imagem do disco"""
        from implementacaoPrimeiraUnidade import Image
        
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
        
        try:
            nova_imagem = Image(caminho)
        except Exception as erro:
            messagebox.showerror("Erro", f"Nao foi possivel carregar a imagem.\n{erro}")
            return
        
        if alvo == 1:
            self.imagem1 = nova_imagem
            self.label_img1.config(text=f"Imagem 1: {Path(self.imagem1.imageName).name}")
        else:
            self.imagem2 = nova_imagem
            self.label_img2.config(text=f"Imagem 2: {Path(self.imagem2.imageName).name}")
        
        if self.imagem1 is not None and self.imagem2 is not None:
            self.imagem2.resizeImage(self.imagem1.largura, self.imagem1.altura)
    
    def aplicar_operacao(self):
        """Aplica a operação escolhida nas duas imagens"""
        from implementacaoPrimeiraUnidade import ImageOperation
        
        operacao_escolhida = self.combo_operacoes.get()
        
        if self.imagem1 is None or self.imagem2 is None:
            messagebox.showwarning("Aviso", "Selecione as duas imagens antes de gerar o resultado.")
            return
        
        if operacao_escolhida not in self.dicionario_operacoes:
            messagebox.showwarning("Aviso", "Selecione uma operação válida.")
            return
        
        self.imagem2.resizeImage(self.imagem1.largura, self.imagem1.altura)
        
        resultado = ImageOperation(self.imagem1, self.imagem2, self.dicionario_operacoes[operacao_escolhida]).result
        resultado.showImage()
    
    def run(self):
        """Inicia a interface"""
        self.root.mainloop()

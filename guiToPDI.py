import cv2
import operator
import tkinter as tk
import numpy as np
from pathlib import Path
from tkinter import ttk, messagebox, filedialog


class ImageOperationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Operações e Transformações")
        self.root.geometry("600x700")
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
        self.imagem_transformacao = None
        self.transformador = None
        self.nome_janela_transformacao = "Transformacao"
        self.largura_canvas_transformacao = 800
        self.altura_canvas_transformacao = 800
        self.cor_fundo_canvas = (230, 230, 230)
        
        # Variáveis para os parâmetros de transformação
        self.rotacao_valor = tk.DoubleVar(value=0)
        self.transladx_valor = tk.DoubleVar(value=0)
        self.translady_valor = tk.DoubleVar(value=0)
        self.escalax_valor = tk.DoubleVar(value=1.0)
        self.escalay_valor = tk.DoubleVar(value=1.0)
        self.cisalhox_valor = tk.DoubleVar(value=0)
        self.cisalhoy_valor = tk.DoubleVar(value=0)
        self.reflexao_valor = tk.StringVar(value="Nenhuma")
        
        self._criar_widgets()
    
    def _criar_widgets(self):
        """Cria todos os widgets da interface com abas"""
        # Notebook (abas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba 1: Operações entre imagens
        frame_operacoes = ttk.Frame(notebook)
        notebook.add(frame_operacoes, text="Operações entre Imagens")
        self._criar_aba_operacoes(frame_operacoes)
        
        # Aba 2: Transformações
        frame_transformacoes = ttk.Frame(notebook)
        notebook.add(frame_transformacoes, text="Transformações")
        self._criar_aba_transformacoes(frame_transformacoes)
    
    def _criar_aba_operacoes(self, parent):
        """Cria a aba de operações entre duas imagens"""
        tk.Label(parent, text="Escolha a operação:", font=("Arial", 11)).pack(pady=15)
        
        self.label_img1 = tk.Label(parent, text="Imagem 1: nao selecionada", font=("Arial", 9))
        self.label_img1.pack()
        
        self.label_img2 = tk.Label(parent, text="Imagem 2: nao selecionada", font=("Arial", 9))
        self.label_img2.pack(pady=(0, 8))
        
        frame_botoes = tk.Frame(parent)
        frame_botoes.pack(pady=(0, 8))
        
        tk.Button(frame_botoes, text="Selecionar Imagem 1", command=lambda: self.selecionar_imagem(1)).pack(side="left", padx=6)
        tk.Button(frame_botoes, text="Selecionar Imagem 2", command=lambda: self.selecionar_imagem(2)).pack(side="left", padx=6)
        
        self.combo_operacoes = ttk.Combobox(parent, values=list(self.dicionario_operacoes.keys()), state="readonly", width=20)
        self.combo_operacoes.set("Selecione...")
        self.combo_operacoes.pack(pady=5)
        
        btn_executar = tk.Button(parent, text="Gerar Resultado", command=self.aplicar_operacao, bg="#212F22", fg="white", font=("Arial", 10, "bold"))
        btn_executar.pack(pady=15)
    
    def _criar_aba_transformacoes(self, parent):
        """Cria a aba de transformações com sliders"""
        # Seleção de imagem para transformação
        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)
        
        tk.Label(frame_selecao, text="Imagem para transformar:", font=("Arial", 10)).pack(side="left", padx=5)
        self.label_img_transform = tk.Label(frame_selecao, text="nao selecionada", font=("Arial", 9), foreground="red")
        self.label_img_transform.pack(side="left", padx=5)
        
        tk.Button(frame_selecao, text="Selecionar Imagem", command=self.selecionar_imagem_transformacao).pack(side="left", padx=5)
        
        # Frame com scrollbar para os sliders
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Adicionar sliders
        self._adicionar_slider(scrollable_frame, "Rotação", self.rotacao_valor, 0, 360, 1)
        self._adicionar_slider(scrollable_frame, "Translação X", self.transladx_valor, -100, 100, 1)
        self._adicionar_slider(scrollable_frame, "Translação Y", self.translady_valor, -100, 100, 1)
        self._adicionar_slider(scrollable_frame, "Escala X", self.escalax_valor, 0.5, 2.0, 0.1)
        self._adicionar_slider(scrollable_frame, "Escala Y", self.escalay_valor, 0.5, 2.0, 0.1)
        self._adicionar_slider(scrollable_frame, "Cisalhamento X", self.cisalhox_valor, -0.5, 0.5, 0.05)
        self._adicionar_slider(scrollable_frame, "Cisalhamento Y", self.cisalhoy_valor, -0.5, 0.5, 0.05)

        frame_reflexao = tk.Frame(scrollable_frame)
        frame_reflexao.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_reflexao, text="Reflexão", width=15, font=("Arial", 9)).pack(side="left")
        combo_reflexao = ttk.Combobox(
            frame_reflexao,
            values=["Nenhuma", "Eixo X", "Eixo Y", "Ambos"],
            state="readonly",
            width=20,
            textvariable=self.reflexao_valor,
        )
        combo_reflexao.pack(side="left", padx=5)
        combo_reflexao.bind("<<ComboboxSelected>>", lambda _event: self.atualizar_transformacao())
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de controle
        frame_botoes = tk.Frame(parent)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Resetar", command=self.resetar_transformacoes, bg="#FF6B6B", fg="white").pack(side="left", padx=5)
    
    def _adicionar_slider(self, parent, label_text, var, from_val, to_val, resolution):
        """Adiciona um slider com rótulo e valor"""
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame, text=label_text, width=15, font=("Arial", 9)).pack(side="left")
        
        slider = ttk.Scale(frame, from_=from_val, to=to_val, orient="horizontal", 
                          variable=var, command=lambda _: self.atualizar_transformacao())
        slider.pack(side="left", fill="x", expand=True, padx=5)
        
        valor_label = tk.Label(frame, text=f"{var.get():.2f}", width=8, font=("Arial", 9))
        valor_label.pack(side="left", padx=5)
        
        # Atualizar o rótulo do valor quando o slider muda
        def atualizar_label(*args):
            valor_label.config(text=f"{var.get():.2f}")
        
        var.trace("w", atualizar_label)
    
    def selecionar_imagem_transformacao(self):
        """Seleciona uma imagem para transformação"""
        from implementacaoPrimeiraUnidade import Image, ImageTransformer
        
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
        
        try:
            cv2.destroyWindow(self.nome_janela_transformacao)
        except cv2.error:
            pass

        try:
            self.imagem_transformacao = Image(caminho)
            self.transformador = ImageTransformer(self.imagem_transformacao)

            base_altura, base_largura = self.imagem_transformacao.image.shape[:2]
            self.largura_canvas_transformacao = max(350, base_largura * 3)
            self.altura_canvas_transformacao = max(350, base_altura * 3)

            cv2.namedWindow(self.nome_janela_transformacao, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(
                self.nome_janela_transformacao,
                self.largura_canvas_transformacao,
                self.altura_canvas_transformacao,
            )

            self.label_img_transform.config(text=Path(caminho).name, foreground="green")
            self.resetar_transformacoes()
        except Exception as erro:
            messagebox.showerror("Erro", f"Nao foi possivel carregar a imagem.\n{erro}")

    def _valor_borda(self, imagem):
        if imagem.ndim == 2:
            return self.cor_fundo_canvas[0]
        return self.cor_fundo_canvas

    def _criar_canvas_base_transformacao(self):
        imagem = self.imagem_transformacao.image
        if imagem.ndim == 2:
            canvas = np.full(
                (self.altura_canvas_transformacao, self.largura_canvas_transformacao),
                self.cor_fundo_canvas[0],
                dtype=np.uint8,
            )
        else:
            canvas = np.full(
                (self.altura_canvas_transformacao, self.largura_canvas_transformacao, 3),
                self.cor_fundo_canvas,
                dtype=np.uint8,
            )

        altura_img, largura_img = imagem.shape[:2]
        x_ini = max(0, (self.largura_canvas_transformacao - largura_img) // 2)
        y_ini = max(0, (self.altura_canvas_transformacao - altura_img) // 2)

        x_fim = min(self.largura_canvas_transformacao, x_ini + largura_img)
        y_fim = min(self.altura_canvas_transformacao, y_ini + altura_img)

        src_x_fim = x_fim - x_ini
        src_y_fim = y_fim - y_ini

        canvas[y_ini:y_fim, x_ini:x_fim] = imagem[0:src_y_fim, 0:src_x_fim]
        return canvas

    def _renderizar_em_canvas(self, imagem):
        """Renderiza a imagem transformada em um canvas fixo com fundo claro."""
        if imagem.ndim == 2:
            canvas = np.full(
                (self.altura_canvas_transformacao, self.largura_canvas_transformacao),
                self.cor_fundo_canvas[0],
                dtype=np.uint8,
            )
        else:
            canvas = np.full(
                (self.altura_canvas_transformacao, self.largura_canvas_transformacao, 3),
                self.cor_fundo_canvas,
                dtype=np.uint8,
            )

        altura_img, largura_img = imagem.shape[:2]
        offset_x = (self.largura_canvas_transformacao - largura_img) // 2
        offset_y = (self.altura_canvas_transformacao - altura_img) // 2

        src_x_ini = 0
        src_y_ini = 0
        dst_x_ini = max(0, offset_x)
        dst_y_ini = max(0, offset_y)

        if offset_x < 0:
            src_x_ini = -offset_x
        if offset_y < 0:
            src_y_ini = -offset_y

        largura_colada = min(
            largura_img - src_x_ini,
            self.largura_canvas_transformacao - dst_x_ini,
        )
        altura_colada = min(
            altura_img - src_y_ini,
            self.altura_canvas_transformacao - dst_y_ini,
        )

        if largura_colada > 0 and altura_colada > 0:
            canvas[
                dst_y_ini:dst_y_ini + altura_colada,
                dst_x_ini:dst_x_ini + largura_colada,
            ] = imagem[
                src_y_ini:src_y_ini + altura_colada,
                src_x_ini:src_x_ini + largura_colada,
            ]

        return canvas
    
    def atualizar_transformacao(self):
        """Atualiza a transformação em tempo real baseado nos sliders"""
        if self.imagem_transformacao is None:
            return

        mapa_reflexao = {
            "Nenhuma": "nenhum",
            "Eixo X": "x",
            "Eixo Y": "y",
            "Ambos": "ambos",
        }
        
        imagem_temp = self._criar_canvas_base_transformacao()
        altura, largura = imagem_temp.shape[:2]
        centro_x = largura / 2.0
        centro_y = altura / 2.0
        borda = self._valor_borda(imagem_temp)

        matriz_rotacao = cv2.getRotationMatrix2D((centro_x, centro_y), self.rotacao_valor.get(), 1.0)
        imagem_temp = cv2.warpAffine(
            imagem_temp,
            matriz_rotacao,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=borda,
        )

        matriz_translacao = np.float32([
            [1, 0, int(self.transladx_valor.get())],
            [0, 1, int(self.translady_valor.get())],
        ])
        imagem_temp = cv2.warpAffine(
            imagem_temp,
            matriz_translacao,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=borda,
        )

        escala_x = self.escalax_valor.get()
        escala_y = self.escalay_valor.get()
        matriz_escala = np.float32([
            [escala_x, 0, centro_x * (1 - escala_x)],
            [0, escala_y, centro_y * (1 - escala_y)],
        ])
        imagem_temp = cv2.warpAffine(
            imagem_temp,
            matriz_escala,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=borda,
        )

        cisalhamento_x = self.cisalhox_valor.get()
        cisalhamento_y = self.cisalhoy_valor.get()
        matriz_cisalhamento = np.float32([
            [1, cisalhamento_x, -cisalhamento_x * centro_y],
            [cisalhamento_y, 1, -cisalhamento_y * centro_x],
        ])
        imagem_temp = cv2.warpAffine(
            imagem_temp,
            matriz_cisalhamento,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=borda,
        )

        reflexao = mapa_reflexao[self.reflexao_valor.get()]
        if reflexao == "x":
            imagem_temp = cv2.flip(imagem_temp, 0)
        elif reflexao == "y":
            imagem_temp = cv2.flip(imagem_temp, 1)
        elif reflexao == "ambos":
            imagem_temp = cv2.flip(imagem_temp, -1)

        cv2.imshow(self.nome_janela_transformacao, imagem_temp)
        cv2.resizeWindow(
            self.nome_janela_transformacao,
            self.largura_canvas_transformacao,
            self.altura_canvas_transformacao,
        )
        cv2.waitKey(1)
    
    def aplicar_transformacoes(self):
        """Aplica todas as transformações e salva o resultado"""
        if self.transformador is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem para transformar.")
            return
        
        self.atualizar_transformacao()
    
    def resetar_transformacoes(self):
        """Reseta todos os sliders para seus valores padrão"""
        self.rotacao_valor.set(0)
        self.transladx_valor.set(0)
        self.translady_valor.set(0)
        self.escalax_valor.set(1.0)
        self.escalay_valor.set(1.0)
        self.cisalhox_valor.set(0)
        self.cisalhoy_valor.set(0)
        self.reflexao_valor.set("Nenhuma")
        
        if self.transformador is not None:
            self.atualizar_transformacao()
    
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
            if self.imagem1 is not None:
                cv2.destroyWindow(self.imagem1.imageName)
            
            self.imagem1 = nova_imagem
            self.imagem1.showImage()
            self.label_img1.config(text=f"Imagem 1: {Path(self.imagem1.imageName).name}")
        else:
            if self.imagem2 is not None:
                cv2.destroyWindow(self.imagem2.imageName)
            
            self.imagem2 = nova_imagem
            self.imagem2.showImage()
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

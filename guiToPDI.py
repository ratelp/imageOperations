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
        self.modo_transformacao = tk.StringVar(value="individual")
        self.opcoes_transformacoes_compostas = [
            "Rotação",
            "Translação",
            "Escala",
            "Cisalhamento",
            "Reflexão",
            "Zoom in - Replicação",
            "Zoom in - Interpolação",
            "Zoom out - Exclusão",
            "Zoom out - Valor médio",
        ]
        self.transformacao_para_adicionar = tk.StringVar(value=self.opcoes_transformacoes_compostas[0])
        self.fila_transformacoes_compostas = []
        self.sequencia_composicao = []
        self.indice_composicao = 0
        self.composicao_ativa = False
        self.imagem_composicao_atual = None
        self.botao_proxima_transformacao = None
        self.lista_transformacoes_compostas = None
        self.label_status_composicao = None
        
        # Variáveis para os parâmetros de transformação
        self.rotacao_valor = tk.DoubleVar(value=0)
        self.transladx_valor = tk.DoubleVar(value=0)
        self.translady_valor = tk.DoubleVar(value=0)
        self.escalax_valor = tk.DoubleVar(value=1.0)
        self.escalay_valor = tk.DoubleVar(value=1.0)
        self.cisalhox_valor = tk.DoubleVar(value=0)
        self.cisalhoy_valor = tk.DoubleVar(value=0)
        self.reflexao_valor = tk.StringVar(value="Nenhuma")
        self.zoom_tipo_valor = tk.StringVar(value="Zoom in - Replicação")
        self.zoom_fator_valor = tk.DoubleVar(value=1.0)
        self.slider_zoom_fator = None
        
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

        # Aba 3: Decomposição
        frame_decomposicao = ttk.Frame(notebook)
        notebook.add(frame_decomposicao, text="Decomposição")
        self._criar_aba_decomposicao(frame_decomposicao)

        # Aba 4: Pseudocolorização
        frame_pseudocolorizacao = ttk.Frame(notebook)
        notebook.add(frame_pseudocolorizacao, text="Pseudocolorização")
        self._criar_aba_pseudocolorizacao(frame_pseudocolorizacao)

    def _criar_aba_decomposicao(self, parent):
        """Cria a aba para decomposição de imagens em diferentes espaços de cores"""
        tk.Label(
            parent, text="Decomposição de Imagem", font=("Arial", 14, "bold")
        ).pack(pady=15)

        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)

        self.label_img_decomposicao = tk.Label(
            frame_selecao,
            text="Nenhuma imagem selecionada",
            font=("Arial", 10),
            foreground="red",
        )
        self.label_img_decomposicao.pack(side="left", padx=10)

        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_decomposicao,
        ).pack(side="left", padx=10)

        frame_opcoes = tk.Frame(parent)
        frame_opcoes.pack(pady=20)

        tk.Label(
            frame_opcoes, text="Selecione o espaço de cores:", font=("Arial", 11)
        ).pack(side="left", padx=10)

        self.combo_espaco_cor = ttk.Combobox(
            frame_opcoes,
            values=["RGB", "CMY", "CMYK", "HSB", "HSL", "YUV"],
            state="readonly",
            width=10,
        )
        self.combo_espaco_cor.set("RGB")
        self.combo_espaco_cor.pack(side="left", padx=10)

        btn_decompor = tk.Button(
            parent,
            text="Decompor Imagem",
            command=self.aplicar_decomposicao,
            bg="#212F22",
            fg="white",
            font=("Arial", 11, "bold"),
        )
        btn_decompor.pack(pady=20)

        self.imagem_para_decomposicao = None

    def selecionar_imagem_decomposicao(self):
        """Seleciona uma imagem para a aba de decomposição"""
        from implementacaoPrimeiraUnidade import Image

        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not caminho:
            return

        try:
            self.imagem_para_decomposicao = Image(caminho)
            self.label_img_decomposicao.config(
                text=Path(caminho).name, foreground="green"
            )
            self.imagem_para_decomposicao.showImage()
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem.\n{erro}")

    def aplicar_decomposicao(self):
        """Aplica a decomposição na imagem selecionada"""
        from implementacaoPrimeiraUnidade import ColorSpaceDecomposer

        if self.imagem_para_decomposicao is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        espaco = self.combo_espaco_cor.get()
        decompositor = ColorSpaceDecomposer(self.imagem_para_decomposicao)
        decompositor.decompose(espaco)


    def _criar_aba_pseudocolorizacao(self, parent):
        tk.Label(parent, text="Pseudocolorização (Fatiamento)", font=("Arial", 14, "bold")).pack(pady=15)
        
        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)
        
        self.label_img_pseudo = tk.Label(frame_selecao, text="Nenhuma imagem selecionada", font=("Arial", 10), foreground="red")
        self.label_img_pseudo.pack(side="left", padx=10)
        
        tk.Button(frame_selecao, text="Selecionar Imagem", command=self.selecionar_imagem_pseudocolorizacao).pack(side="left", padx=10)
        
        frame_intervalo = tk.LabelFrame(parent, text="Intervalo de Intensidade (Fatiamento)", padx=10, pady=10)
        frame_intervalo.pack(pady=15, padx=20, fill="x")
        
        self.pseudo_min_val = tk.IntVar(value=0)
        self.pseudo_max_val = tk.IntVar(value=60)
        
        tk.Label(frame_intervalo, text="Mínimo (0-255):").pack(side="left", padx=5)
        tk.Entry(frame_intervalo, textvariable=self.pseudo_min_val, width=5).pack(side="left", padx=5)
        
        tk.Label(frame_intervalo, text="Máximo (0-255):").pack(side="left", padx=5)
        tk.Entry(frame_intervalo, textvariable=self.pseudo_max_val, width=5).pack(side="left", padx=5)
        
        frame_cor = tk.LabelFrame(parent, text="Cor de Destaque (RGB)", padx=10, pady=10)
        frame_cor.pack(pady=15, padx=20, fill="x")
        
        self.pseudo_r_val = tk.IntVar(value=160)
        self.pseudo_g_val = tk.IntVar(value=57)
        self.pseudo_b_val = tk.IntVar(value=0)
        
        tk.Label(frame_cor, text="R:").pack(side="left", padx=5)
        tk.Entry(frame_cor, textvariable=self.pseudo_r_val, width=5).pack(side="left", padx=5)
        tk.Label(frame_cor, text="G:").pack(side="left", padx=5)
        tk.Entry(frame_cor, textvariable=self.pseudo_g_val, width=5).pack(side="left", padx=5)
        tk.Label(frame_cor, text="B:").pack(side="left", padx=5)
        tk.Entry(frame_cor, textvariable=self.pseudo_b_val, width=5).pack(side="left", padx=5)
        
        btn_aplicar = tk.Button(parent, text="Aplicar Pseudocolorização", command=self.aplicar_pseudocolorizacao_fatiamento, bg="#212F22", fg="white", font=("Arial", 11, "bold"))
        btn_aplicar.pack(pady=20)
        
        self.imagem_para_pseudo = None

    def selecionar_imagem_pseudocolorizacao(self):
        from implementacaoPrimeiraUnidade import Image
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return
        try:
            self.imagem_para_pseudo = Image(caminho)
            self.label_img_pseudo.config(text=Path(caminho).name, foreground="green")
            self.imagem_para_pseudo.showImage()
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem.\n{erro}")

    def aplicar_pseudocolorizacao_fatiamento(self):
        from implementacaoPrimeiraUnidade import PseudoColorizer
        if self.imagem_para_pseudo is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return
            
        try:
            min_val = self.pseudo_min_val.get()
            max_val = self.pseudo_max_val.get()
            r_val = self.pseudo_r_val.get()
            g_val = self.pseudo_g_val.get()
            b_val = self.pseudo_b_val.get()
            
            # opencv expects BGR
            color_bgr = (b_val, g_val, r_val)
            
            colorizer = PseudoColorizer(self.imagem_para_pseudo)
            result_img = colorizer.apply_slicing(min_val, max_val, color_bgr)
            
            cv2.imshow("Pseudocolorização - Fatiamento", result_img)
        except Exception as e:
            messagebox.showerror("Erro", f"Valores inválidos.\n{e}")

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

        frame_modo = tk.LabelFrame(parent, text="Modo de transformação", padx=10, pady=8)
        frame_modo.pack(fill="x", padx=10, pady=(0, 10))

        tk.Radiobutton(
            frame_modo,
            text="Individual",
            value="individual",
            variable=self.modo_transformacao,
            command=self._atualizar_estado_modo_transformacao,
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            frame_modo,
            text="Transformação composta",
            value="composta",
            variable=self.modo_transformacao,
            command=self._atualizar_estado_modo_transformacao,
        ).pack(side="left", padx=5)

        frame_composta = tk.LabelFrame(parent, text="Transformações da composição", padx=10, pady=8)
        frame_composta.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(
            frame_composta,
            text="Adicione transformações na ordem desejada. Você pode repetir transformações.",
            font=("Arial", 9),
        ).pack(anchor="w", pady=(0, 6))

        frame_add_composta = tk.Frame(frame_composta)
        frame_add_composta.pack(fill="x", pady=(0, 6))

        combo_transformacoes = ttk.Combobox(
            frame_add_composta,
            values=self.opcoes_transformacoes_compostas,
            state="readonly",
            width=20,
            textvariable=self.transformacao_para_adicionar,
        )
        combo_transformacoes.pack(side="left", padx=(0, 6))

        tk.Button(
            frame_add_composta,
            text="Adicionar",
            command=self.adicionar_transformacao_composta,
            bg="#212F22",
            fg="white",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            frame_add_composta,
            text="Remover selecionada",
            command=self.remover_transformacao_composta,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            frame_add_composta,
            text="Limpar fila",
            command=self.limpar_transformacoes_compostas,
        ).pack(side="left")

        self.lista_transformacoes_compostas = tk.Listbox(frame_composta, height=6)
        self.lista_transformacoes_compostas.pack(fill="x")

        self.label_status_composicao = tk.Label(
            frame_composta,
            text="Fila vazia.",
            font=("Arial", 9),
            anchor="w",
            justify="left",
        )
        self.label_status_composicao.pack(fill="x", pady=(6, 0))
        
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

        frame_zoom = tk.LabelFrame(scrollable_frame, text="Zoom", padx=10, pady=8)
        frame_zoom.pack(fill="x", padx=10, pady=5)

        linha_zoom_tipo = tk.Frame(frame_zoom)
        linha_zoom_tipo.pack(fill="x", pady=(0, 6))
        tk.Label(linha_zoom_tipo, text="Tipo", width=15, font=("Arial", 9)).pack(side="left")
        combo_zoom = ttk.Combobox(
            linha_zoom_tipo,
            values=[
                "Zoom in - Replicação",
                "Zoom in - Interpolação",
                "Zoom out - Exclusão",
                "Zoom out - Valor médio",
            ],
            state="readonly",
            width=20,
            textvariable=self.zoom_tipo_valor,
        )
        combo_zoom.pack(side="left", padx=5)
        combo_zoom.bind("<<ComboboxSelected>>", self._ao_mudar_tipo_zoom)

        self.slider_zoom_fator = self._adicionar_slider(frame_zoom, "Fator Zoom", self.zoom_fator_valor, 1.0, 4.0, 0.1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de controle
        frame_botoes = tk.Frame(parent)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Resetar", command=self.resetar_transformacoes, bg="#FF6B6B", fg="white").pack(side="left", padx=5)
        self.botao_proxima_transformacao = tk.Button(
            frame_botoes,
            text="Próxima",
            command=self.proxima_transformacao_composta,
            state=tk.DISABLED,
            bg="#212F22",
            fg="white",
        )
        self.botao_proxima_transformacao.pack(side="left", padx=5)

        self._atualizar_estado_modo_transformacao()
        self._atualizar_limites_zoom()

    def _atualizar_estado_modo_transformacao(self):
        if self.botao_proxima_transformacao is None:
            return

        if self.modo_transformacao.get() == "composta":
            self.botao_proxima_transformacao.config(state=tk.NORMAL)
        else:
            self.botao_proxima_transformacao.config(state=tk.DISABLED)

        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_status_composicao()

        if self.modo_transformacao.get() == "composta" and self.imagem_transformacao is not None:
            imagem_base = self._criar_canvas_base_transformacao()
            self._mostrar_imagem_transformacao(imagem_base)

        if self.modo_transformacao.get() == "individual" and self.imagem_transformacao is not None:
            self.atualizar_transformacao()
    
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
        return slider

    def _limites_zoom_por_tipo(self, tipo_zoom):
        if tipo_zoom in {"Zoom in - Replicação", "Zoom in - Interpolação"}:
            return 1.0, 4.0
        return 0.2, 1.0

    def _normalizar_fator_zoom(self, tipo_zoom, fator_zoom):
        minimo, maximo = self._limites_zoom_por_tipo(tipo_zoom)
        return max(minimo, min(maximo, fator_zoom))

    def _atualizar_limites_zoom(self):
        tipo_zoom = self.zoom_tipo_valor.get()
        minimo, maximo = self._limites_zoom_por_tipo(tipo_zoom)

        if self.slider_zoom_fator is not None:
            self.slider_zoom_fator.configure(from_=minimo, to=maximo)

        fator_atual = self._normalizar_fator_zoom(tipo_zoom, self.zoom_fator_valor.get())
        if fator_atual != self.zoom_fator_valor.get():
            self.zoom_fator_valor.set(fator_atual)

    def _ao_mudar_tipo_zoom(self, _event=None):
        self._atualizar_limites_zoom()
        self.atualizar_transformacao()
    
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

    def _aplicar_rotacao(self, imagem, angulo):
        if angulo == 0:
            return imagem

        altura, largura = imagem.shape[:2]
        centro = (largura / 2.0, altura / 2.0)
        matriz = cv2.getRotationMatrix2D(centro, angulo, 1.0)
        return cv2.warpAffine(
            imagem,
            matriz,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=self._valor_borda(imagem),
        )

    def _aplicar_translacao(self, imagem, deslocamento_x, deslocamento_y):
        if deslocamento_x == 0 and deslocamento_y == 0:
            return imagem

        altura, largura = imagem.shape[:2]
        matriz = np.float32([
            [1, 0, int(deslocamento_x)],
            [0, 1, int(deslocamento_y)],
        ])
        return cv2.warpAffine(
            imagem,
            matriz,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=self._valor_borda(imagem),
        )

    def _aplicar_escala(self, imagem, fator_x, fator_y):
        if fator_x <= 0 or fator_y <= 0:
            return imagem

        if fator_x == 1 and fator_y == 1:
            return imagem

        altura, largura = imagem.shape[:2]
        centro_x = largura / 2.0
        centro_y = altura / 2.0
        matriz = np.float32([
            [fator_x, 0, centro_x * (1 - fator_x)],
            [0, fator_y, centro_y * (1 - fator_y)],
        ])
        return cv2.warpAffine(
            imagem,
            matriz,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=self._valor_borda(imagem),
        )

    def _aplicar_cisalhamento(self, imagem, fator_x, fator_y):
        if fator_x == 0 and fator_y == 0:
            return imagem

        altura, largura = imagem.shape[:2]
        centro_x = largura / 2.0
        centro_y = altura / 2.0
        matriz = np.float32([
            [1, fator_x, -fator_x * centro_y],
            [fator_y, 1, -fator_y * centro_x],
        ])
        return cv2.warpAffine(
            imagem,
            matriz,
            (largura, altura),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=self._valor_borda(imagem),
        )

    def _aplicar_reflexao(self, imagem, reflexao):
        if reflexao == "Nenhuma":
            return imagem
        if reflexao == "Eixo X":
            return cv2.flip(imagem, 0)
        if reflexao == "Eixo Y":
            return cv2.flip(imagem, 1)
        if reflexao == "Ambos":
            return cv2.flip(imagem, -1)
        return imagem

    def _aplicar_zoom(self, imagem, tipo_zoom, fator_zoom):
        if self.transformador is None:
            return imagem

        fator_zoom = self._normalizar_fator_zoom(tipo_zoom, fator_zoom)
        self.transformador.imagem_preview = imagem.copy()
        if tipo_zoom == "Zoom in - Replicação":
            return self.transformador.zoom_in_replicacao(fator_zoom)
        if tipo_zoom == "Zoom in - Interpolação":
            return self.transformador.zoom_in_interpolacao(fator_zoom)
        if tipo_zoom == "Zoom out - Exclusão":
            return self.transformador.zoom_out_exclusao(fator_zoom)
        if tipo_zoom == "Zoom out - Valor médio":
            return self.transformador.zoom_out_valor_medio(fator_zoom)
        return imagem

    def _capturar_parametros_transformacao(self, nome_transformacao):
        if nome_transformacao == "Rotação":
            return {"angulo": self.rotacao_valor.get()}
        if nome_transformacao == "Translação":
            return {
                "deslocamento_x": self.transladx_valor.get(),
                "deslocamento_y": self.translady_valor.get(),
            }
        if nome_transformacao == "Escala":
            return {
                "fator_x": self.escalax_valor.get(),
                "fator_y": self.escalay_valor.get(),
            }
        if nome_transformacao == "Cisalhamento":
            return {
                "fator_x": self.cisalhox_valor.get(),
                "fator_y": self.cisalhoy_valor.get(),
            }
        if nome_transformacao == "Reflexão":
            return {"reflexao": self.reflexao_valor.get()}
        if nome_transformacao in {
            "Zoom in - Replicação",
            "Zoom in - Interpolação",
            "Zoom out - Exclusão",
            "Zoom out - Valor médio",
        }:
            fator = self._normalizar_fator_zoom(nome_transformacao, self.zoom_fator_valor.get())
            return {
                "tipo_zoom": nome_transformacao,
                "fator_zoom": fator,
            }
        return {}

    def _formatar_transformacao_composta(self, nome_transformacao, parametros):
        if nome_transformacao == "Rotação":
            return f"Rotação (ângulo={parametros['angulo']:.2f})"
        if nome_transformacao == "Translação":
            return f"Translação (x={parametros['deslocamento_x']:.2f}, y={parametros['deslocamento_y']:.2f})"
        if nome_transformacao == "Escala":
            return f"Escala (x={parametros['fator_x']:.2f}, y={parametros['fator_y']:.2f})"
        if nome_transformacao == "Cisalhamento":
            return f"Cisalhamento (x={parametros['fator_x']:.2f}, y={parametros['fator_y']:.2f})"
        if nome_transformacao == "Reflexão":
            return f"Reflexão ({parametros['reflexao']})"
        if nome_transformacao in {
            "Zoom in - Replicação",
            "Zoom in - Interpolação",
            "Zoom out - Exclusão",
            "Zoom out - Valor médio",
        }:
            return f"{nome_transformacao} (fator={parametros['fator_zoom']:.2f})"
        return nome_transformacao

    def _atualizar_status_composicao(self):
        if self.label_status_composicao is None:
            return

        total = len(self.fila_transformacoes_compostas)
        if total == 0:
            self.label_status_composicao.config(text="Fila vazia.")
            return

        if self.composicao_ativa:
            self.label_status_composicao.config(text=f"Executando passo {self.indice_composicao + 1} de {len(self.sequencia_composicao)}.")
            return

        self.label_status_composicao.config(text=f"{total} transformação(ões) na fila.")

    def adicionar_transformacao_composta(self):
        nome_transformacao = self.transformacao_para_adicionar.get()
        if nome_transformacao not in self.opcoes_transformacoes_compostas:
            messagebox.showwarning("Aviso", "Selecione uma transformação válida para adicionar.")
            return

        parametros = self._capturar_parametros_transformacao(nome_transformacao)
        item = {
            "nome": nome_transformacao,
            "parametros": parametros,
        }
        self.fila_transformacoes_compostas.append(item)

        descricao = self._formatar_transformacao_composta(nome_transformacao, parametros)
        self.lista_transformacoes_compostas.insert(tk.END, f"{len(self.fila_transformacoes_compostas)}. {descricao}")

        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_status_composicao()

    def remover_transformacao_composta(self):
        if self.lista_transformacoes_compostas is None:
            return

        selecao = self.lista_transformacoes_compostas.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma transformação da fila para remover.")
            return

        indice = selecao[0]
        self.lista_transformacoes_compostas.delete(indice)
        self.fila_transformacoes_compostas.pop(indice)
        self._recarregar_lista_transformacoes_compostas()

    def limpar_transformacoes_compostas(self):
        if self.lista_transformacoes_compostas is not None:
            self.lista_transformacoes_compostas.delete(0, tk.END)

        self.fila_transformacoes_compostas = []
        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_status_composicao()

    def _recarregar_lista_transformacoes_compostas(self):
        if self.lista_transformacoes_compostas is None:
            return

        self.lista_transformacoes_compostas.delete(0, tk.END)
        for indice, item in enumerate(self.fila_transformacoes_compostas, start=1):
            descricao = self._formatar_transformacao_composta(item["nome"], item["parametros"])
            self.lista_transformacoes_compostas.insert(tk.END, f"{indice}. {descricao}")

        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_status_composicao()

    def _aplicar_transformacao_por_nome(self, imagem, nome_transformacao, parametros=None):
        parametros = {} if parametros is None else parametros

        if nome_transformacao == "Rotação":
            return self._aplicar_rotacao(imagem, parametros.get("angulo", self.rotacao_valor.get()))
        if nome_transformacao == "Translação":
            return self._aplicar_translacao(
                imagem,
                parametros.get("deslocamento_x", self.transladx_valor.get()),
                parametros.get("deslocamento_y", self.translady_valor.get()),
            )
        if nome_transformacao == "Escala":
            return self._aplicar_escala(
                imagem,
                parametros.get("fator_x", self.escalax_valor.get()),
                parametros.get("fator_y", self.escalay_valor.get()),
            )
        if nome_transformacao == "Cisalhamento":
            return self._aplicar_cisalhamento(
                imagem,
                parametros.get("fator_x", self.cisalhox_valor.get()),
                parametros.get("fator_y", self.cisalhoy_valor.get()),
            )
        if nome_transformacao == "Reflexão":
            return self._aplicar_reflexao(imagem, parametros.get("reflexao", self.reflexao_valor.get()))
        if nome_transformacao in {
            "Zoom in - Replicação",
            "Zoom in - Interpolação",
            "Zoom out - Exclusão",
            "Zoom out - Valor médio",
        }:
            tipo_zoom = parametros.get("tipo_zoom", nome_transformacao)
            fator_zoom = parametros.get("fator_zoom", self.zoom_fator_valor.get())
            return self._aplicar_zoom(
                imagem,
                tipo_zoom,
                fator_zoom,
            )
        return imagem

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

    def _mostrar_imagem_transformacao(self, imagem):
        imagem_canvas = self._renderizar_em_canvas(imagem)
        cv2.imshow(self.nome_janela_transformacao, imagem_canvas)
        cv2.waitKey(1)

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

        if self.modo_transformacao.get() == "composta":
            return

        imagem_temp = self._criar_canvas_base_transformacao()
        imagem_temp = self._aplicar_rotacao(imagem_temp, self.rotacao_valor.get())
        imagem_temp = self._aplicar_translacao(imagem_temp, self.transladx_valor.get(), self.translady_valor.get())
        imagem_temp = self._aplicar_escala(imagem_temp, self.escalax_valor.get(), self.escalay_valor.get())
        imagem_temp = self._aplicar_cisalhamento(imagem_temp, self.cisalhox_valor.get(), self.cisalhoy_valor.get())
        imagem_temp = self._aplicar_reflexao(imagem_temp, self.reflexao_valor.get())

        imagem_temp = self._aplicar_zoom(
            imagem_temp,
            self.zoom_tipo_valor.get(),
            self.zoom_fator_valor.get(),
        )

        self._mostrar_imagem_transformacao(imagem_temp)
    
    def aplicar_transformacoes(self):
        """Aplica todas as transformações e salva o resultado"""
        if self.transformador is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem para transformar.")
            return
        
        self.atualizar_transformacao()

    def proxima_transformacao_composta(self):
        if self.imagem_transformacao is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem para transformar.")
            return

        if self.modo_transformacao.get() != "composta":
            messagebox.showinfo("Informação", "Selecione o modo 'Transformação composta' para usar o botão Próxima.")
            return

        if not self.composicao_ativa:
            self.sequencia_composicao = list(self.fila_transformacoes_compostas)
            self.indice_composicao = 0
            self.imagem_composicao_atual = self._criar_canvas_base_transformacao()

            if not self.sequencia_composicao:
                messagebox.showwarning("Aviso", "Adicione ao menos uma transformação na fila da composição.")
                return

            self.composicao_ativa = True
            self._atualizar_status_composicao()

        if self.indice_composicao >= len(self.sequencia_composicao):
            messagebox.showinfo("Informação", "A transformação composta já foi concluída. Clique em Próxima novamente para reiniciar com os valores atuais.")
            self.composicao_ativa = False
            self.indice_composicao = 0
            self.imagem_composicao_atual = None
            self._atualizar_status_composicao()
            return

        item_transformacao = self.sequencia_composicao[self.indice_composicao]
        nome_transformacao = item_transformacao["nome"]
        parametros = item_transformacao["parametros"]
        self.imagem_composicao_atual = self._aplicar_transformacao_por_nome(
            self.imagem_composicao_atual,
            nome_transformacao,
            parametros,
        )
        self.indice_composicao += 1
        self._atualizar_status_composicao()

        self._mostrar_imagem_transformacao(self.imagem_composicao_atual)

        if self.indice_composicao >= len(self.sequencia_composicao):
            messagebox.showinfo("Informação", "Transformação composta concluída.")
            self.composicao_ativa = False
            self._atualizar_status_composicao()
    
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
        self.zoom_tipo_valor.set("Zoom in - Replicação")
        self.zoom_fator_valor.set(1.0)
        self._atualizar_limites_zoom()
        self.modo_transformacao.set("individual")

        if self.lista_transformacoes_compostas is not None:
            self.lista_transformacoes_compostas.delete(0, tk.END)
        self.fila_transformacoes_compostas = []

        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_estado_modo_transformacao()
        
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

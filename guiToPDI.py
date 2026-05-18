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
        self.root.eval("tk::PlaceWindow . center")

        self.dicionario_operacoes = {
            "Soma": operator.add,
            "Subtração": operator.sub,
            "Multiplicação": operator.mul,
            "Divisão": operator.truediv,
            "AND": operator.and_,
            "OR": operator.or_,
            "XOR": operator.xor,
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
        self.transformacao_para_adicionar = tk.StringVar(
            value=self.opcoes_transformacoes_compostas[0]
        )
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

        # Variáveis para Realce
        self.imagem_para_realce = None
        self.realce_tipo = tk.StringVar(value="linear_a_mapeamento")
        self.realce_g_min = tk.IntVar(value=0)
        self.realce_g_max = tk.IntVar(value=255)
        self.realce_limiar = tk.IntVar(value=128)
        self.realce_gamma = tk.DoubleVar(value=1.5)
        self.realce_bit_plane = tk.IntVar(value=0)
        self.linear_b_intervals = []
        # Variáveis para Segmentação
        self.imagem_para_segmentacao = None
        self.segmentacao_T = tk.IntVar(value=50)
        self.segmentacao_mode = tk.StringVar(value="pontos")
        self.segmentacao_direcao = tk.StringVar(value="horizontal")
        self.segmentacao_metodo_borda = tk.StringVar(value="roberts")
        self.segmentacao_tipo_lim = tk.StringVar(value="global")
        self.segmentacao_metodo_lim = tk.StringVar(value="media")
        self.segmentacao_n_lim = tk.IntVar(value=5)
        self.segmentacao_k_lim = tk.DoubleVar(value=-0.2)
        self.segmentacao_tolerancia_regiao = tk.IntVar(value=15)
        self.segmentacao_sementes = []

        # Variáveis para Filtros
        self.imagem_para_filtros = None
        self.filtro_categoria = tk.StringVar(value="passa_baixa")
        self.filtro_tipo = tk.StringVar(value="Média")
        self.filtro_tamanho = tk.IntVar(value=3)
        self.filtro_modo_cor = tk.StringVar(value="yuv")
        self.filtro_high_boost_a = tk.DoubleVar(value=1.5)
        self.combo_filtro_tipo = None
        self.frame_parametros_filtro = None

        # Variáveis para Meio-tom
        self.imagem_para_meio_tom = None
        self.meio_tom_categoria = tk.StringVar(value="ordenado")
        self.meio_tom_tipo = tk.StringVar(value="2x2")
        self.combo_meio_tom_tipo = None

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

        # Aba 5: Realce
        frame_realce = ttk.Frame(notebook)
        notebook.add(frame_realce, text="Realce")
        self._criar_aba_realce(frame_realce)

        # Aba 6: Segmentação
        frame_segmentacao = ttk.Frame(notebook)
        notebook.add(frame_segmentacao, text="Segmentação")
        self._criar_aba_segmentacao(frame_segmentacao)

        # Aba 7: Filtros
        frame_filtros = ttk.Frame(notebook)
        notebook.add(frame_filtros, text="Filtros")
        self._criar_aba_filtros(frame_filtros)

        # Aba 8: Meio-tom
        frame_meio_tom = ttk.Frame(notebook)
        notebook.add(frame_meio_tom, text="Meio-tom")
        self._criar_aba_meio_tom(frame_meio_tom)

    def mostrar_original_e_resultado(self, titulo_original, img_original, titulo_resultado, img_result):
        """Mostra lado a lado (ou em janelas separadas) a imagem original e a imagem editada."""
        try:
            cv2.imshow(titulo_original, img_original)
        except cv2.error:
            pass

        try:
            cv2.imshow(titulo_resultado, img_result)
        except cv2.error:
            pass

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
        tk.Label(parent, text="Pseudocolorização", font=("Arial", 14, "bold")).pack(
            pady=15
        )

        # Modo de operação
        frame_modo = tk.Frame(parent)
        frame_modo.pack(pady=5)
        self.modo_pseudo = tk.StringVar(value="fatiamento_densidade")
        tk.Radiobutton(
            frame_modo,
            text="Fatiamento por Densidade",
            variable=self.modo_pseudo,
            value="fatiamento_densidade",
            command=self._atualizar_aba_pseudo,
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            frame_modo,
            text="Redistribuição de Cores (Mapa de Cores)",
            variable=self.modo_pseudo,
            value="redistribuicao",
            command=self._atualizar_aba_pseudo,
        ).pack(side="left", padx=10)

        # Seleção de Imagem
        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)
        self.label_img_pseudo = tk.Label(
            frame_selecao,
            text="Nenhuma imagem selecionada",
            font=("Arial", 10),
            foreground="red",
        )
        self.label_img_pseudo.pack(side="left", padx=10)
        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_pseudocolorizacao,
        ).pack(side="left", padx=10)

        # Frame Fatiamento
        self.frame_fatiamento = tk.Frame(parent)

        self.frame_intervalos = tk.Frame(self.frame_fatiamento)
        self.frame_intervalos.pack(pady=5, padx=20, fill="x")

        self.fatiamento_intervals = []
        self._adicionar_intervalo_fatiamento(
            default_min=0, default_max=60, default_r=160, default_g=57, default_b=0
        )
        self._adicionar_intervalo_fatiamento(
            default_min=61, default_max=120, default_r=57, default_g=160, default_b=0
        )
        self._adicionar_intervalo_fatiamento(
            default_min=121, default_max=180, default_r=0, default_g=57, default_b=160
        )

        tk.Button(
            self.frame_fatiamento,
            text="+ Adicionar Intervalo",
            command=self._adicionar_intervalo_fatiamento,
        ).pack(pady=5)

        # Frame Redistribuição (Mapa de Cores)
        self.frame_redistribuicao = tk.Frame(parent)
        frame_mapa = tk.LabelFrame(
            self.frame_redistribuicao,
            text="Redistribuição (Mapa de Cores)",
            padx=10,
            pady=10,
        )
        frame_mapa.pack(pady=15, padx=20, fill="x")

        self.dicionario_colormaps = {
            "JET": cv2.COLORMAP_JET,
            "HOT": cv2.COLORMAP_HOT,
            "RAINBOW": cv2.COLORMAP_RAINBOW,
            "HSV": cv2.COLORMAP_HSV,
            "OCEAN": cv2.COLORMAP_OCEAN,
            "BONE": cv2.COLORMAP_BONE,
            "SPRING": cv2.COLORMAP_SPRING,
            "WINTER": cv2.COLORMAP_WINTER,
            "AUTUMN": cv2.COLORMAP_AUTUMN,
            "SUMMER": cv2.COLORMAP_SUMMER,
            "VIRIDIS": cv2.COLORMAP_VIRIDIS,
        }

        tk.Label(frame_mapa, text="Selecione o Mapa:").pack(side="left", padx=5)
        self.combo_colormap = ttk.Combobox(
            frame_mapa,
            values=list(self.dicionario_colormaps.keys()),
            state="readonly",
            width=15,
        )
        self.combo_colormap.set("JET")
        self.combo_colormap.pack(side="left", padx=5)

        self._atualizar_aba_pseudo()

        btn_aplicar = tk.Button(
            parent,
            text="Aplicar Pseudocolorização",
            command=self.aplicar_pseudocolorizacao,
            bg="#212F22",
            fg="white",
            font=("Arial", 11, "bold"),
        )
        btn_aplicar.pack(pady=20, fill="x", padx=10)

        self.imagem_para_pseudo = None

    def _atualizar_aba_pseudo(self):
        modo = self.modo_pseudo.get()
        if modo == "fatiamento_densidade":
            self.frame_redistribuicao.pack_forget()
            self.frame_fatiamento.pack(fill="x", expand=True)
        elif modo == "redistribuicao":
            self.frame_fatiamento.pack_forget()
            self.frame_redistribuicao.pack(fill="x", expand=True)

    def _adicionar_intervalo_fatiamento(
        self, default_min=0, default_max=255, default_r=255, default_g=0, default_b=0
    ):
        row_frame = tk.LabelFrame(
            self.frame_intervalos, text="Intervalo e Cor de Destaque", padx=5, pady=5
        )
        row_frame.pack(pady=5, fill="x")

        min_val = tk.IntVar(value=default_min)
        max_val = tk.IntVar(value=default_max)
        r_val = tk.IntVar(value=default_r)
        g_val = tk.IntVar(value=default_g)
        b_val = tk.IntVar(value=default_b)

        tk.Label(row_frame, text="Mín:").pack(side="left")
        tk.Entry(row_frame, textvariable=min_val, width=4).pack(side="left", padx=2)
        tk.Label(row_frame, text="Máx:").pack(side="left")
        tk.Entry(row_frame, textvariable=max_val, width=4).pack(side="left", padx=2)

        tk.Label(row_frame, text="  R:").pack(side="left")
        tk.Entry(row_frame, textvariable=r_val, width=4).pack(side="left", padx=2)
        tk.Label(row_frame, text="G:").pack(side="left")
        tk.Entry(row_frame, textvariable=g_val, width=4).pack(side="left", padx=2)
        tk.Label(row_frame, text="B:").pack(side="left")
        tk.Entry(row_frame, textvariable=b_val, width=4).pack(side="left", padx=2)

        interval_data = {
            "frame": row_frame,
            "min": min_val,
            "max": max_val,
            "r": r_val,
            "g": g_val,
            "b": b_val,
        }
        self.fatiamento_intervals.append(interval_data)

        tk.Button(
            row_frame,
            text="Remover",
            command=lambda: self._remover_intervalo_fatiamento(interval_data),
        ).pack(side="right", padx=5)

    def _remover_intervalo_fatiamento(self, interval_data):
        if len(self.fatiamento_intervals) > 1:
            interval_data["frame"].destroy()
            self.fatiamento_intervals.remove(interval_data)
        else:
            messagebox.showwarning("Aviso", "Você deve manter pelo menos um intervalo.")

    def _adicionar_intervalo_realce(self, defaults=(0, 255, 0, 255)):
        """Adiciona um intervalo para o mapeamento linear por partes.
        defaults: (f_min, f_max, g_min, g_max)
        """
        f_min_def, f_max_def, g_min_def, g_max_def = defaults

        row_frame = tk.LabelFrame(
            self.frame_intervalos_realce, text="Intervalo (f_min, f_max) -> (g_min, g_max)", padx=5, pady=5
        )
        row_frame.pack(pady=5, fill="x")

        fmin = tk.IntVar(value=f_min_def)
        fmax = tk.IntVar(value=f_max_def)
        gmin = tk.IntVar(value=g_min_def)
        gmax = tk.IntVar(value=g_max_def)

        tk.Label(row_frame, text="f_min:").pack(side="left")
        tk.Entry(row_frame, textvariable=fmin, width=4).pack(side="left", padx=2)
        tk.Label(row_frame, text="f_max:").pack(side="left")
        tk.Entry(row_frame, textvariable=fmax, width=4).pack(side="left", padx=2)

        tk.Label(row_frame, text="  g_min:").pack(side="left")
        tk.Entry(row_frame, textvariable=gmin, width=4).pack(side="left", padx=2)
        tk.Label(row_frame, text="g_max:").pack(side="left")
        tk.Entry(row_frame, textvariable=gmax, width=4).pack(side="left", padx=2)

        interval_data = {
            "frame": row_frame,
            "f_min": fmin,
            "f_max": fmax,
            "g_min": gmin,
            "g_max": gmax,
        }

        self.linear_b_intervals.append(interval_data)

        tk.Button(
            row_frame,
            text="Remover",
            command=lambda: self._remover_intervalo_realce(interval_data),
        ).pack(side="right", padx=5)

    def _remover_intervalo_realce(self, interval_data):
        if len(self.linear_b_intervals) > 1:
            interval_data["frame"].destroy()
            self.linear_b_intervals.remove(interval_data)
        else:
            messagebox.showwarning("Aviso", "Você deve manter ao menos um intervalo.")

    def selecionar_imagem_pseudocolorizacao(self):
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
            self.imagem_para_pseudo = Image(caminho)
            self.label_img_pseudo.config(text=Path(caminho).name, foreground="green")
            self.imagem_para_pseudo.showImage()
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem.\n{erro}")

    def aplicar_pseudocolorizacao(self):
        from implementacaoPrimeiraUnidade import PseudoColorizer

        if self.imagem_para_pseudo is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            colorizer = PseudoColorizer(self.imagem_para_pseudo)
            modo = self.modo_pseudo.get()

            if modo == "fatiamento_densidade":
                intervalos = []
                for data in self.fatiamento_intervals:
                    min_v = data["min"].get()
                    max_v = data["max"].get()
                    r_v = data["r"].get()
                    g_v = data["g"].get()
                    b_v = data["b"].get()
                    intervalos.append((min_v, max_v, (b_v, g_v, r_v)))

                result_img = colorizer.apply_slicing(intervalos)
                cv2.imshow("Pseudocolorização - Fatiamento por Densidade", result_img)

            elif modo == "redistribuicao":
                nome_colormap = self.combo_colormap.get()
                id_colormap = self.dicionario_colormaps.get(
                    nome_colormap, cv2.COLORMAP_JET
                )

                result_img = colorizer.apply_redistribution(id_colormap)
                cv2.imshow(f"Pseudocolorização - Redistribuição ({nome_colormap})", result_img)

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao aplicar.\n{e}")

    def _criar_aba_operacoes(self, parent):
        """Cria a aba de operações entre duas imagens"""
        tk.Label(parent, text="Escolha a operação:", font=("Arial", 11)).pack(pady=15)

        self.label_img1 = tk.Label(
            parent, text="Imagem 1: nao selecionada", font=("Arial", 9)
        )
        self.label_img1.pack()

        self.label_img2 = tk.Label(
            parent, text="Imagem 2: nao selecionada", font=("Arial", 9)
        )
        self.label_img2.pack(pady=(0, 8))

        frame_botoes = tk.Frame(parent)
        frame_botoes.pack(pady=(0, 8))

        tk.Button(
            frame_botoes,
            text="Selecionar Imagem 1",
            command=lambda: self.selecionar_imagem(1),
        ).pack(side="left", padx=6)
        tk.Button(
            frame_botoes,
            text="Selecionar Imagem 2",
            command=lambda: self.selecionar_imagem(2),
        ).pack(side="left", padx=6)

        self.combo_operacoes = ttk.Combobox(
            parent,
            values=list(self.dicionario_operacoes.keys()),
            state="readonly",
            width=20,
        )
        self.combo_operacoes.set("Selecione...")
        self.combo_operacoes.pack(pady=5)

        btn_executar = tk.Button(
            parent,
            text="Gerar Resultado",
            command=self.aplicar_operacao,
            bg="#212F22",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        btn_executar.pack(pady=15)

    def _criar_aba_transformacoes(self, parent):
        """Cria a aba de transformações com sliders"""
        # Seleção de imagem para transformação
        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)

        tk.Label(
            frame_selecao, text="Imagem para transformar:", font=("Arial", 10)
        ).pack(side="left", padx=5)
        self.label_img_transform = tk.Label(
            frame_selecao, text="nao selecionada", font=("Arial", 9), foreground="red"
        )
        self.label_img_transform.pack(side="left", padx=5)

        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_transformacao,
        ).pack(side="left", padx=5)

        frame_modo = tk.LabelFrame(
            parent, text="Modo de transformação", padx=10, pady=8
        )
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

        frame_composta = tk.LabelFrame(
            parent, text="Transformações da composição", padx=10, pady=8
        )
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
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Adicionar sliders
        self._adicionar_slider(
            scrollable_frame, "Rotação", self.rotacao_valor, 0, 360, 1
        )
        self._adicionar_slider(
            scrollable_frame, "Translação X", self.transladx_valor, -100, 100, 1
        )
        self._adicionar_slider(
            scrollable_frame, "Translação Y", self.translady_valor, -100, 100, 1
        )
        self._adicionar_slider(
            scrollable_frame, "Escala X", self.escalax_valor, 0.5, 2.0, 0.1
        )
        self._adicionar_slider(
            scrollable_frame, "Escala Y", self.escalay_valor, 0.5, 2.0, 0.1
        )
        self._adicionar_slider(
            scrollable_frame, "Cisalhamento X", self.cisalhox_valor, -0.5, 0.5, 0.05
        )
        self._adicionar_slider(
            scrollable_frame, "Cisalhamento Y", self.cisalhoy_valor, -0.5, 0.5, 0.05
        )

        frame_reflexao = tk.Frame(scrollable_frame)
        frame_reflexao.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_reflexao, text="Reflexão", width=15, font=("Arial", 9)).pack(
            side="left"
        )
        combo_reflexao = ttk.Combobox(
            frame_reflexao,
            values=["Nenhuma", "Eixo X", "Eixo Y", "Ambos"],
            state="readonly",
            width=20,
            textvariable=self.reflexao_valor,
        )
        combo_reflexao.pack(side="left", padx=5)
        combo_reflexao.bind(
            "<<ComboboxSelected>>", lambda _event: self.atualizar_transformacao()
        )

        frame_zoom = tk.LabelFrame(scrollable_frame, text="Zoom", padx=10, pady=8)
        frame_zoom.pack(fill="x", padx=10, pady=5)

        linha_zoom_tipo = tk.Frame(frame_zoom)
        linha_zoom_tipo.pack(fill="x", pady=(0, 6))
        tk.Label(linha_zoom_tipo, text="Tipo", width=15, font=("Arial", 9)).pack(
            side="left"
        )
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

        self.slider_zoom_fator = self._adicionar_slider(
            frame_zoom, "Fator Zoom", self.zoom_fator_valor, 1.0, 4.0, 0.1
        )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botões de controle
        frame_botoes = tk.Frame(parent)
        frame_botoes.pack(pady=10)

        tk.Button(
            frame_botoes,
            text="Resetar",
            command=self.resetar_transformacoes,
            bg="#FF6B6B",
            fg="white",
        ).pack(side="left", padx=5)
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

        if (
            self.modo_transformacao.get() == "composta"
            and self.imagem_transformacao is not None
        ):
            imagem_base = self._criar_canvas_base_transformacao()
            self._mostrar_imagem_transformacao(imagem_base)

        if (
            self.modo_transformacao.get() == "individual"
            and self.imagem_transformacao is not None
        ):
            self.atualizar_transformacao()

    def _adicionar_slider(self, parent, label_text, var, from_val, to_val, resolution):
        """Adiciona um slider com rótulo e valor"""
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text=label_text, width=15, font=("Arial", 9)).pack(side="left")

        slider = ttk.Scale(
            frame,
            from_=from_val,
            to=to_val,
            orient="horizontal",
            variable=var,
            command=lambda _: self.atualizar_transformacao(),
        )
        slider.pack(side="left", fill="x", expand=True, padx=5)

        valor_label = tk.Label(
            frame, text=f"{var.get():.2f}", width=8, font=("Arial", 9)
        )
        valor_label.pack(side="left", padx=5)

        # Atualizar o rótulo do valor quando o slider muda
        def atualizar_label(*args):
            valor_label.config(text=f"{var.get():.2f}")

        var.trace_add("write", atualizar_label)
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

        fator_atual = self._normalizar_fator_zoom(
            tipo_zoom, self.zoom_fator_valor.get()
        )
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
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"),
                ("Todos os arquivos", "*.*"),
            ],
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
            try:
                self.imagem_transformacao.showImage()
            except Exception:
                pass
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
        matriz = np.float32(
            [
                [1, 0, int(deslocamento_x)],
                [0, 1, int(deslocamento_y)],
            ]
        )
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
        matriz = np.float32(
            [
                [fator_x, 0, centro_x * (1 - fator_x)],
                [0, fator_y, centro_y * (1 - fator_y)],
            ]
        )
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
        matriz = np.float32(
            [
                [1, fator_x, -fator_x * centro_y],
                [fator_y, 1, -fator_y * centro_x],
            ]
        )
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
            fator = self._normalizar_fator_zoom(
                nome_transformacao, self.zoom_fator_valor.get()
            )
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
            return (
                f"Escala (x={parametros['fator_x']:.2f}, y={parametros['fator_y']:.2f})"
            )
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
            self.label_status_composicao.config(
                text=f"Executando passo {self.indice_composicao + 1} de {len(self.sequencia_composicao)}."
            )
            return

        self.label_status_composicao.config(text=f"{total} transformação(ões) na fila.")

    def adicionar_transformacao_composta(self):
        nome_transformacao = self.transformacao_para_adicionar.get()
        if nome_transformacao not in self.opcoes_transformacoes_compostas:
            messagebox.showwarning(
                "Aviso", "Selecione uma transformação válida para adicionar."
            )
            return

        parametros = self._capturar_parametros_transformacao(nome_transformacao)
        item = {
            "nome": nome_transformacao,
            "parametros": parametros,
        }
        self.fila_transformacoes_compostas.append(item)

        descricao = self._formatar_transformacao_composta(
            nome_transformacao, parametros
        )
        self.lista_transformacoes_compostas.insert(
            tk.END, f"{len(self.fila_transformacoes_compostas)}. {descricao}"
        )

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
            messagebox.showwarning(
                "Aviso", "Selecione uma transformação da fila para remover."
            )
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
            descricao = self._formatar_transformacao_composta(
                item["nome"], item["parametros"]
            )
            self.lista_transformacoes_compostas.insert(tk.END, f"{indice}. {descricao}")

        self.composicao_ativa = False
        self.indice_composicao = 0
        self.sequencia_composicao = []
        self.imagem_composicao_atual = None
        self._atualizar_status_composicao()

    def _aplicar_transformacao_por_nome(
        self, imagem, nome_transformacao, parametros=None
    ):
        parametros = {} if parametros is None else parametros

        if nome_transformacao == "Rotação":
            return self._aplicar_rotacao(
                imagem, parametros.get("angulo", self.rotacao_valor.get())
            )
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
            return self._aplicar_reflexao(
                imagem, parametros.get("reflexao", self.reflexao_valor.get())
            )
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
                (
                    self.altura_canvas_transformacao,
                    self.largura_canvas_transformacao,
                    3,
                ),
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
                (
                    self.altura_canvas_transformacao,
                    self.largura_canvas_transformacao,
                    3,
                ),
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
                dst_y_ini : dst_y_ini + altura_colada,
                dst_x_ini : dst_x_ini + largura_colada,
            ] = imagem[
                src_y_ini : src_y_ini + altura_colada,
                src_x_ini : src_x_ini + largura_colada,
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
        imagem_temp = self._aplicar_translacao(
            imagem_temp, self.transladx_valor.get(), self.translady_valor.get()
        )
        imagem_temp = self._aplicar_escala(
            imagem_temp, self.escalax_valor.get(), self.escalay_valor.get()
        )
        imagem_temp = self._aplicar_cisalhamento(
            imagem_temp, self.cisalhox_valor.get(), self.cisalhoy_valor.get()
        )
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
            messagebox.showinfo(
                "Informação",
                "Selecione o modo 'Transformação composta' para usar o botão Próxima.",
            )
            return

        if not self.composicao_ativa:
            self.sequencia_composicao = list(self.fila_transformacoes_compostas)
            self.indice_composicao = 0
            self.imagem_composicao_atual = self._criar_canvas_base_transformacao()

            if not self.sequencia_composicao:
                messagebox.showwarning(
                    "Aviso",
                    "Adicione ao menos uma transformação na fila da composição.",
                )
                return

            self.composicao_ativa = True
            self._atualizar_status_composicao()

        if self.indice_composicao >= len(self.sequencia_composicao):
            messagebox.showinfo(
                "Informação",
                "A transformação composta já foi concluída. Clique em Próxima novamente para reiniciar com os valores atuais.",
            )
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
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"),
                ("Todos os arquivos", "*.*"),
            ],
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
            self.label_img1.config(
                text=f"Imagem 1: {Path(self.imagem1.imageName).name}"
            )
        else:
            if self.imagem2 is not None:
                cv2.destroyWindow(self.imagem2.imageName)

            self.imagem2 = nova_imagem
            self.imagem2.showImage()
            self.label_img2.config(
                text=f"Imagem 2: {Path(self.imagem2.imageName).name}"
            )

        if self.imagem1 is not None and self.imagem2 is not None:
            self.imagem2.resizeImage(self.imagem1.largura, self.imagem1.altura)

    def aplicar_operacao(self):
        """Aplica a operação escolhida nas duas imagens"""
        from implementacaoPrimeiraUnidade import ImageOperation

        operacao_escolhida = self.combo_operacoes.get()

        if self.imagem1 is None or self.imagem2 is None:
            messagebox.showwarning(
                "Aviso", "Selecione as duas imagens antes de gerar o resultado."
            )
            return

        if operacao_escolhida not in self.dicionario_operacoes:
            messagebox.showwarning("Aviso", "Selecione uma operação válida.")
            return

        self.imagem2.resizeImage(self.imagem1.largura, self.imagem1.altura)

        resultado = ImageOperation(
            self.imagem1, self.imagem2, self.dicionario_operacoes[operacao_escolhida]
        ).result
        # mostrar apenas o resultado (originais já estão sendo exibidas separadamente)
        try:
            resultado.showImage()
        except Exception:
            try:
                cv2.imshow(f"Resultado - Operação ({operacao_escolhida})", resultado.image)
            except Exception:
                pass

    def _criar_aba_filtros(self, parent):
        """Cria a aba para filtros passa-baixa e passa-alta"""
        tk.Label(parent, text="Filtros", font=("Arial", 14, "bold")).pack(pady=15)

        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)

        self.label_img_filtros = tk.Label(
            frame_selecao,
            text="Nenhuma imagem selecionada",
            font=("Arial", 10),
            foreground="red",
        )
        self.label_img_filtros.pack(side="left", padx=10)

        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_filtros,
        ).pack(side="left", padx=10)

        frame_modo_cor = tk.LabelFrame(
            parent, text="Modo para imagens coloridas", padx=10, pady=8
        )
        frame_modo_cor.pack(fill="x", padx=10, pady=(0, 10))

        tk.Radiobutton(
            frame_modo_cor,
            text="YUV (filtrar luminância)",
            variable=self.filtro_modo_cor,
            value="yuv",
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_modo_cor,
            text="Canais individuais (RGB)",
            variable=self.filtro_modo_cor,
            value="channels",
        ).pack(anchor="w", padx=10)

        frame_categoria = tk.LabelFrame(parent, text="Categoria", padx=10, pady=8)
        frame_categoria.pack(fill="x", padx=10, pady=(0, 10))

        tk.Radiobutton(
            frame_categoria,
            text="Passa-baixa",
            variable=self.filtro_categoria,
            value="passa_baixa",
            command=self._atualizar_opcoes_filtro,
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            frame_categoria,
            text="Passa-alta",
            variable=self.filtro_categoria,
            value="passa_alta",
            command=self._atualizar_opcoes_filtro,
        ).pack(side="left", padx=10)

        frame_tipo = tk.LabelFrame(parent, text="Filtro", padx=10, pady=8)
        frame_tipo.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame_tipo, text="Selecione:").pack(side="left", padx=(0, 8))
        self.combo_filtro_tipo = ttk.Combobox(
            frame_tipo,
            textvariable=self.filtro_tipo,
            state="readonly",
            width=30,
        )
        self.combo_filtro_tipo.pack(side="left", fill="x", expand=True)
        self.combo_filtro_tipo.bind(
            "<<ComboboxSelected>>", lambda _event: self._atualizar_parametros_filtro()
        )

        self.frame_parametros_filtro = tk.LabelFrame(
            parent, text="Parâmetros", padx=10, pady=8
        )
        self.frame_parametros_filtro.pack(fill="x", padx=10, pady=(0, 10))

        self._atualizar_opcoes_filtro()

        tk.Button(
            parent,
            text="Aplicar Filtro",
            command=self.aplicar_filtro,
            bg="#212F22",
            fg="white",
            font=("Arial", 11, "bold"),
        ).pack(pady=20, fill="x", padx=10)

    def _opcoes_filtro_por_categoria(self):
        if self.filtro_categoria.get() == "passa_alta":
            return ["H1", "H2", "M1", "M2", "M3", "Alto-reforço (High-Boost)"]

        return [
            "Média",
            "Mediana",
            "Máximo",
            "Mínimo",
            "Moda",
            "Kawahara",
            "Tomita e Tsuji",
            "Nagao e Matsuyama",
            "Somboonkaew",
        ]

    def _atualizar_opcoes_filtro(self):
        opcoes = self._opcoes_filtro_por_categoria()
        if self.combo_filtro_tipo is not None:
            self.combo_filtro_tipo.configure(values=opcoes)

        if self.filtro_tipo.get() not in opcoes:
            self.filtro_tipo.set(opcoes[0])

        self._atualizar_parametros_filtro()

    def _atualizar_parametros_filtro(self):
        if self.frame_parametros_filtro is None:
            return

        for widget in self.frame_parametros_filtro.winfo_children():
            widget.destroy()

        tipo = self.filtro_tipo.get()

        if tipo in {"Média", "Mediana"}:
            tk.Label(self.frame_parametros_filtro, text="Tamanho da máscara:").pack(
                anchor="w", pady=(0, 5)
            )
            tk.Radiobutton(
                self.frame_parametros_filtro,
                text="3x3",
                variable=self.filtro_tamanho,
                value=3,
            ).pack(side="left", padx=10)
            tk.Radiobutton(
                self.frame_parametros_filtro,
                text="5x5",
                variable=self.filtro_tamanho,
                value=5,
            ).pack(side="left", padx=10)
        elif tipo == "Alto-reforço (High-Boost)":
            frame_a = tk.Frame(self.frame_parametros_filtro)
            frame_a.pack(fill="x", pady=5)
            tk.Label(frame_a, text="Fator A:", width=14).pack(side="left")
            tk.Scale(
                frame_a,
                from_=1.0,
                to=5.0,
                orient="horizontal",
                resolution=0.1,
                variable=self.filtro_high_boost_a,
            ).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_a, textvariable=self.filtro_high_boost_a, width=5).pack(
                side="left"
            )
        else:
            tk.Label(
                self.frame_parametros_filtro,
                text="Este filtro usa máscara fixa.",
                font=("Arial", 9),
            ).pack(anchor="w")

    def selecionar_imagem_filtros(self):
        """Seleciona uma imagem para filtros"""
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
            self.imagem_para_filtros = Image(caminho)
            self.label_img_filtros.config(
                text=f"Imagem: {Path(caminho).name}",
                foreground="green",
            )
            try:
                self.imagem_para_filtros.showImage()
            except Exception:
                pass
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{erro}")

    def aplicar_filtro(self):
        """Aplica o filtro selecionado"""
        from implementacaoPrimeiraUnidade import ImageFilter

        if self.imagem_para_filtros is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            filtro = ImageFilter(
                self.imagem_para_filtros,
                color_mode=self.filtro_modo_cor.get(),
            )
            tipo = self.filtro_tipo.get()

            if tipo == "Média":
                resultado = filtro.media(self.filtro_tamanho.get())
            elif tipo == "Mediana":
                resultado = filtro.mediana(self.filtro_tamanho.get())
            elif tipo == "Máximo":
                resultado = filtro.maximo()
            elif tipo == "Mínimo":
                resultado = filtro.minimo()
            elif tipo == "Moda":
                resultado = filtro.moda()
            elif tipo == "Kawahara":
                resultado = filtro.kawahara()
            elif tipo == "Tomita e Tsuji":
                resultado = filtro.tomita_tsuji()
            elif tipo == "Nagao e Matsuyama":
                resultado = filtro.nagao_matsuyama()
            elif tipo == "Somboonkaew":
                resultado = filtro.somboonkaew()
            elif tipo in {"H1", "H2", "M1", "M2", "M3"}:
                resultado = filtro.passa_alta(tipo)
            elif tipo == "Alto-reforço (High-Boost)":
                resultado = filtro.alto_reforco(self.filtro_high_boost_a.get())
            else:
                messagebox.showwarning("Aviso", "Selecione um filtro válido.")
                return

            cv2.imshow(f"Resultado - Filtro ({tipo})", resultado)
            cv2.waitKey(1)
            messagebox.showinfo("Sucesso", "Filtro aplicado com sucesso!")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao aplicar filtro:\n{erro}")

    def _criar_aba_meio_tom(self, parent):
        """Cria a aba para técnicas de meio-tom"""
        tk.Label(parent, text="Meio-tom", font=("Arial", 14, "bold")).pack(pady=15)

        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)

        self.label_img_meio_tom = tk.Label(
            frame_selecao,
            text="Nenhuma imagem selecionada",
            font=("Arial", 10),
            foreground="red",
        )
        self.label_img_meio_tom.pack(side="left", padx=10)

        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_meio_tom,
        ).pack(side="left", padx=10)

        frame_categoria = tk.LabelFrame(parent, text="Técnica", padx=10, pady=8)
        frame_categoria.pack(fill="x", padx=10, pady=(0, 10))

        tk.Radiobutton(
            frame_categoria,
            text="Pontilhado Ordenado",
            variable=self.meio_tom_categoria,
            value="ordenado",
            command=self._atualizar_opcoes_meio_tom,
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_categoria,
            text="Pontilhado com Difusão",
            variable=self.meio_tom_categoria,
            value="difusao",
            command=self._atualizar_opcoes_meio_tom,
        ).pack(anchor="w", padx=10)

        frame_tipo = tk.LabelFrame(parent, text="Método", padx=10, pady=8)
        frame_tipo.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame_tipo, text="Selecione:").pack(side="left", padx=(0, 8))
        self.combo_meio_tom_tipo = ttk.Combobox(
            frame_tipo,
            textvariable=self.meio_tom_tipo,
            state="readonly",
            width=30,
        )
        self.combo_meio_tom_tipo.pack(side="left", fill="x", expand=True)

        self._atualizar_opcoes_meio_tom()

        tk.Button(
            parent,
            text="Aplicar Meio-tom",
            command=self.aplicar_meio_tom,
            bg="#212F22",
            fg="white",
            font=("Arial", 11, "bold"),
        ).pack(pady=20, fill="x", padx=10)

    def _opcoes_meio_tom_por_categoria(self):
        if self.meio_tom_categoria.get() == "difusao":
            return [
                "Floyd e Steinberg",
                "Rogers",
                "Jarvis, Judice e Ninke",
                "Stucki",
                "Stevenson e Arce",
            ]

        return ["2x2", "2x3", "3x3"]

    def _atualizar_opcoes_meio_tom(self):
        opcoes = self._opcoes_meio_tom_por_categoria()
        if self.combo_meio_tom_tipo is not None:
            self.combo_meio_tom_tipo.configure(values=opcoes)

        if self.meio_tom_tipo.get() not in opcoes:
            self.meio_tom_tipo.set(opcoes[0])

    def selecionar_imagem_meio_tom(self):
        """Seleciona uma imagem para meio-tom"""
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
            self.imagem_para_meio_tom = Image(caminho)
            self.label_img_meio_tom.config(
                text=f"Imagem: {Path(caminho).name}",
                foreground="green",
            )
            try:
                self.imagem_para_meio_tom.showImage()
            except Exception:
                pass
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{erro}")

    def aplicar_meio_tom(self):
        """Aplica a técnica de meio-tom selecionada"""
        from implementacaoPrimeiraUnidade import Halftoning

        if self.imagem_para_meio_tom is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            meio_tom = Halftoning(self.imagem_para_meio_tom)
            tipo = self.meio_tom_tipo.get()

            if self.meio_tom_categoria.get() == "ordenado":
                resultado = meio_tom.pontilhado_ordenado(tipo)
            elif self.meio_tom_categoria.get() == "difusao":
                resultado = meio_tom.difusao_erro(tipo)
            else:
                messagebox.showwarning("Aviso", "Selecione uma técnica válida.")
                return

            cv2.imshow(f"Resultado - Meio-tom ({tipo})", resultado)
            cv2.waitKey(1)
            messagebox.showinfo("Sucesso", "Meio-tom aplicado com sucesso!")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao aplicar meio-tom:\n{erro}")

    def _criar_aba_realce(self, parent):
        """Cria a aba para realce e transformações de contraste"""
        tk.Label(parent, text="Realce e Transformações de Contraste", font=("Arial", 14, "bold")).pack(pady=15)

        # Seleção de Imagem
        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)
        self.label_img_realce = tk.Label(
            frame_selecao,
            text="Nenhuma imagem selecionada",
            font=("Arial", 10),
            foreground="red",
        )
        self.label_img_realce.pack(side="left", padx=10)
        tk.Button(
            frame_selecao,
            text="Selecionar Imagem",
            command=self.selecionar_imagem_realce,
        ).pack(side="left", padx=10)

        # Seleção de Tipo de Realce
        frame_tipo = tk.LabelFrame(parent, text="Tipo de Transformação", padx=10, pady=8)
        frame_tipo.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame_tipo, text="Selecione o tipo:", font=("Arial", 10)).pack(anchor="w")

        tipos_realce = [
            ("Linear - Mapeamento (Min/Max)", "linear_a_mapeamento"),
            ("Linear - Por Partes", "linear_b_partes"),
            ("Linear - Inversa (Negativo)", "linear_c_inversa"),
            ("Linear - Binária (Thresholding)", "linear_d_binaria"),
            ("Não-Linear - Logarítmica", "nlinear_logaritmica"),
            ("Não-Linear - Raiz", "nlinear_raiz"),
            ("Não-Linear - Exponencial", "nlinear_exponencial"),
            ("Não-Linear - Quadrado", "nlinear_quadrado"),
            ("Fatiamento de Bits", "fatiamento_bits"),
            ("Equalização de Histograma", "equalizacao_histograma"),
            ("Ajuste de brilho - Correção Gama", "correcao_gama"),
        ]

        for label, valor in tipos_realce:
            tk.Radiobutton(
                frame_tipo,
                text=label,
                variable=self.realce_tipo,
                value=valor,
                command=self._atualizar_parametros_realce,
            ).pack(anchor="w", padx=10)

        # Frame de Parâmetros
        self.frame_parametros_realce = tk.LabelFrame(parent, text="Parâmetros", padx=10, pady=8)
        self.frame_parametros_realce.pack(fill="x", padx=10, pady=(0, 10))

        self._atualizar_parametros_realce()

        # Botão Aplicar
        btn_aplicar = tk.Button(
            parent,
            text="Aplicar Realce",
            command=self.aplicar_realce,
            bg="#212F22",
            fg="white",
            font=("Arial", 11, "bold"),
        )
        btn_aplicar.pack(pady=20, fill="x", padx=10)

    def _atualizar_parametros_realce(self):
        """Atualiza os parâmetros exibidos baseado no tipo de realce selecionado"""
        # Limpa os widgets anteriores
        for widget in self.frame_parametros_realce.winfo_children():
            widget.destroy()

        tipo = self.realce_tipo.get()

        if tipo == "linear_a_mapeamento":
            tk.Label(self.frame_parametros_realce, text="Mapeamento Linear (f → g)", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            frame_g_min = tk.Frame(self.frame_parametros_realce)
            frame_g_min.pack(fill="x", pady=5)
            tk.Label(frame_g_min, text="g_min (saída mínima):", width=20).pack(side="left")
            tk.Scale(frame_g_min, from_=0, to=255, orient="horizontal", variable=self.realce_g_min).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_g_min, textvariable=self.realce_g_min, width=5).pack(side="left")

            frame_g_max = tk.Frame(self.frame_parametros_realce)
            frame_g_max.pack(fill="x", pady=5)
            tk.Label(frame_g_max, text="g_max (saída máxima):", width=20).pack(side="left")
            tk.Scale(frame_g_max, from_=0, to=255, orient="horizontal", variable=self.realce_g_max).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_g_max, textvariable=self.realce_g_max, width=5).pack(side="left")

            tk.Label(self.frame_parametros_realce, text="Expande o intervalo dinâmico da imagem", font=("Arial", 8, "italic")).pack(anchor="w", pady=(10, 0))

        elif tipo == "linear_b_partes":
            tk.Label(self.frame_parametros_realce, text="Mapeamento Linear por Partes", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            # Container para intervalos dinâmicos
            self.frame_intervalos_realce = tk.Frame(self.frame_parametros_realce)
            self.frame_intervalos_realce.pack(fill="x", pady=5)

            # Reinicia os intervalos ao entrar neste modo para evitar refs para widgets destruídos
            self.linear_b_intervals = []

            # Botões de controle
            controles = tk.Frame(self.frame_parametros_realce)
            controles.pack(fill="x", pady=(3, 8))
            tk.Button(controles, text="+ Adicionar Intervalo", command=self._adicionar_intervalo_realce).pack(side="left")

            # Se não existir nenhum intervalo, adiciona um padrão
            if not self.linear_b_intervals:
                self._adicionar_intervalo_realce()

        elif tipo == "linear_c_inversa":
            tk.Label(self.frame_parametros_realce, text="Transformação Inversa", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))
            tk.Label(self.frame_parametros_realce, text="Nega a imagem: g(x,y) = 255 - f(x,y)", font=("Arial", 8)).pack(anchor="w")

        elif tipo == "linear_d_binaria":
            tk.Label(self.frame_parametros_realce, text="Transformação Binária (Thresholding)", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            frame_limiar = tk.Frame(self.frame_parametros_realce)
            frame_limiar.pack(fill="x", pady=5)
            tk.Label(frame_limiar, text="Limiar:", width=20).pack(side="left")
            tk.Scale(frame_limiar, from_=0, to=255, orient="horizontal", variable=self.realce_limiar).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_limiar, textvariable=self.realce_limiar, width=5).pack(side="left")

            tk.Label(self.frame_parametros_realce, text="Pixels acima do limiar → 255, abaixo → 0", font=("Arial", 8, "italic")).pack(anchor="w", pady=(10, 0))

        elif tipo == "nlinear_logaritmica":
            tk.Label(self.frame_parametros_realce, text="Transformação Logarítmica", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))
            tk.Label(self.frame_parametros_realce, text="g(x,y) = c * log(1 + f(x,y)) — Expande áreas escuras", font=("Arial", 8)).pack(anchor="w")

        elif tipo == "nlinear_raiz":
            tk.Label(self.frame_parametros_realce, text="Transformação Raiz", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))
            tk.Label(self.frame_parametros_realce, text="g(x,y) = c * √f(x,y) — Clareia a imagem (Gamma 0.5)", font=("Arial", 8)).pack(anchor="w")

        elif tipo == "nlinear_exponencial":
            tk.Label(self.frame_parametros_realce, text="Transformação Exponencial", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            frame_gamma = tk.Frame(self.frame_parametros_realce)
            frame_gamma.pack(fill="x", pady=5)
            tk.Label(frame_gamma, text="Gamma:", width=20).pack(side="left")
            tk.Scale(frame_gamma, from_=0.5, to=3.0, orient="horizontal", variable=self.realce_gamma, resolution=0.1).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_gamma, text=f"{self.realce_gamma.get():.1f}", width=5).pack(side="left")

            tk.Label(self.frame_parametros_realce, text="g(x,y) = 255 * (f(x,y)/255)^γ — Escurece (γ>1) ou clareia (γ<1)", font=("Arial", 8, "italic")).pack(anchor="w", pady=(10, 0))

        elif tipo == "correcao_gama":
            tk.Label(self.frame_parametros_realce, text="Correção Gama", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            frame_gamma = tk.Frame(self.frame_parametros_realce)
            frame_gamma.pack(fill="x", pady=5)
            tk.Label(frame_gamma, text="Gama:", width=20).pack(side="left")
            tk.Scale(frame_gamma, from_=0.1, to=3.0, orient="horizontal", variable=self.realce_gamma, resolution=0.1).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_gamma, text=f"{self.realce_gamma.get():.1f}", width=5).pack(side="left")

            tk.Label(self.frame_parametros_realce, text="Aplica correção gama: g = 255*(f/255)^γ — ajuste fino do brilho", font=("Arial", 8, "italic")).pack(anchor="w", pady=(10, 0))

        elif tipo == "fatiamento_bits":
            tk.Label(self.frame_parametros_realce, text="Fatiamento de Bits", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))

            frame_bit = tk.Frame(self.frame_parametros_realce)
            frame_bit.pack(fill="x", pady=5)
            tk.Label(frame_bit, text="Plano (0-7):", width=20).pack(side="left")
            tk.Scale(frame_bit, from_=0, to=7, orient="horizontal", variable=self.realce_bit_plane).pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(frame_bit, textvariable=self.realce_bit_plane, width=4).pack(side="left")

            tk.Label(self.frame_parametros_realce, text="Extrai o plano de bits especificado (0 = LSB, 7 = MSB)", font=("Arial", 8, "italic")).pack(anchor="w", pady=(10, 0))

        elif tipo == "nlinear_quadrado":
            tk.Label(self.frame_parametros_realce, text="Transformação Quadrado", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))
            tk.Label(self.frame_parametros_realce, text="g(x,y) = c * f(x,y)² (Gamma 2.0) — Escurece significativamente", font=("Arial", 8)).pack(anchor="w")

        elif tipo == "equalizacao_histograma":
            tk.Label(self.frame_parametros_realce, text="Equalização de Histograma", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 10))
            tk.Label(self.frame_parametros_realce, text="Redistribui os pixels uniformemente ao longo do intervalo de intensidade — Aumenta o contraste global", font=("Arial", 8)).pack(anchor="w")

    def selecionar_imagem_realce(self):
        """Seleciona uma imagem para realce"""
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
            self.imagem_para_realce = Image(caminho)
            self.label_img_realce.config(
                text=f"Imagem: {Path(caminho).name}",
                foreground="green"
            )
            try:
                self.imagem_para_realce.showImage()
            except Exception:
                pass
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{erro}")

    def _criar_aba_segmentacao(self, parent):
        tk.Label(parent, text="Segmentação de Imagem", font=("Arial", 14, "bold")).pack(pady=15)

        frame_selecao = tk.Frame(parent)
        frame_selecao.pack(pady=10)

        self.label_img_segmentacao = tk.Label(frame_selecao, text="Nenhuma imagem selecionada", font=("Arial", 10), foreground="red")
        self.label_img_segmentacao.pack(side="left", padx=10)

        tk.Button(frame_selecao, text="Selecionar Imagem", command=self.selecionar_imagem_segmentacao).pack(side="left", padx=10)

        # Modo de segmentação (vertical)
        frame_tipo = tk.LabelFrame(parent, text="Modo de Segmentação", padx=10, pady=8)
        frame_tipo.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame_tipo, text="Selecione o modo:", font=("Arial", 10)).pack(anchor="w")

        tk.Radiobutton(
            frame_tipo,
            text="Detecção de Pontos",
            variable=self.segmentacao_mode,
            value="pontos",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_tipo,
            text="Detecção de Retas",
            variable=self.segmentacao_mode,
            value="retas",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_tipo,
            text="Detecção de Bordas",
            variable=self.segmentacao_mode,
            value="bordas",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_tipo,
            text="Limiarização",
            variable=self.segmentacao_mode,
            value="limiarizacao",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(anchor="w", padx=10)
        tk.Radiobutton(
            frame_tipo,
            text="Crescimento de Regiões",
            variable=self.segmentacao_mode,
            value="crescimento_regioes",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(anchor="w", padx=10)

        # Frame de parâmetros específicos
        self.frame_parametros_segmentacao = tk.LabelFrame(parent, text="Parâmetros", padx=10, pady=8)
        self.frame_parametros_segmentacao.pack(fill="x", padx=10, pady=(0, 10))

        # Parâmetro T geral (usado por pontos e retas)
        frame_param_t = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_param_t, text="Limiar T:", width=15).pack(side="left")
        tk.Scale(frame_param_t, from_=0, to=255, orient="horizontal", variable=self.segmentacao_T).pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(frame_param_t, textvariable=self.segmentacao_T, width=4).pack(side="left")
        self.frame_param_t = frame_param_t

        # Direção (para retas)
        frame_dir = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_dir, text="Direção:", width=15).pack(side="left")
        combo_dir = ttk.Combobox(
            frame_dir,
            values=["horizontal", "vertical", "45", "135"],
            state="readonly",
            textvariable=self.segmentacao_direcao,
            width=12,
        )
        combo_dir.pack(side="left", padx=5)
        self.frame_param_direcao = frame_dir

        # Método de bordas
        frame_borda = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_borda, text="Método:", width=15).pack(side="left")
        combo_borda = ttk.Combobox(
            frame_borda,
            values=[
                "roberts",
                "roberts_cruzado",
                "prewitt_gx",
                "prewitt_gy",
                "prewitt_magnitude",
                "sobel_gx",
                "sobel_gy",
                "sobel_magnitude",
                "kirsch",
                "robinson",
                "frei_chen",
                "laplaciano_h1",
                "laplaciano_h2",
            ],
            state="readonly",
            textvariable=self.segmentacao_metodo_borda,
            width=20,
        )
        combo_borda.pack(side="left", padx=5)
        self.frame_param_borda = frame_borda

        # Tipo de limiarização (global/local)
        frame_lim_tipo = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_lim_tipo, text="Tipo de Lim.:", width=15).pack(side="left")
        tk.Radiobutton(
            frame_lim_tipo,
            text="Global",
            variable=self.segmentacao_tipo_lim,
            value="global",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(side="left", padx=3)
        tk.Radiobutton(
            frame_lim_tipo,
            text="Local",
            variable=self.segmentacao_tipo_lim,
            value="local",
            command=self._atualizar_opcoes_segmentacao,
        ).pack(side="left", padx=3)
        self.frame_param_lim_tipo = frame_lim_tipo

        # Método de limiarização local
        frame_lim_metodo = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_lim_metodo, text="Método:", width=15).pack(side="left")
        combo_lim = ttk.Combobox(
            frame_lim_metodo,
            values=["media", "minimo", "maximo", "niblack"],
            state="readonly",
            textvariable=self.segmentacao_metodo_lim,
            width=12,
        )
        combo_lim.pack(side="left", padx=5)
        combo_lim.bind("<<ComboboxSelected>>", lambda e: self._atualizar_opcoes_segmentacao())
        self.frame_param_lim_metodo = frame_lim_metodo

        # Vizinhança (n)
        frame_lim_n = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_lim_n, text="Vizinhança (n):", width=15).pack(side="left")
        tk.Scale(frame_lim_n, from_=3, to=21, orient="horizontal", variable=self.segmentacao_n_lim).pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(frame_lim_n, textvariable=self.segmentacao_n_lim, width=3).pack(side="left")
        self.frame_param_lim_n = frame_lim_n

        # K para Niblack
        frame_lim_k = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_lim_k, text="K (Niblack):", width=15).pack(side="left")
        tk.Scale(frame_lim_k, from_=-1.0, to=0.0, orient="horizontal", resolution=0.1, variable=self.segmentacao_k_lim).pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(frame_lim_k, textvariable=self.segmentacao_k_lim, width=5).pack(side="left")
        self.frame_param_lim_k = frame_lim_k

        # Crescimento de regiões
        frame_regiao_tol = tk.Frame(self.frame_parametros_segmentacao)
        tk.Label(frame_regiao_tol, text="Tolerância:", width=15).pack(side="left")
        tk.Scale(frame_regiao_tol, from_=0, to=255, orient="horizontal", variable=self.segmentacao_tolerancia_regiao).pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(frame_regiao_tol, textvariable=self.segmentacao_tolerancia_regiao, width=4).pack(side="left")
        self.frame_param_regiao_tol = frame_regiao_tol

        frame_regiao_sementes = tk.Frame(self.frame_parametros_segmentacao)
        tk.Button(frame_regiao_sementes, text="Selecionar Sementes", command=self.selecionar_sementes_segmentacao).pack(side="left", padx=(0, 8))
        self.label_sementes_segmentacao = tk.Label(frame_regiao_sementes, text="0 sementes selecionadas", foreground="red")
        self.label_sementes_segmentacao.pack(side="left")
        self.frame_param_regiao_sementes = frame_regiao_sementes

        # Botão Aplicar
        btn_aplicar = tk.Button(parent, text="Aplicar Segmentação", command=self.aplicar_segmentacao, bg="#212F22", fg="white", font=("Arial", 11, "bold"))
        btn_aplicar.pack(pady=20, fill="x", padx=10)

        self._atualizar_opcoes_segmentacao()

    def _atualizar_opcoes_segmentacao(self):
        """Atualiza a visibilidade dos controles baseado no modo selecionado"""
        # Limpa a visibilidade de todos os frames
        self.frame_param_t.pack_forget()
        self.frame_param_direcao.pack_forget()
        self.frame_param_borda.pack_forget()
        self.frame_param_lim_tipo.pack_forget()
        self.frame_param_lim_metodo.pack_forget()
        self.frame_param_lim_n.pack_forget()
        self.frame_param_lim_k.pack_forget()
        self.frame_param_regiao_tol.pack_forget()
        self.frame_param_regiao_sementes.pack_forget()

        modo = self.segmentacao_mode.get()

        if modo == "pontos":
            self.frame_param_t.pack(fill="x", pady=5)

        elif modo == "retas":
            self.frame_param_t.pack(fill="x", pady=5)
            self.frame_param_direcao.pack(fill="x", pady=5)

        elif modo == "bordas":
            self.frame_param_borda.pack(fill="x", pady=5)

        elif modo == "limiarizacao":
            self.frame_param_lim_tipo.pack(fill="x", pady=5)

            if self.segmentacao_tipo_lim.get() == "local":
                self.frame_param_lim_metodo.pack(fill="x", pady=5)
                self.frame_param_lim_n.pack(fill="x", pady=5)

                if self.segmentacao_metodo_lim.get() == "niblack":
                    self.frame_param_lim_k.pack(fill="x", pady=5)

        elif modo == "crescimento_regioes":
            self.frame_param_regiao_tol.pack(fill="x", pady=5)
            self.frame_param_regiao_sementes.pack(fill="x", pady=5)

    def selecionar_imagem_segmentacao(self):
        from implementacaoPrimeiraUnidade import Image

        caminho = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pgm"), ("Todos os arquivos", "*.*")])
        if not caminho:
            return
        try:
            self.imagem_para_segmentacao = Image(caminho)
            self.segmentacao_sementes = []
            self.label_img_segmentacao.config(text=Path(caminho).name, foreground="green")
            self._atualizar_label_sementes_segmentacao()
            try:
                self.imagem_para_segmentacao.showImage()
            except Exception:
                pass
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{erro}")

    def _atualizar_label_sementes_segmentacao(self):
        total = len(self.segmentacao_sementes)
        texto = "1 semente selecionada" if total == 1 else f"{total} sementes selecionadas"
        cor = "green" if total else "red"
        self.label_sementes_segmentacao.config(text=texto, foreground=cor)

    def selecionar_sementes_segmentacao(self):
        if self.imagem_para_segmentacao is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        janela = "Selecionar Sementes - Enter/Esc finaliza, C limpa"
        imagem_base = self.imagem_para_segmentacao.image.copy()
        if len(imagem_base.shape) == 2:
            imagem_base = cv2.cvtColor(imagem_base, cv2.COLOR_GRAY2BGR)

        visualizacao = imagem_base.copy()
        sementes = list(self.segmentacao_sementes)
        janela_aberta = False

        def redesenhar():
            visualizacao[:] = imagem_base
            for indice, (x, y) in enumerate(sementes, start=1):
                cv2.circle(visualizacao, (x, y), 4, (0, 0, 255), -1)
                cv2.putText(visualizacao, str(indice), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
            cv2.imshow(janela, visualizacao)

        def registrar_clique(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                sementes.append((x, y))
                redesenhar()

        try:
            cv2.namedWindow(janela)
            janela_aberta = True
            cv2.setMouseCallback(janela, registrar_clique)
            redesenhar()

            while True:
                if cv2.getWindowProperty(janela, cv2.WND_PROP_VISIBLE) < 1:
                    janela_aberta = False
                    break

                tecla = cv2.waitKey(20) & 0xFF
                if tecla in (13, 27):
                    break
                if tecla in (ord("c"), ord("C")):
                    sementes.clear()
                    redesenhar()

            self.segmentacao_sementes = sementes
            self._atualizar_label_sementes_segmentacao()
        except Exception as erro:
            messagebox.showerror("Erro", f"Não foi possível selecionar sementes:\n{erro}")
        finally:
            if janela_aberta:
                try:
                    cv2.setMouseCallback(janela, lambda *args: None)
                    cv2.destroyWindow(janela)
                    cv2.waitKey(1)
                except Exception:
                    pass

    def aplicar_segmentacao(self):
        from implementacaoPrimeiraUnidade import Segmentacao

        if self.imagem_para_segmentacao is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            seg = Segmentacao(self.imagem_para_segmentacao)
            if self.segmentacao_mode.get() == "pontos":
                resultado = seg.deteccao_pontos(self.segmentacao_T.get())
                win_title = "Segmentacao (Deteccao de Pontos)"
            elif self.segmentacao_mode.get() == "retas":
                direcao = self.segmentacao_direcao.get()
                resultado = seg.deteccao_retas(direcao, self.segmentacao_T.get())
                win_title = f"Segmentacao (Deteccao de Retas - {direcao})"
            elif self.segmentacao_mode.get() == "bordas":
                metodo = self.segmentacao_metodo_borda.get()
                resultado = seg.deteccao_bordas(metodo)
                win_title = f"Segmentacao (Deteccao de Bordas - {metodo})"
            elif self.segmentacao_mode.get() == "limiarizacao":
                if self.segmentacao_tipo_lim.get() == "global":
                    resultado = seg.limiarizacao_global()
                    win_title = "Segmentacao (Limiarizacao Global)"
                else:
                    metodo = self.segmentacao_metodo_lim.get()
                    n = self.segmentacao_n_lim.get()
                    if metodo == "niblack":
                        k = self.segmentacao_k_lim.get()
                        resultado = seg.limiarizacao_local(metodo, n, k)
                    else:
                        resultado = seg.limiarizacao_local(metodo, n)
                    win_title = f"Segmentacao (Limiarizacao Local - {metodo})"
            else:
                if not self.segmentacao_sementes:
                    messagebox.showwarning("Aviso", "Selecione pelo menos uma semente para o crescimento de regiões.")
                    return

                resultado = seg.crescimento_regioes(self.segmentacao_sementes, self.segmentacao_tolerancia_regiao.get())
                win_title = "Segmentacao (Crescimento de Regioes)"

            try:
                cv2.imshow(win_title, resultado)
                cv2.waitKey(1)
            except Exception:
                pass
            messagebox.showinfo("Sucesso", "Segmentação aplicada com sucesso!")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao aplicar segmentação:\n{erro}")

    def aplicar_realce(self):
        """Aplica a transformação de realce selecionada"""
        from implementacaoPrimeiraUnidade import Realce

        if self.imagem_para_realce is None:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro.")
            return

        try:
            realce = Realce(self.imagem_para_realce)
            tipo = self.realce_tipo.get()
            resultado = None

            if tipo == "linear_a_mapeamento":
                resultado = realce.aplicar_com_cores(
                    realce.linear_a_mapeamento,
                    self.realce_g_min.get(),
                    self.realce_g_max.get(),
                )

            elif tipo == "linear_b_partes":
                intervalos = [
                    (
                        data["f_min"].get(),
                        data["f_max"].get(),
                        data["g_min"].get(),
                        data["g_max"].get(),
                    )
                    for data in self.linear_b_intervals
                ]

                if not intervalos:
                    messagebox.showwarning(
                        "Aviso",
                        "Adicione ao menos um intervalo para aplicar o mapeamento por partes.",
                    )
                    return

                resultado = realce.aplicar_com_cores(realce.linear_b_partes, intervalos)

            elif tipo == "linear_c_inversa":
                resultado = realce.aplicar_com_cores(realce.linear_c_inversa)

            elif tipo == "linear_d_binaria":
                resultado = realce.aplicar_com_cores(
                    realce.linear_d_binaria,
                    self.realce_limiar.get()
                )

            elif tipo == "nlinear_logaritmica":
                resultado = realce.aplicar_com_cores(realce.nlinear_logaritmica)

            elif tipo == "nlinear_raiz":
                resultado = realce.aplicar_com_cores(realce.nlinear_raiz)

            elif tipo == "nlinear_exponencial":
                resultado = realce.aplicar_com_cores(
                    realce.nlinear_exponencial,
                    self.realce_gamma.get()
                )

            elif tipo == "correcao_gama":
                resultado = realce.aplicar_com_cores(
                    realce.correcao_gama,
                    self.realce_gamma.get()
                )

            elif tipo == "fatiamento_bits":
                resultado = realce.fatiamento_bits(self.realce_bit_plane.get())

            elif tipo == "nlinear_quadrado":
                resultado = realce.aplicar_com_cores(realce.nlinear_quadrado)

            elif tipo == "equalizacao_histograma":
                resultado = realce.aplicar_com_cores(realce.equalizacao_histograma)

            if resultado is not None:
                try:
                    cv2.imshow("Resultado - Realce", resultado)
                except Exception:
                    pass
                messagebox.showinfo("Sucesso", "Realce aplicado com sucesso!")

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao aplicar realce:\n{erro}")

    def run(self):
        """Inicia a interface"""
        self.root.mainloop()

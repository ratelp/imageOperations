import cv2
import numpy as np
import operator
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog

class Image:

    def __init__(self,imageName, image = None):
        self.image = cv2.imread(imageName) if image is None else image
        self.imageName = imageName
        self.altura, self.largura = self.image.shape[:2]

    def showImage(self):
        cv2.imshow(self.imageName,self.image)

    def resizeImage(self, largura, altura):
        self.image = cv2.resize(self.image, (largura, altura))

class ImageOperation:

    def __init__(self, image1, image2, operator):
        image1_float = image1.image.astype(np.int32)
        image2_float = image2.image.astype(np.int32) 

        result = operator(image1_float, image2_float)

        result = cv2.normalize(result, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        self.result = Image("Resultado",result.astype(np.uint8))


janela = tk.Tk()
janela.title("Painel de Operações")
janela.geometry("460x320")
janela.eval('tk::PlaceWindow . center') 

dicionario_operacoes = {
    "Soma": operator.add,
    "Subtração": operator.sub,
    "Multiplicação": operator.mul,
    "Divisão": operator.truediv,
    "AND": operator.and_,
    "OR": operator.or_,
    "XOR": operator.xor
}

imagem1 = None
imagem2 = None

tk.Label(janela, text="Escolha a operação:", font=("Arial", 11)).pack(pady=15)

label_img1 = tk.Label(janela, text="Imagem 1: nao selecionada", font=("Arial", 9))
label_img1.pack()

label_img2 = tk.Label(janela, text="Imagem 2: nao selecionada", font=("Arial", 9))
label_img2.pack(pady=(0, 8))

def selecionar_imagem(alvo):
    global imagem1, imagem2

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
        imagem1 = nova_imagem
        label_img1.config(text=f"Imagem 1: {Path(imagem1.imageName).name}")
    else:
        imagem2 = nova_imagem
        label_img2.config(text=f"Imagem 2: {Path(imagem2.imageName).name}")

    if imagem1 is not None and imagem2 is not None:
        imagem2.resizeImage(imagem1.largura, imagem1.altura)

frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=(0, 8))

tk.Button(frame_botoes, text="Selecionar Imagem 1", command=lambda: selecionar_imagem(1)).pack(side="left", padx=6)
tk.Button(frame_botoes, text="Selecionar Imagem 2", command=lambda: selecionar_imagem(2)).pack(side="left", padx=6)

combo_operacoes = ttk.Combobox(janela, values=list(dicionario_operacoes.keys()), state="readonly", width=20)
combo_operacoes.set("Selecione...")
combo_operacoes.pack(pady=5)

def aplicar_operacao():
    operacao_escolhida = combo_operacoes.get()

    if imagem1 is None or imagem2 is None:
        messagebox.showwarning("Aviso", "Selecione as duas imagens antes de gerar o resultado.")
        return

    if operacao_escolhida not in dicionario_operacoes:
        messagebox.showwarning("Aviso", "Selecione uma operação válida.")
        return

    imagem2.resizeImage(imagem1.largura, imagem1.altura)

    resultado = ImageOperation(imagem1, imagem2, dicionario_operacoes[operacao_escolhida]).result
    resultado.showImage()

btn_executar = tk.Button(janela, text="Gerar Resultado", command=aplicar_operacao, bg="#212F22", fg="white", font=("Arial", 10, "bold"))
btn_executar.pack(pady=15)

janela.mainloop()
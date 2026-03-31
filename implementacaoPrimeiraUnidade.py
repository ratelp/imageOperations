import cv2
import numpy as np
import tkinter as tk
from guiToPDI import ImageOperationGUI


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

class ImageTransformer:
    def  __init__(self, image):
        self.imagem_base = image.image

        self.imagem_preview = self.imagem_base.copy()

    def resetar_preview(self):
        self.imagem_preview = self.imagem_base.copy()
        return self.imagem_preview

    def rotacao(self, angulo):
        if angulo == 0:
            return self.imagem_preview

        altura, largura = self.imagem_preview.shape[:2]

        centro = (largura / 2, altura/ 2)

        matriz = cv2.getRotationMatrix2D(centro, angulo, 1.0)
        self.imagem_preview = cv2.warpAffine(self.imagem_preview, matriz, (largura, altura))

        return self.imagem_preview
    
    def transladar(self, deslocamento_x, deslocamento_y):
        if deslocamento_x == 0 and deslocamento_y == 0:
            return self.imagem_preview
            
        altura, largura = self.imagem_preview.shape[:2]
        
        matriz = np.float32([
            [1, 0, deslocamento_x],
            [0, 1, deslocamento_y]
        ])
        
        self.imagem_preview = cv2.warpAffine(self.imagem_preview, matriz, (largura, altura))
        
        return self.imagem_preview

    def escalar(self, fator_x, fator_y):
        if fator_x <= 0 or fator_y <= 0:
            return self.imagem_preview

        if fator_x == 1 and fator_y == 1:
            return self.imagem_preview
            
        altura, largura = self.imagem_preview.shape[:2]
        
        nova_largura = int(largura * fator_x)
        nova_altura = int(altura * fator_y)
        
        self.imagem_preview = cv2.resize(self.imagem_preview, (nova_largura, nova_altura))
        
        return self.imagem_preview

    def refletir(self, eixo):
        if eixo == 'nenhum':
            return self.imagem_preview
        if eixo == 'x':
            self.imagem_preview = cv2.flip(self.imagem_preview, 0)
        elif eixo == 'y':
            self.imagem_preview = cv2.flip(self.imagem_preview, 1)
        elif eixo == 'ambos':
            self.imagem_preview = cv2.flip(self.imagem_preview, -1)
            
        return self.imagem_preview

    def cisalhar(self, fator_x, fator_y):
        if fator_x == 0 and fator_y == 0:
            return self.imagem_preview
            
        altura, largura = self.imagem_preview.shape[:2]
        
        matriz = np.float32([
            [1, fator_x, 0],
            [fator_y, 1, 0]
        ])
        
        self.imagem_preview = cv2.warpAffine(self.imagem_preview, matriz, (largura, altura))
        
        return self.imagem_preview


if __name__ == "__main__":
    janela = tk.Tk()
    app = ImageOperationGUI(janela)
    app.run()
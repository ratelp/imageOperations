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

if __name__ == "__main__":
    janela = tk.Tk()
    app = ImageOperationGUI(janela)
    app.run()
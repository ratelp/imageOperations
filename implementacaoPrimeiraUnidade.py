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
            self.imagem_preview = cv2.flip(self.imagem_preview, 1)
        elif eixo == 'y':
            self.imagem_preview = cv2.flip(self.imagem_preview, 0)
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


    def zoom_in_replicacao(self, fator_zoom):
        if fator_zoom <= 1.0:
            return self.imagem_preview
        
        altura, largura = self.imagem_preview.shape[:2]

        nova_dim = (int(largura*fator_zoom),int(altura*fator_zoom))

        self.imagem_preview = cv2.resize(self.imagem_preview, nova_dim, interpolation=cv2.INTER_NEAREST)

        return self.imagem_preview
        
    def zoom_in_interpolacao(self, fator_zoom):
        if fator_zoom <= 1.0:
            return self.imagem_preview
        
        altura, largura = self.imagem_preview.shape[:2]

        nova_dim = (int(largura*fator_zoom),int(altura*fator_zoom))
        self.imagem_preview = cv2.resize(self.imagem_preview, nova_dim, interpolation=cv2.INTER_LINEAR)

        return self.imagem_preview
    
    def zoom_out_exclusao(self, fator_zoom):
        if fator_zoom >= 1.0:
            return self.imagem_preview
        
        altura, largura = self.imagem_preview.shape[:2]
        nova_dim = (int(largura*fator_zoom),int(altura*fator_zoom))

        self.imagem_preview =cv2.resize(self.imagem_preview, nova_dim, interpolation=cv2.INTER_NEAREST)

        return self.imagem_preview

    def zoom_out_valor_medio(self, fator_zoom):
        if fator_zoom >= 1.0:
            return self.imagem_preview
        
        altura, largura = self.imagem_preview.shape[:2]
        nova_dim = (int(largura*fator_zoom),int(altura*fator_zoom))

        self.imagem_preview =cv2.resize(self.imagem_preview, nova_dim, interpolation=cv2.INTER_AREA)

        return self.imagem_preview
        

class ColorSpaceDecomposer:
    def __init__(self, image):
        self.image = image.image

    def decompose(self, color_space):
        # opencv abre em bgr por padrão
        img_bgr = self.image
        altura, largura = img_bgr.shape[:2]
        preto = np.zeros((altura, largura), dtype=np.uint8)

        if color_space == "RGB":
            b, g, r = cv2.split(img_bgr)
            cv2.imshow("RGB - R (Red)", cv2.merge([preto, preto, r]))
            cv2.imshow("RGB - G (Green)", cv2.merge([preto, g, preto]))
            cv2.imshow("RGB - B (Blue)", cv2.merge([b, preto, preto]))

        elif color_space == "CMY":
            bgr_norm = img_bgr.astype(np.float32) / 255.0
            b, g, r = cv2.split(bgr_norm)
            c, m, y = 1.0 - r, 1.0 - g, 1.0 - b

            # para mostrar CMY colorido, convertemos cada um de volta para BGR
            # Cyan = G+B, Magenta = R+B, Yellow = R+G
            c_img = cv2.merge(
                [(c * 255).astype(np.uint8), (c * 255).astype(np.uint8), preto]
            )
            m_img = cv2.merge(
                [(m * 255).astype(np.uint8), preto, (m * 255).astype(np.uint8)]
            )
            y_img = cv2.merge(
                [preto, (y * 255).astype(np.uint8), (y * 255).astype(np.uint8)]
            )

            cv2.imshow("CMY - C (Cyan)", c_img)
            cv2.imshow("CMY - M (Magenta)", m_img)
            cv2.imshow("CMY - Y (Yellow)", y_img)

        elif color_space == "CMYK":
            bgr_norm = img_bgr.astype(np.float32) / 255.0
            b, g, r = cv2.split(bgr_norm)
            c, m, y = 1.0 - r, 1.0 - g, 1.0 - b
            k = np.minimum(np.minimum(c, m), y)

            c_k = (np.where(k == 1.0, 0, (c - k) / (1.0 - k)) * 255).astype(np.uint8)
            m_k = (np.where(k == 1.0, 0, (m - k) / (1.0 - k)) * 255).astype(np.uint8)
            y_k = (np.where(k == 1.0, 0, (y - k) / (1.0 - k)) * 255).astype(np.uint8)
            k_img = (k * 255).astype(np.uint8)

            cv2.imshow("CMYK - C", cv2.merge([c_k, c_k, preto]))
            cv2.imshow("CMYK - M", cv2.merge([m_k, preto, m_k]))
            cv2.imshow("CMYK - Y", cv2.merge([preto, y_k, y_k]))
            cv2.imshow("CMYK - K (Black)", k_img)

        elif color_space == "HSB":
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            self._split_and_show(
                hsv, ["H (Hue)", "S (Saturation)", "B/V (Brightness/Value)"], "HSB"
            )

        elif color_space == "HSL":
            hls = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HLS)
            channels = cv2.split(hls)
            cv2.imshow("HSL - H (Hue)", channels[0])
            cv2.imshow("HSL - S (Saturation)", channels[2])
            cv2.imshow("HSL - L (Lightness)", channels[1])

        elif color_space == "YUV":
            yuv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)

            # para mostrar yuv, mantemos o canal desejado e neutralizamos os outros para o valor médio (128)
            u_color = cv2.cvtColor(
                cv2.merge([np.full_like(y, 128), u, np.full_like(v, 128)]),
                cv2.COLOR_YUV2BGR,
            )
            v_color = cv2.cvtColor(
                cv2.merge([np.full_like(y, 128), np.full_like(u, 128), v]),
                cv2.COLOR_YUV2BGR,
            )

            cv2.imshow("YUV - Y (Luma)", y)
            cv2.imshow("YUV - U (Chroma Blue)", u_color)
            cv2.imshow("YUV - V (Chroma Red)", v_color)


class PseudoColorizer:
    def __init__(self, image):
        self.image = image.image

    def apply_slicing(self, min_val, max_val, color_bgr):
        img = self.image

        # Converter para escala de cinza se for colorida
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Converter de volta para BGR para poder aplicar cor
        colored = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # Criar máscara para o fatiamento
        mask = (gray >= min_val) & (gray <= max_val)

        # Aplicar a cor (OpenCV usa BGR)
        colored[mask] = color_bgr

        return colored

if __name__ == "__main__":
    janela = tk.Tk()
    app = ImageOperationGUI(janela)
    app.run()
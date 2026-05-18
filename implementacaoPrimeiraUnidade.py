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
        cv2.waitKey(1)

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

    def _split_and_show(self, img, titles, prefix=""):
        channels = cv2.split(img)
        for i, channel in enumerate(channels):
            if i < len(titles):
                cv2.imshow(f"{prefix} - {titles[i]}", channel)

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
            self._split_and_show(
                hls, ["H (Hue)", "L (Lightness)", "S (Saturation)"], "HSL"
            )

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

    def apply_slicing(self, intervals):
        img = self.image

        # Converter para escala de cinza se for colorida
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Converter de volta para BGR para poder aplicar cor
        colored = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # Criar máscaras para o fatiamento
        for min_val, max_val, color_bgr in intervals:
            mask = (gray >= min_val) & (gray <= max_val)
            colored[mask] = color_bgr

        return colored

    def apply_redistribution(self, colormap_type):
        img = self.image

        # inicialmente, converte imagem para escala de cinza
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        colored = cv2.applyColorMap(gray, colormap_type)
        return colored

class ImageFilter:
    def __init__(self, image, color_mode="yuv"):
        self.image = image.image
        self.color_mode = color_mode

    def _clip_uint8(self, image):
        return np.clip(image, 0, 255).astype(np.uint8)

    def _apply_to_gray_or_color(self, func):
        if len(self.image.shape) == 2:
            return func(self.image)

        if self.color_mode == "channels":
            channels = cv2.split(self.image)
            filtered_channels = [func(channel) for channel in channels]
            return cv2.merge(filtered_channels)

        img_yuv = cv2.cvtColor(self.image, cv2.COLOR_BGR2YUV)
        canal_y = img_yuv[:, :, 0]
        img_yuv[:, :, 0] = func(canal_y)
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    def media(self, tamanho):
        def aplicar_media(canal):
            raio = tamanho // 2
            padded = np.pad(canal, raio, mode="reflect").astype(np.float32)
            resultado = np.zeros_like(canal, dtype=np.float32)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + tamanho, x : x + tamanho]
                    resultado[y, x] = np.sum(janela) / (tamanho * tamanho)

            return self._clip_uint8(np.round(resultado))

        return self._apply_to_gray_or_color(aplicar_media)

    def mediana(self, tamanho):
        def aplicar_mediana(canal):
            raio = tamanho // 2
            padded = np.pad(canal, raio, mode="reflect")
            resultado = np.zeros_like(canal)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + tamanho, x : x + tamanho].reshape(-1)
                    resultado[y, x] = np.median(janela)

            return resultado.astype(np.uint8)

        return self._apply_to_gray_or_color(aplicar_mediana)

    def maximo(self):
        def aplicar_maximo(canal):
            tamanho = 3
            raio = tamanho // 2
            padded = np.pad(canal, raio, mode="reflect")
            resultado = np.zeros_like(canal)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + tamanho, x : x + tamanho]
                    resultado[y, x] = np.max(janela)

            return resultado

        return self._apply_to_gray_or_color(aplicar_maximo)

    def minimo(self):
        def aplicar_minimo(canal):
            tamanho = 3
            raio = tamanho // 2
            padded = np.pad(canal, raio, mode="reflect")
            resultado = np.zeros_like(canal)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + tamanho, x : x + tamanho]
                    resultado[y, x] = np.min(janela)

            return resultado

        return self._apply_to_gray_or_color(aplicar_minimo)

    def moda(self):
        def aplicar_moda(canal):
            padded = cv2.copyMakeBorder(
                canal, 1, 1, 1, 1, borderType=cv2.BORDER_REFLECT
            )
            resultado = np.zeros_like(canal)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + 3, x : x + 3].reshape(-1)
                    contagens = np.bincount(janela, minlength=256)
                    resultado[y, x] = np.argmax(contagens)

            return resultado

        return self._apply_to_gray_or_color(aplicar_moda)

    def _filtro_variancia_minima(self, regioes):
        def aplicar(canal):
            raio = 2
            padded = cv2.copyMakeBorder(
                canal, raio, raio, raio, raio, borderType=cv2.BORDER_REFLECT
            )
            resultado = np.zeros_like(canal)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + 5, x : x + 5].astype(np.float32)
                    melhor_media = 0
                    menor_variancia = None

                    for regiao_def in regioes:
                        if isinstance(regiao_def[0], slice):
                            linhas, colunas = regiao_def
                            regiao = janela[linhas, colunas]
                        else:
                            coordenadas = tuple(zip(*regiao_def))
                            regiao = janela[coordenadas]

                        variancia = np.var(regiao)
                        if menor_variancia is None or variancia < menor_variancia:
                            menor_variancia = variancia
                            melhor_media = np.mean(regiao)

                    resultado[y, x] = np.clip(round(melhor_media), 0, 255)

            return resultado.astype(np.uint8)

        return self._apply_to_gray_or_color(aplicar)

    def kawahara(self):
        regioes = [
            (slice(0, 3), slice(0, 3)),
            (slice(0, 3), slice(2, 5)),
            (slice(2, 5), slice(0, 3)),
            (slice(2, 5), slice(2, 5)),
        ]
        return self._filtro_variancia_minima(regioes)

    def tomita_tsuji(self):
        regioes = [
            (slice(0, 3), slice(0, 3)),
            (slice(0, 3), slice(2, 5)),
            (slice(2, 5), slice(0, 3)),
            (slice(2, 5), slice(2, 5)),
            (slice(1, 4), slice(1, 4)),
        ]
        return self._filtro_variancia_minima(regioes)

    def nagao_matsuyama(self):
        regioes = [
            [(0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2)],
            [(1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4)],
            [(2, 2), (3, 1), (3, 2), (3, 3), (4, 1), (4, 2), (4, 3)],
            [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1)],
            [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)],
            [(0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3)],
            [(2, 1), (2, 2), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)],
            [(2, 2), (2, 3), (3, 2), (3, 3), (3, 4), (4, 3), (4, 4)],
            (slice(1, 4), slice(1, 4))
        ]
        return self._filtro_variancia_minima(regioes)

    def somboonkaew(self):
        regioes = [
            [(0, 0), (1, 1), (1, 3), (2, 2), (3, 1), (3, 3), (4, 4)],
            [(0, 4), (1, 1), (1, 3), (2, 2), (3, 1), (3, 3), (4, 0)],
            [(1, 2), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 2)],
            [(0, 2), (1, 2), (2, 1), (2, 2), (2, 3), (3, 2), (4, 2)],
            [(1, 1), (1, 2), (1, 3), (2, 2), (3, 1), (3, 2), (3, 3)],
            [(1, 1), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 3)],
            [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 2), (3, 3)],
            [(1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2)],
            [(1, 2), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)],
            [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2)],
            [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 2)],
            [(1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 2), (3, 3)],
        ]
        return self._filtro_variancia_minima(regioes)

    def passa_alta(self, mascara):
        mascaras = {
            "H1": np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float32),
            "H2": np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32),
            "M1": np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32),
            "M2": np.array([[1, -2, 1], [-2, 5, -2], [1, -2, 1]], dtype=np.float32),
            "M3": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32),
        }
        kernel = mascaras[mascara]

        def aplicar_mascara(canal):
            padded = np.pad(canal, 1, mode="reflect").astype(np.float32)
            resultado = np.zeros_like(canal, dtype=np.float32)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + 3, x : x + 3]
                    resultado[y, x] = np.sum(janela * kernel)

            return self._clip_uint8(resultado)

        return self._apply_to_gray_or_color(aplicar_mascara)

    def alto_reforco(self, fator_a):
        def aplicar(canal):
            canal_float = canal.astype(np.float32)
            padded = np.pad(canal_float, 1, mode="reflect")
            baixa = np.zeros_like(canal_float)

            for y in range(canal.shape[0]):
                for x in range(canal.shape[1]):
                    janela = padded[y : y + 3, x : x + 3]
                    baixa[y, x] = np.sum(janela) / 9

            return self._clip_uint8((fator_a * canal_float) - baixa)

        return self._apply_to_gray_or_color(aplicar)


class Halftoning:
    def __init__(self, image):
        self.image = image.image

        if len(self.image.shape) == 3:
            self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.image_gray = self.image.copy()

    def pontilhado_ordenado(self, tamanho_matriz):
        matrizes = {
            "2x2": np.array([[0, 2], [3, 1]], dtype=np.float32),
            "2x3": np.array([[0, 4, 1], [5, 2, 3]], dtype=np.float32),
            "3x3": np.array(
                [
                    [6, 8, 4],
                    [1, 0, 3],
                    [5, 2, 7],
                ],
                dtype=np.float32,
            ),
        }

        matriz = matrizes[tamanho_matriz]
        matriz = ((matriz + 0.5) / matriz.size) * 255
        limiares = np.tile(matriz, (self.image_gray.shape[0] // len(matriz) + 1, self.image_gray.shape[1] // len(matriz[0]) + 1))[:self.image_gray.shape[0], :self.image_gray.shape[1]]

        resultado = ((self.image_gray > limiares) * 255).astype(np.uint8)

        return resultado

    def difusao_erro(self, tipo):
        kernels = {
            "Floyd e Steinberg": (
                16,
                [
                    (0, 1, 7),
                    (1, -1, 3),
                    (1, 0, 5),
                    (1, 1, 1),
                ],
            ),
            "Rogers": (
                8,
                [
                    (0, 1, 3),
                    (1, 0, 3),
                    (1, 1, 2),
                ],
            ),
            "Jarvis, Judice e Ninke": (
                48,
                [
                    (0, 1, 7),
                    (0, 2, 5),
                    (1, -2, 3),
                    (1, -1, 5),
                    (1, 0, 7),
                    (1, 1, 5),
                    (1, 2, 3),
                    (2, -2, 1),
                    (2, -1, 3),
                    (2, 0, 5),
                    (2, 1, 3),
                    (2, 2, 1),
                ],
            ),
            "Stucki": (
                42,
                [
                    (0, 1, 8),
                    (0, 2, 4),
                    (1, -2, 2),
                    (1, -1, 4),
                    (1, 0, 8),
                    (1, 1, 4),
                    (1, 2, 2),
                    (2, -2, 1),
                    (2, -1, 2),
                    (2, 0, 4),
                    (2, 1, 2),
                    (2, 2, 1),
                ],
            ),
            "Stevenson e Arce": (
                200,
                [
                    (0, 2, 32),
                    (1, -3, 12),
                    (1, -1, 26),
                    (1, 1, 30),
                    (1, 3, 16),
                    (2, -2, 12),
                    (2, 0, 26),
                    (2, 2, 12),
                    (3, -3, 5),
                    (3, -1, 12),
                    (3, 1, 12),
                    (3, 3, 5),
                ],
            ),
        }

        divisor, pesos = kernels[tipo]
        imagem_com_erros = self.image_gray.astype(np.float32).copy()
        resultado = np.zeros_like(self.image_gray, dtype=np.uint8)
        altura, largura = imagem_com_erros.shape

        for y in range(altura):
            for x in range(largura):
                valor_antigo = imagem_com_erros[y, x]
                valor_novo = 255 if valor_antigo >= 128 else 0
                resultado[y, x] = valor_novo
                erro = valor_antigo - valor_novo

                for desloc_y, desloc_x, peso in pesos:
                    vizinho_y = y + desloc_y
                    vizinho_x = x + desloc_x

                    if 0 <= vizinho_y < altura and 0 <= vizinho_x < largura:
                        imagem_com_erros[vizinho_y, vizinho_x] += erro * peso / divisor

        return resultado


class Realce:
    def __init__(self, image):
        self.image = image.image

        # passando para escala de cinza
        if len(self.image.shape) == 3:
            self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.image_gray = self.image.copy()

    def linear_a_mapeamento(self, g_min, g_max):
        f_min = np.min(self.image_gray)
        f_max = np.max(self.image_gray)

        img_float = self.image_gray.astype(np.float32)

        if f_max > f_min:
            resultado = ((img_float - f_min) / (f_max - f_min)) * (g_max - g_min) + g_min
        else:
            resultado = img_float

        return np.clip(resultado, 0, 255).astype(np.uint8)

    def linear_b_partes(self, intervalos):
        img_float = self.image_gray.astype(np.float32)
        resultado = np.zeros_like(img_float)

        for f_min, f_max, g_min, g_max in intervalos:
            mask = (img_float >= f_min) & (img_float <= f_max)

            if f_max > f_min:
                resultado[mask] = ((img_float[mask] - f_min) / (f_max - f_min)) * (g_max - g_min) + g_min
            else:
                resultado[mask] = g_min

        return np.clip(resultado, 0, 255).astype(np.uint8)

    def linear_c_inversa(self):
        return cv2.bitwise_not(self.image_gray)

    def linear_d_binaria(self, limiar):
        _, resultado = cv2.threshold(self.image_gray, limiar, 255, cv2.THRESH_BINARY)
        return resultado

    def nlinear_logaritmica(self):
        img_float = self.image_gray.astype(np.float32)

        c = 255.0 / np.log(1 + np.max(img_float))

        resultado = c * np.log(1 + img_float)
        return np.clip(resultado, 0, 255).astype(np.uint8)

    def nlinear_raiz(self):
        img_float = self.image_gray.astype(np.float32)

        c = 255.0 / np.sqrt(np.max(img_float))

        resultado = c * np.sqrt(img_float)
        return np.clip(resultado, 0, 255).astype(np.uint8)

    def nlinear_exponencial(self, gamma=1.5):
        img_float = self.image_gray.astype(np.float32)

        img_norm = img_float / 255.0
        resultado = 255.0 * (img_norm ** gamma)

        return np.clip(resultado, 0, 255).astype(np.uint8)

    def nlinear_quadrado(self):
        img_float = self.image_gray.astype(np.float32)

        c = 255.0 / (np.max(img_float) ** 2)

        resultado = c * (img_float ** 2)
        return np.clip(resultado, 0, 255).astype(np.uint8)

    def equalizacao_histograma(self):
        return cv2.equalizeHist(self.image_gray)

    def aplicar_com_cores(self, func_transformacao, *args):
        if len(self.image.shape) == 2:
            return func_transformacao(*args)

        img_yuv = cv2.cvtColor(self.image, cv2.COLOR_BGR2YUV)

        canal_y = img_yuv[:, :, 0]

        backup_gray = self.image_gray
        self.image_gray = canal_y

        canal_y_realcado = func_transformacao(*args)

        self.image_gray = backup_gray

        img_yuv[:, :, 0] = canal_y_realcado

        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    def correcao_gama(self, gamma):
        img_norm = self.image_gray.astype(np.float32) / 255.0

        resultado_norm = cv2.pow(img_norm, gamma)

        resultado = np.clip(resultado_norm * 255.0, 0, 255).astype(np.uint8)

        return resultado

    def fatiamento_bits(self, plano):
        plano = max(0, min(7, plano))

        mascara = 2 ** plano

        fatiado = cv2.bitwise_and(self.image_gray, mascara)

        _, resultado = cv2.threshold(fatiado, 0, 255, cv2.THRESH_BINARY)

        return resultado

class Segmentacao:
    def __init__(self, image):
        self.image = image.image

        if len(self.image.shape) == 3:
            self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            self.image_gray = self.image.copy()

    def deteccao_pontos(self, T):
        kernel = np.array([[-1, -1, -1],
                           [-1,  8, -1],
                           [-1, -1, -1]], dtype=np.float32)

        R = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel)

        R_abs = np.abs(R)

        _, resultado = cv2.threshold(R_abs, T, 255, cv2.THRESH_BINARY)

        return resultado.astype(np.uint8)

    def deteccao_retas(self, direcao, T):
        if direcao == 'horizontal':
            kernel = np.array([[-1, -1, -1],
                               [ 2,  2,  2],
                               [-1, -1, -1]], dtype=np.float32)

        elif direcao == 'vertical':
            kernel = np.array([[-1,  2, -1],
                               [-1,  2, -1],
                               [-1,  2, -1]], dtype=np.float32)

        elif direcao == '45':
            kernel = np.array([[-1, -1,  2],
                               [-1,  2, -1],
                               [ 2, -1, -1]], dtype=np.float32)

        elif direcao == '135':
            kernel = np.array([[ 2, -1, -1],
                               [-1,  2, -1],
                               [-1, -1,  2]], dtype=np.float32)
        else:
            raise ValueError("Direção inválida. Escolha entre: 'horizontal', 'vertical', '45', '135'")

        R = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel)

        R_abs = np.abs(R)

        _, resultado = cv2.threshold(R_abs, T, 255, cv2.THRESH_BINARY)

        return resultado.astype(np.uint8)

    def deteccao_bordas(self, metodo):
        if metodo == 'roberts':
            kernel_x = np.array([[-1, 0], [0, 1]], dtype=np.float32)
            kernel_y = np.array([[0, -1], [1, 0]], dtype=np.float32)
            return self._aplicar_gradiente_xy(kernel_x, kernel_y)
        elif metodo == 'roberts_cruzado':
            kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
            kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)
            return self._aplicar_gradiente_xy(kernel_x, kernel_y)
        elif metodo == 'prewitt_gx':
            kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel_x)
        elif metodo == 'prewitt_gy':
            kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel_y)
        elif metodo == 'prewitt_magnitude':
            kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
            kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
            return self._aplicar_gradiente_xy(kernel_x, kernel_y)
        elif metodo == 'sobel_gx':
            kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel_x)
        elif metodo == 'sobel_gy':
            kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel_y)
        elif metodo == 'sobel_magnitude':
            kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
            kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
            return self._aplicar_gradiente_xy(kernel_x, kernel_y)
        elif metodo == 'kirsch':
            kernels = [
                np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),
                np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float32),
                np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float32),
                np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float32),
                np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float32),
                np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float32),
                np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float32),
                np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float32)
            ]
            return self._aplicar_mascara_maxima(kernels)
        elif metodo == 'robinson':
            kernels = [
                np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32),
                np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]], dtype=np.float32),
                np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32),
                np.array([[0, -1, -2], [1, 0, -1], [2, 1, 0]], dtype=np.float32),
                np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32),
                np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], dtype=np.float32),
                np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32),
                np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], dtype=np.float32)
            ]
            return self._aplicar_mascara_maxima(kernels)
        elif metodo == 'frei_chen':
            sq2 = np.sqrt(2)
            kernels = [
                np.array([[1, sq2, 1], [0, 0, 0], [-1, -sq2, -1]], dtype=np.float32),
                np.array([[1, 0, -1], [sq2, 0, -sq2], [1, 0, -1]], dtype=np.float32),
                np.array([[0, -1, sq2], [1, 0, -1], [-sq2, 1, 0]], dtype=np.float32),
                np.array([[sq2, -1, 0], [-1, 0, 1], [0, 1, -sq2]], dtype=np.float32)
            ]
            return self._aplicar_mascara_maxima(kernels)
        elif metodo == 'laplaciano_h1':
            kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel)
        elif metodo == 'laplaciano_h2':
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
            return self._aplicar_mascara_simples(kernel)
        else:
            raise ValueError("Método de borda não reconhecido.")

    def _aplicar_mascara_simples(self, kernel):
        R = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel)

        R_abs = np.abs(R)

        resultado = cv2.normalize(R_abs, None, 0, 255, cv2.NORM_MINMAX)

        return resultado.astype(np.uint8)

    def _aplicar_gradiente_xy(self, kernel_x, kernel_y):
        Gx = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel_x)
        Gy = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel_y)

        magnitude = cv2.magnitude(Gx, Gy)

        resultado = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        return resultado.astype(np.uint8)

    def _aplicar_mascara_maxima(self, kernels):
        max_response = np.zeros_like(self.image_gray, dtype=np.float64)

        for kernel in kernels:
            R = cv2.filter2D(self.image_gray, cv2.CV_64F, kernel)
            R_abs = np.abs(R)

            max_response = np.maximum(max_response, R_abs)

        resultado = cv2.normalize(max_response, None, 0, 255, cv2.NORM_MINMAX)
        return resultado.astype(np.uint8)

    def limiarizacao_global(self):
        img_float = self.image_gray.astype(np.float32)

        T = np.mean(img_float)

        while True:
            R1 = img_float[img_float <= T]  # Fundo
            R2 = img_float[img_float > T]   # Objeto

            mu1 = np.mean(R1) if len(R1) > 0 else 0
            mu2 = np.mean(R2) if len(R2) > 0 else 0

            novo_T = (mu1 + mu2) / 2.0

            if abs(T - novo_T) < 1e-4:
                break

            T = novo_T

        _, resultado = cv2.threshold(self.image_gray, int(T), 255, cv2.THRESH_BINARY)
        return resultado.astype(np.uint8)

    def limiarizacao_local(self, metodo, n, k=None, C=10):
        if n % 2 == 0:
            n += 1

        altura, largura = self.image_gray.shape
        resultado = np.zeros((altura, largura), dtype=np.uint8)

        pad = n // 2

        img_padded = np.pad(self.image_gray.astype(np.float32), pad, mode='reflect')

        for i in range(altura):
            for j in range(largura):

                vizinhanca = img_padded[i : i + n, j : j + n]
                pixel_atual = self.image_gray[i, j]

                if metodo == 'media':
                    T = np.mean(vizinhanca) - C

                elif metodo == 'minimo':
                    T = np.min(vizinhanca) + C

                elif metodo == 'maximo':
                    T = np.max(vizinhanca) - C

                elif metodo == 'niblack':
                    if k is None:
                        raise ValueError("O parâmetro 'k' precisa ser informado para Niblack.")

                    mu = np.mean(vizinhanca)
                    sigma = np.std(vizinhanca) # Desvio padrão manual da matriz nxn
                    T = mu + k * sigma
                else:
                    raise ValueError("Método inválido.")

                if pixel_atual > T:
                    resultado[i, j] = 255

        return resultado

if __name__ == "__main__":
    janela = tk.Tk()
    app = ImageOperationGUI(janela)
    app.run()

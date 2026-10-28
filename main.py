from typing import Literal
from ollama import Client, ResponseError
import cv2
import time
from pydantic import BaseModel
from animations.spinner import Carregando
import customtkinter as ctk

#Mapeamento numeros arduino:
# 1 = não reciclavel
# 2 = plástico / isopor
# 3 = papel
# 4 = vidro
# 5 = metal
# 6 = orgânico
# 7 = madeira
# 0 = erro


PORTA_SERIAL = ""
BAUD_RATE = 9600

CAMERA_INDEX = 0
FOTO_ALTURA = 340
FOTO_LARGURA = 340
CAMINHO_FOTO = "lixotriagem.jpg"


MODELO_LOCAL = "qwen2.5vl:3b"

client = Client(host="http://localhost:11434")

class ClassificacaoTemplate(BaseModel):
    objectshown: str
    material: Literal["plastic", "paper", "cardboard", "glass", "metal", "organic", "wood", "fabric", "other", "food", "mixed"]
    color: Literal["transparent", "white", "black", "gray", "red", "orange" , "yellow", "green", "blue", "purple", "pink", "brown", "multicolor"]
    state: Literal["clean", "dirty", "wet"]


# App pra mostrar os resultados (Colocar em monitor separado na UFU)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Classificação de Lixo")
        self.geometry("900x600")

        ctk.set_appearance_mode("light")
        
        self.textoresultado = ctk.CTkLabel(self, text="Resultado aqui!", font=("Arial", 30, "bold"), text_color="black")
        self.textoresultado.grid(row=1, column=2, padx=10, pady=10)
        
        self.quadradoclassificacao = ctk.CTkLabel(self, width=80, height=80, fg_color="black", text_color="white", corner_radius=10, font=("Arial", 40, "bold"))
        self.quadradoclassificacao.grid(row=1, column=1, padx=10, pady=10)
        
        self.textotempo = ctk.CTkLabel(self, text="Tempo de classificação: 0s", font=("Arial", 20, "bold"), text_color="black")
        self.textotempo.grid(row=2, column=2, padx=10, pady=5)


def tirarfoto():
    cam = cv2.VideoCapture(CAMERA_INDEX)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FOTO_ALTURA)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, FOTO_LARGURA)

    for i in range(5):
        cam.read()
    ok, frame = cam.read()
    cam.release()

    if not ok:
        raise RuntimeError("Não deu pra tirar foto nessa webcam!")
        
    cv2.imwrite(CAMINHO_FOTO, frame)
    return CAMINHO_FOTO

def warmup():
    with Carregando(f'Carregando a IA {MODELO_LOCAL} na memória ram (warmup)'):
        try:
            client.chat(
                model=MODELO_LOCAL,
                messages=[{"role": "user", "content": "Ready for the Iniciacao Cientifica?"}]
                options={"temperature": 0},
                keep_alive= -1)
            print(f"{MODELO_LOCAL} pronto para uso! Apenas aperte o botão.")
        except ResponseError as e:
            print(f"Erro no lado do Ollama: {e.error}")
        except Exception as e:
            print(f"Erro ao carregar a IA! {e}. Confira o ollama!")

def codigo(json):
    
    #caso 1: plastico

    if json['material'] == "plastic" and json['state'] != "dirty":
        return "2"

    #caso 2: papel / papelão
    elif json['material'] in ("paper", "cardboard") and json['state'] == "clean":
        return "3"  
    # caso 4: vidro
    elif json['material'] == "glass":
        return "4"
    # caso 5: metal
    elif json['material'] == "metal":
        return "5"
    # caso 6: orgânico
    elif json['material'] in ("organic", "food"):
        return "6"
    # caso 7: madeira
    elif json['material'] == "wood":
        return "7"
    else:
        return "1"  

def classificar(foto):


    with Carregando(f"{MODELO_LOCAL} está analisando a foto..."):
        try:
            inicio = time.time()

            resp = client.chat(
                model=MODELO_LOCAL,
                messages=[{
                    "role": "user",
                    "content" : "Describe the waste item in the image. Fill every field of the JSON.",
                    "images": [foto],
                    
                }],
                format = ClassificacaoTemplate.model_json_schema(),
                options = {"temperature": 0},
                keep_alive = -1)
            time = time.time() - inicio

            resultadoformatado = codigo(ClassificacaoTemplate.model_validate_json(resp.message.content).model_dump())
            return resultadoformatado
        except Exception as e: 
            print(f"Erro: {e}")
            return "0"
        

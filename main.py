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
        
        
        self.textoresultado = ctk.CTkLabel(self, text="Resultado aqui!", font=("Arial", 110, "bold"), text_color="black")
        self.textoresultado.grid(row=1, column=2, padx=10, pady=10)
        
        self.quadradoclassificacao = ctk.CTkLabel(self, width=290, height=290, fg_color="black", text_color="white", corner_radius=10, font=("Arial", 32, "bold"), text="?")
        self.quadradoclassificacao.grid(row=1, column=1, padx=10, pady=10, rowspan=2)
        
        self.textotempo = ctk.CTkLabel(self, text="Tempo de classificação: 0s", font=("Arial", 70, "bold"), text_color="black")
        self.textotempo.grid(row=2, column=2, padx=10, pady=3)
        
    def atualizar(self,classe,tempo = 0):
        corclasses = {
            "1": "red",
            "2": "blue",
            "3": "gray",
            "4": "green",
            "5": "yellow",
            "6": "brown",
            "7": "orange",
            "0": "black",
            "10": "gray"
        }
        textoclasses = {
            "1": "Não reciclável",
            "2": "Plástico / Isopor",
            "3": "Papel",
            "4": "Vidro",
            "5": "Metal",
            "6": "Orgânico",
            "7": "Madeira",
            "0": "Erro",
            "10": "Processando"
        }
        self.quadradoclassificacao.configure(text=classe, fg_color=corclasses.get(classe, "black"))
        self.textotempo.configure(text=f"Tempo de classificação: {tempo:.2f}s")
        self.textoresultado.configure(text=textoclasses.get(classe, "Erro"), text_color=corclasses.get(classe, "black"))
        

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
                messages=[{"role": "user", "content": "Ready for the Iniciacao Cientifica?"}],
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
        classe = "3"  
    # caso 4: vidro
    elif json['material'] == "glass":
        classe = "4"
    # caso 5: metal
    elif json['material'] == "metal":
        classe = "5"
    # caso 6: orgânico
    elif json['material'] in ("organic", "food"):
        classe = "6"
    # caso 7: madeira
    elif json['material'] == "wood":
        classe = "7"
    else:
        classe = "1"

    return classe

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
            timee = time.time() - inicio

            resultadoformatado = codigo(ClassificacaoTemplate.model_validate_json(resp.message.content).model_dump())
            app.after(1, lambda: app.atualizar(resultadoformatado, timee))
            return resultadoformatado

        except Exception as e: 
            print(f"Erro: {e}")
            return "0"
        



def main():
    warmup()
    print(f"Conectando na porta serial {PORTA_SERIAL}...")
    try:
        arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)  # Aguarda a conexão com o Arduino
        print("Conectado ao seu arduino! Pode apertar o botão")
    except Exception as e:
        print(f"Erro ao conectar na porta serial: {e}")
        return
    
    
    try:
        while True:
            if arduino.in_waiting > 0:
                linha = (arduino.readline().decode("utf-8").strip())
                
                if linha == "CAPTURE"
                print("Botão apertado! Tirando foto...")
                app.after(0, lambda: app.atualizar("10", 0)) 
                try:
                    foto = tirarfoto()
                    print("Foto tirada! Classificando...")
                    codigo = classificar(foto)
                    print(f"Codigo:: {codigo}")

                except Exception as e:
                    print(f"Erro ao tirar foto ou classificar: {e}")
                    codigo = "0"
                arduino.write(f"{codigo}\n".encode("utf-8"))
                
        time.sleep(0.05)
        
        
app = App()

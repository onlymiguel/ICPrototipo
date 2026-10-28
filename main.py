from typing import Literal
from ollama import chat 
from pydantic import BaseModel
from animations.spinner import Carregando


#Mapeamento numeros arduino:
# 1 = não reciclavel
# 2 = plástico / isopor
# 3 = papel
# 4 = vidro
# 5 = orgânico
# 6 = madeira
# 

PORTA_SERIAL = ""
BAUD_RATE = 9600

CAMERA_INDEX = 0
FOTO_ALTURA = 340
FOTO_LARGURA = 340
CAMINHO_FOTO = "lixotriagem.jpg"


MODELO_LOCAL = "qwen2.5v1:3b"

client = Client(host="http://localhost:11434")

class ClassificacaoTemplate(BaseModel):
    objectshown: str
    material: Literal["plastic", "paper", "cardboard", "glass", "metal", "organic", "wood", "fabric", "other", "food", "mixed"]
    color: Literal["transparent", "white", "black", "gray", "red", "orange" , "yellow", "green", "blue", "purple", "pink", "brown", "multicolor"]
    state: Literal["clean", "dirty", "wet"]

def tirarfoto():
    cam = cv2.VideoCapture(CAMERA_INDEX)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FOTO_ALTURA)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, FOTO_LARGURA)

    for i in range(5):
        cam.read()
    ok, frame = cam.read()
    cam.release()

    if not ok:
        raise RuntimeError("Não deu pra tirar foto nessa webcam!"
        
    cv2.imwrite(CAMINHO_FOTO, frame))
    return CAMINHO_FOTO

def warmup():
    with Carregando(f'Carregando a IA {MODELO_LOCAL} na memória ram (warmup)')
        try:
            client.chat(
                model=MODELO_LOCAL
                messages=[{"role": "user", "content": "Ready for the Iniciacao Cientifica?"}]
                options={"temperature": 0}
                keep_alive= -1

            )
            print(f"{MODELO_LOCAL} pronto para uso! Apenas aperte o botão.")
        except ResponseError as e:
            print(f"Erro no lado do Ollama: {e.error}")
        except Exception as e:
            print(f"Erro ao carregar a IA! {e}. Confira o ollama!")

def codigo(json):
    
    if json['material'] == "plastic"    
    


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
                format = ClassificacaoTemplate.model_json.schema(),
                options = {"temperature": 0}
                keep_alive = -1
            )
            resultadoformatado = codigo(ClassificacaoTemplate.model_validate_json(resp.message.content).model_dump())
        except Exception as e: 
            print(f"Erro: {e}")
            return "0"
        
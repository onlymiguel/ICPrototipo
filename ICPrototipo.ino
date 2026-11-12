const int BOTAO_PIN = 2;

const int VERMELHO = 8;
const int AZUL = 6;
const int VERDE = 7;


const unsigned long DEBOUNCE_MS = 300;
const unsigned long LED_ON_TIME_MS = 20000;


unsigned long ultimaPressao = 0;
unsigned long ledOnTimestamp = 0;
bool esperandoResposta = false;
bool ledAtivo = false;

void setup() {
    Serial.begin(9600);
    pinMode(BOTAO_PIN, INPUT_PULLUP);
    pinMode(VERMELHO, OUTPUT);
    pinMode(AZUL, OUTPUT);
    pinMode(VERDE, OUTPUT);
    setCor(0,0,0);
}

void loop() {
    // 1) Botão
    if (digitalRead(BOTAO_PIN) == LOW) {
        unsigned long agora = millis();
        if (agora - ultimaPressao > DEBOUNCE_MS && !esperandoResposta && !ledAtivo) {
            ultimaPressao = agora;
            esperandoResposta = true;
            setCor(0,0,0);
            Serial.println("CAPTURE");
        }
    }

    // 2) Resposta do Python
    if (Serial.available() > 0) {
        String resposta = Serial.readStringUntil('\n');
        resposta.trim();
        if (resposta.length() > 0) {
            esperandoResposta = false;
            acenderLed(resposta.charAt(0));
        }
    }

    // 3) Apaga os LEDs depois do tempo
    if (ledAtivo && millis() - ledOnTimestamp >= LED_ON_TIME_MS) {
        setCor(0,0,0);
        ledAtivo = false;
    }
}


void setCor(int r, int g, int b) {
    analogWrite(VERMELHO, 255 - r);
    analogWrite(VERDE, 255 - g);
    analogWrite(AZUL, 255- b);
}
void acenderLed(char classe) {
    setCor(0,0,0);

    switch (classe) {
        case '1': setCor(255,0,0);      break;
        case '2': setCor(0,0,255);      break;
        case '3': setCor(255,255,255);  break;
        case '4': setCor(0,255,0);      break;
        case '5': setCor(255,255,0);    break;
        case '6': setCor(255,0,255);    break;
        case '7': setCor(255,0,255);    break;
        case '0':
        default: 

            break;
    }

    ledAtivo = true;
    ledOnTimestamp = millis();

}


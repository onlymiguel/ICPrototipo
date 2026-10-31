const int BOTAO_PIN = 2;

const int LED_NAORECICLAVEL_PIN = 3;
const int LED_PLASTICO_PIN = 4;
const int LED_PAPEL_PIN = 5;
const int LED_METAL_PIN = 6;
const int LED_VIDRO_PIN = 7;
const int LED_ORGANICO_PIN = 8;
const int SPEAKER_PIN = 9;

const unsigned long DEBOUNCE_MS = 300;
const unsigned long LED_ON_TIME_MS = 20000;
const unsigned int  BEEP_FREQ_HZ = 550;
const unsigned long BEEP_DURATION_MS = 4000;

unsigned long ultimaPressao = 0;
unsigned long ledOnTimestamp = 0;
bool esperandoResposta = false;
bool ledAtivo = false;

void setup() {
    Serial.begin(9600);
    pinMode(BOTAO_PIN, INPUT_PULLUP);
    pinMode(LED_NAORECICLAVEL_PIN, OUTPUT);
    pinMode(LED_PLASTICO_PIN, OUTPUT);
    pinMode(LED_PAPEL_PIN, OUTPUT);
    pinMode(LED_METAL_PIN, OUTPUT);
    pinMode(LED_VIDRO_PIN, OUTPUT);
    pinMode(LED_ORGANICO_PIN, OUTPUT);
    pinMode(SPEAKER_PIN, OUTPUT);
    apagarTodosLeds();
}

void loop() {

    // Aqui ele pega o sinal do botão
    if (digitalRead(BOTAO_PIN) == LOW) {
        unsigned long agora = millis();
        if (agora - ultimaPressao > DEBOUNCE_MS && !esperandoResposta && !ledAtivo) {
        ultimaPressao = agora;
        esperandoResposta = true;
        apagarTodosLeds();
        Serial.println("CAPTURE");
    }
    if (Serial.available() > 0) {
        String resposta = Serial.readStringUntil('\n');
        resposta.trim();

        if (resposta.length() > 0) {
            char classe = resposta.charAt(0);
            esperandoResposta = false;
            acenderLed(classe);
        }
    }
    if (ledAtivo && millis() - ledOnTimestamp >= LED_ON_TIME_MS) {
        apagarTodosLeds();
        ledAtivo = false;
    }
}

void acenderLed(char classe) {
    apagarTodosLeds();

    switch (classe) {
        case '1':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_NAORECICLAVEL_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '2':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_PLASTICO_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '3':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_PAPEL_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '4':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_METAL_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '5':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_VIDRO_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '6':
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            digitalWrite(LED_ORGANICO_PIN, HIGH);
            ledAtivo = true;
            ledOnTimestamp = millis();
            break;
        case '0':
        default:
                        digitalWrite(LED_NAORECICLAVEL_PIN, HIGH);
            digitalWrite(LED_PLASTICO_PIN, HIGH);
            digitalWrite(LED_PAPEL_PIN, HIGH);
            digitalWrite(LED_METAL_PIN, HIGH);
            digitalWrite(LED_VIDRO_PIN, HIGH);
            digitalWrite(LED_ORGANICO_PIN, HIGH);
            tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
            ledAtivo = true;
            ledOnTimestamp = millis();
    }

    ledOnTimestamp = millis();
    ledAtivo = true;

    // Emite o beep
    tone(SPEAKER_PIN, BEEP_FREQ_HZ, BEEP_DURATION_MS);
}

void apagarTodosLeds() {
    digitalWrite(LED_NAORECICLAVEL_PIN, LOW);
    digitalWrite(LED_PLASTICO_PIN, LOW);
    digitalWrite(LED_PAPEL_PIN, LOW);
    digitalWrite(LED_METAL_PIN, LOW);
    digitalWrite(LED_VIDRO_PIN, LOW);
    digitalWrite(LED_ORGANICO_PIN, LOW);
}

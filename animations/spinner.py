import sys
import time
import itertools
import threading


# _ : nao pode mexer de fora
class Carregando:
    def __init__(self, mensagem="Carregando...", pararem=None):
        self.mensagem = mensagem
        self.parar_em = pararem

        self._parar = threading.Event()
        self._lock = threading.Lock()
        self._original = sys.stdout
        self._thread = threading.Thread(target=self._animar, daemon=True)

    def _animar(self):
        for simbolo in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
            if self._parar.is_set():
                break
            with self._lock:
                self._original.write(f"\r{self.mensagem} {simbolo}")
                self._original.flush()
            time.sleep(0.1)
    def _limpar_linha(self):
        self._original.write("\r" + " " * (len(self.mensagem) + 4) + "\r")
    def _encerrar(self):
        if not self._parar.is_set():
            self._parar.set()
            self._thread.join()
            with self._lock:
                self._limpar_linha()
    def write(self, texto):
        if texto.strip() and not self._parar.is_set():
            if self.parar_em is None or self.parar_em in texto:
                self._encerrar()
        with self._lock:
            if not self._parar.is_set():
                self._limpar_linha()
            self._original.write(texto)
    def flush(self):
        self._original.flush()

    def __enter__(self):
        sys.stdout = self
        self._thread.start()
        return self
    def __exit__(self, *args):
        self._encerrar()
        sys.stdout = self._original
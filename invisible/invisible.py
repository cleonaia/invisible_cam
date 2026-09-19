import cv2
import numpy as np
from utils import DetectorPersona, ClasificadorEstadoMano, EstadoPermanencia


class Invisible:
    def __init__(self, imagen_fondo=None, tiempo_registro=0.2, fps=30):
        self.detector_persona = DetectorPersona()
        self.clasificador_mano = ClasificadorEstadoMano()
        self.imagen_fondo = None
        self.estado = EstadoPermanencia(tiempo_registro, fps, estado_inicial=False)
        self.caja_suavizada = None
        self.cajas_sin_actualizar = 0
        if imagen_fondo is not None:
            self.cargar_fondo(imagen_fondo)

    def cargar_fondo(self, imagen_fondo):
        self.imagen_fondo = imagen_fondo

    def _suavizar_caja(self, caja, factor=0.8):
        if self.caja_suavizada is None:
            self.caja_suavizada = tuple(int(valor) for valor in caja)
            return self.caja_suavizada

        valores_previos = self.caja_suavizada
        valores_nuevos = tuple(int(valor) for valor in caja)
        self.caja_suavizada = tuple(
            int(round(valor_previo * factor + valor_nuevo * (1 - factor)))
            for valor_previo, valor_nuevo in zip(valores_previos, valores_nuevos)
        )
        return self.caja_suavizada

    def aplicar_invisible(self, frame, dibujar_caja=False):
        if self.imagen_fondo is None:
            raise ValueError("La imagen de fondo no está configurada. Usa cargar_fondo() para establecerla.")

        mano_cerrada, caja_mano = self.clasificador_mano.mano_cerrada_y_caja(frame)
        if mano_cerrada is None or caja_mano is None:
            self.caja_suavizada = None
            self.cajas_sin_actualizar = 0
            return frame

        mano_cerrada = self.estado.actualizar(mano_cerrada)

        if not mano_cerrada:
            self.caja_suavizada = None
            self.cajas_sin_actualizar = 0
            return frame

        self.cajas_sin_actualizar = 0
        centro_mano = (caja_mano[0] + caja_mano[2] // 2, caja_mano[1] + caja_mano[3] // 2)
        caja = self.detector_persona.detectar_caja(frame, punto_objetivo=centro_mano)
        if caja is None:
            if self.caja_suavizada is None:
                return frame
            self.cajas_sin_actualizar += 1
            if self.cajas_sin_actualizar > 2:
                self.caja_suavizada = None
                self.cajas_sin_actualizar = 0
                return frame
            caja = self.caja_suavizada
        else:
            caja = self._suavizar_caja(caja)

        if caja is None:
            return frame

        if dibujar_caja:
            frame = self.detector_persona.dibujar_caja(frame, caja)

        x, y, w, h = caja
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(frame.shape[1], x + w)
        y1 = min(frame.shape[0], y + h)

        if x1 <= x0 or y1 <= y0:
            return frame

        fondo_region = self.imagen_fondo[y0:y1, x0:x1]
        if fondo_region.shape[:2] != (y1 - y0, x1 - x0):
            fondo_region = cv2.resize(
                self.imagen_fondo,
                (x1 - x0, y1 - y0),
                interpolation=cv2.INTER_LINEAR,
            )

        frame[y0:y1, x0:x1] = fondo_region
        return frame


__all__ = ["Invisible"]


if __name__ == "__main__":
    import time

    fps = 30
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    efecto = Invisible(fps=fps)
    ret = False
    while not ret:
        print("No se pudo capturar la cámara. Se volverá a intentar en 100 ms")
        time.sleep(0.1)
        ret, _ = cap.read()
    for _ in range(60):
        ret, fondo = cap.read()
    cv2.imwrite("invisible.jpg", fondo)
    efecto.cargar_fondo(fondo)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        salida = efecto.aplicar_invisible(frame)
        cv2.imshow("Invisible", salida)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(1 / fps)

    cap.release()
    cv2.destroyAllWindows()

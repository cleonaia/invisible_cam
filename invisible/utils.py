from typing import Optional, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class EstadoPermanencia:
    def __init__(self, tiempo_mantenimiento, fps=1, estado_inicial=False):
        self.tiempo_mantenimiento = max(1, int(tiempo_mantenimiento * fps))
        self.i = self.tiempo_mantenimiento
        self.estado = estado_inicial

    def actualizar(self, estado):
        if estado == self.estado:
            self.i += 1
            if self.i > self.tiempo_mantenimiento:
                self.i = self.tiempo_mantenimiento
            return self.estado
        self.i -= 1
        if self.i < 0:
            self.i = self.tiempo_mantenimiento
            self.estado = estado
        return self.estado


class DetectorPersona:
    def __init__(
        self,
        ruta_modelo: str = "efficientdet_lite0.tflite",
        umbral_puntuacion: float = 0.25,
        factor_escalado: float = 2.0,
    ) -> None:
        self.factor_escalado = max(1.0, factor_escalado)
        opciones = vision.ObjectDetectorOptions(
            base_options=python.BaseOptions(model_asset_path=ruta_modelo),
            score_threshold=umbral_puntuacion,
            running_mode=vision.RunningMode.IMAGE,
            category_allowlist=["person"],
        )
        self._detector = vision.ObjectDetector.create_from_options(opciones)

    @staticmethod
    def _mejorar_imagen(frame_rgb):
        lab = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.equalizeHist(l)
        lab = cv2.merge((l, a, b))
        frame_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return cv2.GaussianBlur(frame_rgb, (3, 3), 0)

    def detectar_caja(self, frame, padding=24, punto_objetivo: Optional[Tuple[int, int]] = None):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = self._mejorar_imagen(frame_rgb)
        altura, ancho, _ = frame_rgb.shape
        factor = self.factor_escalado
        if factor > 1.0:
            frame_rgb = cv2.resize(
                frame_rgb,
                (int(ancho * factor), int(altura * factor)),
                interpolation=cv2.INTER_CUBIC,
            )

        imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultado = self._detector.detect(imagen_mp)
        if not resultado.detections:
            return None

        candidatos = []
        for deteccion in resultado.detections:
            b = deteccion.bounding_box
            x = int(b.origin_x / factor)
            y = int(b.origin_y / factor)
            w = int(b.width / factor)
            h = int(b.height / factor)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(ancho - x, w + padding * 2)
            h = min(altura - y, h + padding * 2)
            candidatos.append((x, y, w, h))

        if not candidatos:
            return None

        if punto_objetivo is not None:
            px, py = punto_objetivo
            candidatos_con_punto = [
                caja
                for caja in candidatos
                if caja[0] <= px <= caja[0] + caja[2] and caja[1] <= py <= caja[1] + caja[3]
            ]
            if candidatos_con_punto:
                caja = min(candidatos_con_punto, key=lambda item: item[2] * item[3])
            else:
                caja = min(
                    candidatos,
                    key=lambda item: ((item[0] + item[2] / 2) - px) ** 2 + ((item[1] + item[3] / 2) - py) ** 2,
                )
        else:
            caja = max(candidatos, key=lambda item: item[2] * item[3])

        x, y, w, h = caja
        margen_x = max(8, int(w * 0.08))
        margen_y = max(10, int(h * 0.12))
        x = max(0, x - margen_x)
        y = max(0, y - margen_y)
        w = min(ancho - x, w + margen_x * 2)
        h = min(altura - y, h + margen_y * 2)
        return (x, y, w, h)

    def dibujar_caja(self, frame, caja: Tuple[int, int, int, int], color: Tuple[int, int, int] = (0, 255, 0), grosor: int = 2):
        x, y, w, h = caja
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, grosor)
        return frame


class ClasificadorEstadoMano:
    def __init__(
        self,
        ruta_modelo: str = "hand_landmarker.task",
        confianza_deteccion: float = 0.2,
        confianza_seguimiento: float = 0.2,
        factor_escalado: float = 2.0,
    ) -> None:
        self.factor_escalado = max(1.0, factor_escalado)
        opciones_base = python.BaseOptions(model_asset_path=ruta_modelo)
        opciones = vision.HandLandmarkerOptions(
            base_options=opciones_base,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=confianza_deteccion,
            min_tracking_confidence=confianza_seguimiento,
        )
        self._detector = vision.HandLandmarker.create_from_options(opciones)

    @staticmethod
    def _mejorar_imagen(frame_rgb):
        lab = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        frame_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return cv2.GaussianBlur(frame_rgb, (3, 3), 0)

    def _caja_mano(self, puntos_mano, ancho: int, alto: int) -> Tuple[int, int, int, int]:
        xs = [punto.x * ancho for punto in puntos_mano]
        ys = [punto.y * alto for punto in puntos_mano]
        x0 = max(0, int(min(xs)))
        y0 = max(0, int(min(ys)))
        x1 = min(ancho, int(max(xs)))
        y1 = min(alto, int(max(ys)))
        return (x0, y0, max(1, x1 - x0), max(1, y1 - y0))

    def _es_puno(self, puntos_mano) -> bool:
        muneca = puntos_mano[0]
        dedos_cerrados = 0
        comparaciones = [
            (4, 3),
            (8, 6),
            (12, 10),
            (16, 14),
            (20, 18),
        ]

        for punta, intermedia in comparaciones:
            distancia_punta = self._distancia(puntos_mano[punta], muneca)
            distancia_intermedia = self._distancia(puntos_mano[intermedia], muneca)
            if distancia_punta <= distancia_intermedia * 1.02:
                dedos_cerrados += 1

        return dedos_cerrados >= 4

    def _analizar_manos(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = self._mejorar_imagen(frame_rgb)
        altura, ancho, _ = frame_rgb.shape
        factor = self.factor_escalado
        if factor > 1.0:
            frame_rgb = cv2.resize(
                frame_rgb,
                (int(ancho * factor), int(altura * factor)),
                interpolation=cv2.INTER_CUBIC,
            )

        imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultado = self._detector.detect(imagen_mp)
        if not resultado.hand_landmarks:
            return []

        manos = []
        for puntos_mano in resultado.hand_landmarks:
            caja = self._caja_mano(puntos_mano, ancho, altura)
            manos.append((self._es_puno(puntos_mano), caja))

        return manos

    def mano_cerrada(self, frame):
        manos = self._analizar_manos(frame)
        if not manos:
            return None
        return any(es_puno for es_puno, _ in manos)

    def mano_cerrada_y_caja(self, frame):
        manos = self._analizar_manos(frame)
        if not manos:
            return None, None

        manos_puno = [item for item in manos if item[0]]
        if manos_puno:
            manos_puno.sort(key=lambda item: item[1][2] * item[1][3])
            return manos_puno[0]

        manos.sort(key=lambda item: item[1][2] * item[1][3])
        return manos[0]

    @staticmethod
    def _distancia(punto_a, punto_b) -> float:
        dx = punto_a.x - punto_b.x
        dy = punto_a.y - punto_b.y
        return (dx * dx + dy * dy) ** 0.5


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    detector = DetectorPersona()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        caja = detector.detectar_caja(frame)
        if caja is not None:
            frame = detector.dibujar_caja(frame, caja)
        cv2.imshow("Invisible", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

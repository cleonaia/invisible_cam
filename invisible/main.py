import tkinter as tk
from tkinter import ttk, messagebox
import time
import cv2
from invisible import Invisible


archivo_fondo = "invisible.jpg"
tiempo_cuenta_atras = 5
ancho_camara = 1280
alto_camara = 720


class AplicacionInvisible:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Invisible")
        self.root.geometry("640x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#edf2f7")

        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("Panel.TFrame", background="#edf2f7")
        estilo.configure(
            "Titulo.TLabel",
            background="#edf2f7",
            foreground="#111827",
            font=("Segoe UI", 24, "bold"),
        )
        estilo.configure(
            "Texto.TLabel",
            background="#edf2f7",
            foreground="#374151",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Estado.TLabel",
            background="#ffffff",
            foreground="#1f2937",
            font=("Segoe UI", 10),
            padding=12,
        )
        estilo.configure(
            "Accent.TButton",
            background="#1f6feb",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10),
        )
        estilo.map(
            "Accent.TButton",
            background=[("active", "#185ac9"), ("pressed", "#164fb5")],
            foreground=[("active", "#ffffff")],
        )
        estilo.configure(
            "Secondary.TButton",
            background="#e5e7eb",
            foreground="#111827",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10),
        )
        estilo.map(
            "Secondary.TButton",
            background=[("active", "#d1d5db"), ("pressed", "#c4c9d2")],
            foreground=[("active", "#111827")],
        )
        estilo.configure(
            "Check.TCheckbutton",
            background="#edf2f7",
            foreground="#1f2937",
            font=("Segoe UI", 10),
        )

        self.estado_var = tk.StringVar(
            value="Limpia la escena y luego captura una imagen de fondo desde la vista previa en vivo."
        )
        self.imagen_fondo = None
        self.dibujar_caja_var = tk.BooleanVar(value=True)

        contenedor = ttk.Frame(self.root, padding=22, style="Panel.TFrame")
        contenedor.pack(fill="both", expand=True)

        titulo = ttk.Label(contenedor, text="Invisible", style="Titulo.TLabel")
        titulo.pack(anchor="w")

        instrucciones = ttk.Label(
            contenedor,
            text=(
                "Paso 1: limpia la escena y asegúrate de que nadie sea visible. "
                "Paso 2: haz clic en Capturar fondo, observa la vista previa en vivo y usa la cuenta regresiva para salir del encuadre. "
                "Paso 3: cuando se capture el fondo, inicia el efecto y alza el puño para activar la invisibilidad."
            ),
            wraplength=560,
            justify="left",
            style="Texto.TLabel",
        )
        instrucciones.pack(anchor="w", pady=(10, 14))

        fila_botones = ttk.Frame(contenedor, style="Panel.TFrame")
        fila_botones.pack(anchor="w", pady=(0, 12))

        self.boton_capturar = ttk.Button(
            fila_botones,
            text="Capturar fondo",
            command=self.capturar_fondo,
            style="Accent.TButton",
        )
        self.boton_capturar.pack(side="left")

        self.boton_iniciar = ttk.Button(
            fila_botones,
            text="Iniciar aplicación",
            command=self.iniciar_aplicacion,
            state="disabled",
            style="Secondary.TButton",
        )
        self.boton_iniciar.pack(side="left", padx=(12, 0))

        self.checkbox_caja = ttk.Checkbutton(
            contenedor,
            text="Dibujar rectángulo de la persona",
            variable=self.dibujar_caja_var,
            style="Check.TCheckbutton",
        )
        self.checkbox_caja.pack(anchor="w", pady=(0, 12))

        estado = ttk.Label(
            contenedor,
            textvariable=self.estado_var,
            wraplength=560,
            justify="left",
            style="Estado.TLabel",
        )
        estado.pack(anchor="w", fill="x")

    def capturar_fondo(self) -> None:
        self.estado_var.set(
            f"Abriendo vista previa de la cámara. Aléjate antes de que termine la cuenta regresiva de {tiempo_cuenta_atras} segundos."
        )
        self.root.update_idletasks()
        nombre_ventana = "Vista previa del fondo"

        captura = cv2.VideoCapture(0)
        if not captura.isOpened():
            messagebox.showerror("Error de cámara", "No se pudo abrir la cámara.")
            self.estado_var.set("La cámara no está disponible.")
            return

        captura.set(cv2.CAP_PROP_FRAME_WIDTH, ancho_camara)
        captura.set(cv2.CAP_PROP_FRAME_HEIGHT, alto_camara)

        frame = None
        tiempo_inicio = time.time()

        try:
            while True:
                ret, frame = captura.read()
                if not ret:
                    continue

                transcurrido = time.time() - tiempo_inicio
                restante = max(0, int(tiempo_cuenta_atras - transcurrido + 0.999))

                frame_previo = frame.copy()
                cv2.putText(
                    frame_previo,
                    f"Capturando en {restante}s",
                    (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.7,
                    (0, 0, 0),
                    3,
                    cv2.LINE_AA,
                )

                cv2.imshow(nombre_ventana, frame_previo)
                self.estado_var.set(
                    f"Vista previa en ejecución. La captura empieza en {restante} segundos."
                )
                self.root.update_idletasks()

                tecla = cv2.waitKey(1) & 0xFF
                if tecla in (27, ord("q")):
                    self.estado_var.set("Captura del fondo cancelada.")
                    return
                if cv2.getWindowProperty(nombre_ventana, cv2.WND_PROP_VISIBLE) < 1:
                    self.estado_var.set("Captura del fondo cancelada.")
                    return

                if transcurrido >= tiempo_cuenta_atras:
                    break

            if frame is None:
                messagebox.showerror(
                    "Error de captura", "No se pudo capturar una imagen de fondo."
                )
                self.estado_var.set("La captura falló.")
                return
        finally:
            captura.release()
            cv2.destroyWindow(nombre_ventana)

        if frame is None:
            messagebox.showerror("Error de captura", "No se pudo capturar una imagen de fondo.")
            self.estado_var.set("La captura falló.")
            return

        self.imagen_fondo = frame.copy()
        cv2.imwrite(archivo_fondo, self.imagen_fondo)
        fondo_cargado = cv2.imread(archivo_fondo)
        if fondo_cargado is not None:
            self.imagen_fondo = fondo_cargado

        self.estado_var.set(
            f"Fondo capturado desde la vista previa y guardado en {archivo_fondo}."
        )
        self.boton_iniciar.config(state="normal")

    def iniciar_aplicacion(self) -> None:
        if self.imagen_fondo is None:
            messagebox.showinfo("Falta el fondo", "Primero captura una imagen de fondo.")
            return

        self.root.withdraw()
        try:
            self.bucle_camara()
        finally:
            self.root.deiconify()

    def bucle_camara(self) -> None:
        detector = Invisible(imagen_fondo=self.imagen_fondo, fps=30)
        captura = cv2.VideoCapture(0)
        nombre_ventana = "Invisible"

        if not captura.isOpened():
            messagebox.showerror("Error de cámara", "No se pudo abrir la cámara.")
            return

        captura.set(cv2.CAP_PROP_FRAME_WIDTH, ancho_camara)
        captura.set(cv2.CAP_PROP_FRAME_HEIGHT, alto_camara)

        try:
            while True:
                ret, frame = captura.read()
                if not ret:
                    break

                salida = detector.aplicar_invisible(
                    frame,
                    dibujar_caja=self.dibujar_caja_var.get(),
                )
                cv2.imshow(nombre_ventana, salida)

                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord("q"):
                    break
                if cv2.getWindowProperty(nombre_ventana, cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            captura.release()
            cv2.destroyAllWindows()

    def ejecutar(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    AplicacionInvisible().ejecutar()
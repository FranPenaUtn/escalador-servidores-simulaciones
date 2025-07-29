import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

# --- Parámetros generales ---
dt = 0.5
cpu_target = 0.60
cooldown_steps = int(5 / dt)
pods_actuales = 2
ultimo_escaleo = -cooldown_steps
tiempo_actual = 0.0
ddos_activado = False
ruido_activado = True
min_pods = 2
max_pods = 10

# Historial
tiempos, uso_cpu, cantidad_pods, carga_registrada = [], [], [], []
errores, funcion_control = [], []

# --- Setup de gráficos ---
fig, axes = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
ax1, ax2, ax3, ax4, ax5 = axes
plt.subplots_adjust(bottom=0.4)

# CPU
line_cpu, = ax1.plot([], [], color='orange', label='CPU por pod (%)')
ax1.axhline(cpu_target * 100, color='r', linestyle='--', label='Objetivo CPU (60%)')
ax1.set_ylabel('CPU (%)'); ax1.set_ylim(0, 220)
ax1.legend(); ax1.grid(True)
text_cpu = ax1.text(-5, 0, '', fontsize=8, va='center', color='black')

# Pods
line_pods, = ax2.plot([], [], color='green', label='Pods activos')
ax2.set_ylabel('Pods activos'); ax2.set_ylim(0, 12)
ax2.legend(); ax2.grid(True)
text_pods = ax2.text(-5, 0, '', fontsize=8, va='center', color='black')

# Carga
line_carga, = ax3.plot([], [], color='blue', label='Carga total')
ax3.set_ylabel('Carga total'); ax3.legend(); ax3.grid(True)

# Error
line_error, = ax4.plot([], [], color='red', label='Error (CPU_real - CPU_medida)')
ax4.set_ylabel('Error'); ax4.grid(True); ax4.legend()
text_error = ax4.text(-5, 0, '', fontsize=8, va='center', color='black')


# Función de control
line_control, = ax5.plot([], [], color='purple', label='f(t) = Kp * e(t)')
ax5.set_ylabel('F[kT] (CPU medida)'); ax5.set_xlabel('Tiempo (min)'); ax5.grid(True)
ax5.legend()
text_control = ax5.text(-5, 0, '', fontsize=8, va='center', color='black')

# Sliders
slider_carga = Slider(plt.axes([0.25, 0.27, 0.5, 0.03]), 'Carga', 0.0, 5.0, valinit=1, valstep=0.1)
slider_kp = Slider(plt.axes([0.25, 0.22, 0.5, 0.03]), 'Kp', 1, 10, valinit=4.0, valstep=0.5)

# Botones
def toggle_ddos(event):
    global ddos_activado
    ddos_activado = not ddos_activado
    btn_ddos.label.set_text('DDoS ON' if ddos_activado else 'Ataque DDoS')

def toggle_ruido(event):
    global ruido_activado
    ruido_activado = not ruido_activado
    btn_ruido.label.set_text('Ruido: ON' if ruido_activado else 'Ruido: OFF')

btn_ddos = Button(plt.axes([0.15, 0.05, 0.15, 0.04]), 'Ataque DDoS'); btn_ddos.on_clicked(toggle_ddos)
btn_ruido = Button(plt.axes([0.35, 0.05, 0.20, 0.04]), 'Ruido: ON'); btn_ruido.on_clicked(toggle_ruido)

# Update
def update(frame):
    global pods_actuales, ultimo_escaleo, tiempo_actual

    carga_total = 12.0 if ddos_activado else slider_carga.val
    if ruido_activado:
        carga_total += np.random.normal(0, 0.05)
    carga_total = min(carga_total, pods_actuales * 2.0)

    uso_actual = carga_total / pods_actuales
    error = uso_actual - cpu_target
    kp = slider_kp.val
    f_t = kp * error

    if len(tiempos) - ultimo_escaleo >= cooldown_steps:
        delta = int(np.round(f_t))
        deseadas = pods_actuales + delta
        deseadas = max(min_pods, min(max_pods, deseadas))
        if deseadas != pods_actuales:
            pods_actuales = deseadas
            ultimo_escaleo = len(tiempos)

    # Guardar datos
    tiempos.append(tiempo_actual)
    uso_cpu.append(uso_actual * 100)
    cantidad_pods.append(pods_actuales)
    carga_registrada.append(carga_total)
    errores.append(error)
    funcion_control.append(uso_actual)

    # Graficar
    line_cpu.set_data(tiempos, uso_cpu)
    line_pods.set_data(tiempos, cantidad_pods)
    line_carga.set_data(tiempos, carga_registrada)
    line_error.set_data(tiempos, errores)
    line_control.set_data(tiempos, funcion_control)

    text_cpu.set_text(f'CPU actual: {uso_actual * 100:.1f}%')
    text_cpu.set_position((tiempo_actual - 5, uso_actual * 100))
    text_pods.set_text(f'Pods activos: {pods_actuales}')
    text_pods.set_position((tiempo_actual - 5, pods_actuales))

    text_error.set_text(f'Error: {error:.3f}')
    text_error.set_position((tiempo_actual - 5, error))

    text_control.set_text(f'F[kT]: {uso_actual:.2f}')
    text_control.set_position((tiempo_actual - 5, uso_actual))

    for ax in [ax1, ax2, ax3, ax4, ax5]:
        ax.relim(); ax.autoscale_view()

    tiempo_actual += dt

# Animación
ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)

# Reset
def reset_simulacion(event):
    global pods_actuales, ultimo_escaleo, tiempo_actual
    global tiempos, uso_cpu, cantidad_pods, carga_registrada, errores, funcion_control
    global ddos_activado, ruido_activado

    pods_actuales = 2
    ultimo_escaleo = -cooldown_steps
    tiempo_actual = 0.0
    ddos_activado = False
    ruido_activado = True

    for arr in [tiempos, uso_cpu, cantidad_pods, carga_registrada, errores, funcion_control]:
        arr.clear()

    slider_carga.set_val(1)
    slider_kp.set_val(4.0)
    btn_ddos.label.set_text("Ataque DDoS")
    btn_ruido.label.set_text("Ruido: ON")

    for line in [line_cpu, line_pods, line_carga, line_error, line_control]:
        line.set_data([], [])

    text_cpu.set_text('')
    text_pods.set_text('')
    text_error.set_text('')
    text_control.set_text('')
    for ax in [ax1, ax2, ax3, ax4, ax5]:
        ax.relim(); ax.autoscale_view()

    fig.canvas.draw_idle()

btn_reset = Button(plt.axes([0.60, 0.05, 0.15, 0.04]), 'Resetear')
btn_reset.on_clicked(reset_simulacion)

# Ejecutar
plt.show()

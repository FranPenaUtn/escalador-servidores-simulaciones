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

# --- Setup de gráficos ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
plt.subplots_adjust(bottom=0.4)


# CPU
line_cpu, = ax1.plot([], [], color='orange', label='CPU por pod (%)')
ax1.axhline(cpu_target * 100, color='r', linestyle='--', label='Objetivo CPU (60%)')
ax1.axhline(100, color='b', linestyle='--', label='Banda de error')
ax1.set_ylabel('CPU por pod (%)')
ax1.set_ylim(0, 220)
ax1.legend(); ax1.grid(True)
text_cpu = ax1.text(-5, 0, '', fontsize=8, va='center', color='black')

# Pods
line_pods, = ax2.plot([], [], color='green', label='Pods activos')
ax2.set_ylabel('Pods activos'); ax2.set_ylim(0, 12)
ax2.legend(); ax2.grid(True)
text_pods = ax2.text(-5, 0, '', fontsize=8, va='center', color='black')

# Carga
line_carga, = ax3.plot([], [], color='blue', label='Carga total')
ax3.set_ylabel('Carga total'); ax3.set_xlabel('Tiempo (min)')
ax3.legend(); ax3.grid(True)

# Sliders
slider_carga = Slider(plt.axes([0.25, 0.27, 0.5, 0.03]), 'Carga', 0.0, 5.0, valinit=0.5, valstep=0.1)
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

# Actualización
def update(frame):
    global pods_actuales, ultimo_escaleo, tiempo_actual

    carga_total = 12.0 if ddos_activado else slider_carga.val
    if ruido_activado:
        carga_total += np.random.normal(0, 0.05)
    carga_total = min(carga_total, pods_actuales * 2.0)

    uso_actual = carga_total / pods_actuales
    error = uso_actual - cpu_target
    kp = slider_kp.val

    if len(tiempos) - ultimo_escaleo >= cooldown_steps:
        delta =  int(np.round(kp * error)) if error < 0 else int(np.round(kp * error))
        deseadas = pods_actuales + delta
        deseadas = max(min_pods, min(max_pods, deseadas))
        if deseadas != pods_actuales:
            pods_actuales = deseadas
            ultimo_escaleo = len(tiempos)

    # Guardar
    tiempos.append(tiempo_actual)
    uso_cpu.append(uso_actual * 100)
    cantidad_pods.append(pods_actuales)
    carga_registrada.append(carga_total)

    # Graficar
    line_cpu.set_data(tiempos, uso_cpu)
    line_pods.set_data(tiempos, cantidad_pods)
    line_carga.set_data(tiempos, carga_registrada)

    text_cpu.set_text(f'CPU actual: {uso_actual * 100:.1f}% {error}')
    text_cpu.set_position((tiempo_actual - 5, uso_actual * 100))
    text_pods.set_text(f'Pods activos: {pods_actuales}')
    text_pods.set_position((tiempo_actual - 5, pods_actuales))

    ax1.relim(); ax1.autoscale_view()
    ax2.relim(); ax2.autoscale_view()
    ax3.relim(); ax3.autoscale_view()

    tiempo_actual += dt

# Ejecutar animación
ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)

def reset_simulacion(event):
    global pods_actuales, ultimo_escaleo, tiempo_actual
    global tiempos, uso_cpu, cantidad_pods, carga_registrada
    global ddos_activado, ruido_activado

    # Reset variables de estado
    pods_actuales = 2
    ultimo_escaleo = -cooldown_steps
    tiempo_actual = 0.0
    ddos_activado = False
    ruido_activado = True

    # Reset arrays
    tiempos.clear()
    uso_cpu.clear()
    cantidad_pods.clear()
    carga_registrada.clear()

    # Reset sliders
    slider_carga.set_val(0.5)
    slider_kp.set_val(10.0)

    # Reset etiquetas de botones
    btn_ddos.label.set_text("Ataque DDoS")
    btn_ruido.label.set_text("Ruido: ON")

    # Limpiar gráficos
    line_cpu.set_data([], [])
    line_pods.set_data([], [])
    line_carga.set_data([], [])
    text_cpu.set_text('')
    text_pods.set_text('')

    ax1.relim(); ax1.autoscale_view()
    ax2.relim(); ax2.autoscale_view()
    ax3.relim(); ax3.autoscale_view()
    fig.canvas.draw_idle()

# Crear botón de reset
btn_reset = Button(plt.axes([0.60, 0.05, 0.15, 0.04]), 'Resetear')
btn_reset.on_clicked(reset_simulacion)

# Mostrar simulación
plt.show()

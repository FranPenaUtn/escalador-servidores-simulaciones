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
simulacion_pausada = False

# Historial
tiempos, uso_cpu, cantidad_pods, carga_registrada = [], [], [], []
errores, senal_f = [], []

# --- Setup de gráficos ---
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 14), sharex=True)
plt.subplots_adjust(bottom=0.35)


# CPU
line_cpu, = ax1.plot([], [], color='orange', label='CPU por pod (%)')
target_line = ax1.axhline(60, color='r', linestyle='--', label='Objetivo CPU')
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
ax3.set_ylabel('Carga total')
ax3.legend(); ax3.grid(True)

# Error
line_error, = ax4.plot([], [], color='red', label='Error (e)')
ax4.set_ylabel('Error (e)')
ax4.legend(); ax4.grid(True)
text_error = ax4.text(-5, 0, '', fontsize=8, va='center', color='black')

# Señal f
line_f, = ax5.plot([], [], color='purple', label='Señal f')
ax5.set_ylabel('f'); ax5.set_xlabel('Tiempo (min)')
ax5.legend(); ax5.grid(True)
text_f = ax5.text(-5, 0, '', fontsize=8, va='center', color='black')

# Sliders
slider_carga = Slider(plt.axes([0.15, 0.25, 0.525, 0.03]), 'Carga', 0.0, 5.0, valinit=1, valstep=0.1)
slider_kp = Slider(plt.axes([0.15, 0.20, 0.525, 0.03]), 'Kp', 1, 10, valinit=4.0, valstep=0.5)
slider_cpu_target = Slider(plt.axes([0.15, 0.15, 0.525, 0.03]), 'CPU Target (%)', 0, 100, valinit=60, valstep=5)

# Botones
def toggle_ddos(event):
    global ddos_activado
    ddos_activado = not ddos_activado
    btn_ddos.label.set_text('DDoS ON' if ddos_activado else 'Ataque DDoS')

def toggle_ruido(event):
    global ruido_activado
    ruido_activado = not ruido_activado
    btn_ruido.label.set_text('Ruido: ON' if ruido_activado else 'Ruido: OFF')

def toggle_pausa(event):
    global simulacion_pausada
    simulacion_pausada = not simulacion_pausada
    btn_pausa.label.set_text('Reanudar' if simulacion_pausada else 'Pausar')

btn_ddos = Button(plt.axes([0.85, 0.26, 0.12, 0.04]), 'DDoS'); btn_ddos.on_clicked(toggle_ddos)
btn_ruido = Button(plt.axes([0.85, 0.20, 0.12, 0.04]), 'Ruido'); btn_ruido.on_clicked(toggle_ruido)
btn_pausa = Button(plt.axes([0.85, 0.14, 0.12, 0.04]), 'Pausar'); btn_pausa.on_clicked(toggle_pausa)

# Actualización
def update(frame):
    global pods_actuales, ultimo_escaleo, tiempo_actual

    # Si la simulación está pausada, no actualizar
    if simulacion_pausada:
        return

    # Obtener el CPU target del slider (convertir de % a decimal)
    cpu_target_actual = slider_cpu_target.val / 100.0

    carga_total = 12.0 if ddos_activado else slider_carga.val
    if ruido_activado:
        carga_total += np.random.normal(0, 0.05)
    carga_total = min(carga_total, pods_actuales * 2.0)

    uso_actual = carga_total / pods_actuales
    error = uso_actual - cpu_target_actual
    kp = slider_kp.val

    if len(tiempos) - ultimo_escaleo >= cooldown_steps:
        delta =  int(np.round(kp * error))
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
    errores.append(error)
    senal_f.append(uso_actual)

    # Graficar
    line_cpu.set_data(tiempos, uso_cpu)
    line_pods.set_data(tiempos, cantidad_pods)
    line_carga.set_data(tiempos, carga_registrada)
    line_error.set_data(tiempos, errores)
    line_f.set_data(tiempos, senal_f)

    # Actualizar línea de objetivo CPU
    target_line.set_ydata([cpu_target_actual * 100, cpu_target_actual * 100])
    
    text_cpu.set_text(f'CPU actual: {uso_actual * 100:.1f}%')
    text_cpu.set_position((tiempo_actual - 5, uso_actual * 100))
    text_pods.set_text(f'Pods activos: {pods_actuales}')
    text_pods.set_position((tiempo_actual - 5, pods_actuales))
    text_error.set_text(f'error: {error}')
    text_error.set_position((tiempo_actual - 5, error))
    text_f.set_text(f'f: {senal_f[-1]:.2f}')
    text_f.set_position((tiempo_actual - 5, senal_f[-1]))


    ax1.relim(); ax1.autoscale_view()
    ax2.relim(); ax2.autoscale_view()
    ax3.relim(); ax3.autoscale_view()
    ax4.relim(); ax4.autoscale_view()
    ax5.relim(); ax5.autoscale_view()

    tiempo_actual += dt

# Ejecutar animación
ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)

def reset_simulacion(event):
    global pods_actuales, ultimo_escaleo, tiempo_actual
    global tiempos, uso_cpu, cantidad_pods, carga_registrada
    global errores, senal_f
    global ddos_activado, ruido_activado, simulacion_pausada

    # Reset variables de estado
    pods_actuales = 2
    ultimo_escaleo = -cooldown_steps
    tiempo_actual = 0.0
    ddos_activado = False
    ruido_activado = True
    simulacion_pausada = False

    # Reset arrays
    tiempos.clear()
    uso_cpu.clear()
    cantidad_pods.clear()
    carga_registrada.clear()
    errores.clear()
    senal_f.clear()

    # Reset sliders
    slider_carga.set_val(1)
    slider_kp.set_val(4.0)
    slider_cpu_target.set_val(60)

    # Reset etiquetas de botones
    btn_ddos.label.set_text("Ataque DDoS")
    btn_ruido.label.set_text("Ruido: ON")
    btn_pausa.label.set_text("Pausar")

    # Limpiar gráficos
    line_cpu.set_data([], [])
    line_pods.set_data([], [])
    line_carga.set_data([], [])
    line_error.set_data([], [])
    line_f.set_data([], [])
    text_cpu.set_text('')
    text_pods.set_text('')
    text_error.set_text('')
    text_f.set_text('')

    ax1.relim(); ax1.autoscale_view()
    ax2.relim(); ax2.autoscale_view()
    ax3.relim(); ax3.autoscale_view()
    ax4.relim(); ax4.autoscale_view()
    ax5.relim(); ax5.autoscale_view()
    fig.canvas.draw_idle()

# Crear botón de reset
btn_reset = Button(plt.axes([0.85, 0.08, 0.12, 0.04]), 'Reset')
btn_reset.on_clicked(reset_simulacion)

# Mostrar simulación
plt.show()
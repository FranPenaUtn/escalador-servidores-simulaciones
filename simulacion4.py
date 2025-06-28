import numpy as np
import matplotlib.pyplot as plt

# Parámetros de simulación
total_time_minutes = 120  # tiempo total de simulación en minutos (2 horas)
dt = 0.5  # paso de tiempo en minutos (0.5 min = 30 segundos por paso)
num_steps = int(total_time_minutes / dt) + 1  # cantidad de instantes de tiempo simulados

# Setpoint (objetivo) de utilización de CPU (fracción de 1, es decir 0.60 = 60%)
cpu_target = 0.60

# Límite mínimo y máximo de pods
min_pods = 2
max_pods = 10

# Tiempo de enfriamiento (cooldown) en minutos para evitar escalados muy seguidos
cooldown_minutes = 5  # por ejemplo, 5 minutos de espera mínima entre escalados
cooldown_steps = int(cooldown_minutes / dt)

# Función que modela la carga del sistema (con picos y caídas en el tiempo)
def carga_sistema(t):
    """
    Devuelve la carga total relativa a la capacidad de un pod en el tiempo t (minutos).
    Incluye una carga base y picos de carga en ciertos intervalos de tiempo.
    """
    # Carga base (por ejemplo, 0.5 corresponde a 50% de uso de un pod)
    carga = 0.5
    # Pico 1: alta carga entre 25 y 35 minutos
    if 25 <= t < 35:
        carga += 1.5  # aumento de carga (pico alto)        
    # Pico 2: carga moderada entre 50 y 55 minutos
    if 50 <= t < 55:
        carga += 0.8  # aumento de carga (pico moderado)
    # Pico 3: alta carga entre 80 y 90 minutos
    if 80 <= t < 90:
        carga += 1.5  # aumento de carga (segundo pico alto)

    return carga

# Arreglos para almacenar resultados en el tiempo
tiempos = np.arange(0, total_time_minutes + 0.0001, dt)  # vector de tiempo en minutos
uso_cpu = np.zeros_like(tiempos)    # utilización de CPU por pod (fracción de 1)
cantidad_pods = np.zeros_like(tiempos)  # número de pods activos

# Condiciones iniciales
pods_actuales = min_pods  # iniciar con el número mínimo de pods
ultimo_escaleo = -cooldown_steps  # indicador de último paso donde se escaló (inicializar negativo para permitir escalar al inicio)

retardo_minutos = 2
retardo_steps = int(retardo_minutos / dt)
escalado_pendiente = [min_pods] * retardo_steps  # Inicializar la cola

# Bucle de simulación en pasos de dt
for i, t in enumerate(tiempos):
    # 1. Calcular carga actual del sistema
    carga_total = carga_sistema(t)
    # 2. Calcular utilización promedio de CPU por pod
    uso_actual = carga_total / pods_actuales
    # Guardar métricas actuales en los arreglos de resultados
    uso_cpu[i] = uso_actual
    cantidad_pods[i] = pods_actuales
    # 3. Controlador proporcional: decidir si escalar según CPU vs objetivo
    if i - ultimo_escaleo >= cooldown_steps:
        replicas_deseadas = pods_actuales * (uso_actual / cpu_target)
        nuevos_pods = int(np.ceil(replicas_deseadas))
        nuevos_pods = min(max(nuevos_pods, min_pods), max_pods)

        if nuevos_pods != pods_actuales:
            escalado_pendiente.append(nuevos_pods)  # encola el nuevo valor
            pods_actuales = escalado_pendiente.pop(0)  # aplica el más viejo
            ultimo_escaleo = i
        else:
            escalado_pendiente.append(pods_actuales)
            pods_actuales = escalado_pendiente.pop(0)
    else:
        escalado_pendiente.append(pods_actuales)
        pods_actuales = escalado_pendiente.pop(0)
# Fin del bucle de simulación

# Graficar resultados
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,6), sharex=True)
# Gráfico de utilización de CPU (% por pod)
ax1.plot(tiempos, uso_cpu * 100, color='orange', label='Utilización CPU (%)')
ax1.axhline(cpu_target * 100, color='r', linestyle='--', label='Objetivo CPU (60%)')
ax1.set_ylabel('Utilización CPU por pod (%)')
ax1.set_title('Utilización promedio de CPU por pod en el tiempo')
ax1.legend(loc='upper right')
ax1.grid(True)
# Gráfico del número de pods activos
ax2.plot(tiempos, cantidad_pods, color='orange', label='Número de Pods')
ax2.set_ylabel('Número de pods')
ax2.set_xlabel('Tiempo (minutos)')
ax2.set_title('Número de pods activos en el tiempo')
ax2.set_ylim(0, max_pods + 1)
ax2.legend(loc='upper right')
ax2.grid(True)
plt.tight_layout()
plt.show()

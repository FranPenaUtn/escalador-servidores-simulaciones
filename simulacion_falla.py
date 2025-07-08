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
    if 25 <= t < 30:
        carga += 1.5  # aumento de carga (pico alto)        
    # Pico 2: carga moderada entre 50 y 55 minutos
    if 30 <= t < 35:
        carga += 2  # aumento de carga (pico moderado)
    # inicia el ataque DDOS
    if 35 <= t < 121:
        carga += 10  # aumento de carga (segundo pico alto)

    carga += np.random.normal(0, 0.1)

    return carga


# Arreglos para almacenar resultados en el tiempo
tiempos = np.arange(0, total_time_minutes + 0.0001, dt)  # vector de tiempo en minutos
uso_cpu = np.zeros_like(tiempos)    # utilización de CPU por pod (fracción de 1)
cantidad_pods = np.zeros_like(tiempos)  # número de pods activos

# Condiciones iniciales
pods_actuales = min_pods  # iniciar con el número mínimo de pods
ultimo_escaleo = -cooldown_steps  # indicador de último paso donde se escaló (inicializar negativo para permitir escalar al inicio)

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
        # Calcular réplicas deseadas según la fórmula proporcional
        replicas_deseadas = pods_actuales * (uso_actual / cpu_target)

        # Redondear hacia arriba para no infra-provisionar (ceil asegura cubrir la carga)
        nuevos_pods = int(np.ceil(replicas_deseadas))
        # Aplicar límites mínimo y máximo
        if nuevos_pods < min_pods:
            nuevos_pods = min_pods
        if nuevos_pods > max_pods:
            nuevos_pods = max_pods
        # Si hay un cambio en la cantidad de pods, aplicar escalado
        if nuevos_pods != pods_actuales:
            pods_actuales = nuevos_pods
            ultimo_escaleo = i  # registrar el paso en que se escala
# Fin del bucle de simulación

# Graficar resultados
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,8), sharex=True)


# Gráfico de utilización de CPU (% por pod)
ax1.plot(tiempos, uso_cpu * 100, color='orange', label='Utilización CPU (%)')
ax1.axhline(cpu_target * 100, color='r', linestyle='--', label='Objetivo CPU (60%)')
ax1.axvline(x=35, color='y', linestyle='--', label='Inicio ataque DDoS')
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

# Calcular la carga total a lo largo del tiempo para graficarla
cargas = np.array([carga_sistema(t) for t in tiempos])

# Gráfico de la carga total del sistema
ax3.plot(tiempos, cargas, color='blue', label='Carga de trabajo total')
ax3.set_ylabel('Carga total')
ax3.set_xlabel('Tiempo (minutos)')
ax3.set_title('Evolución de la carga de trabajo del sistema')
ax3.grid(True)
ax3.legend(loc='upper right')


plt.tight_layout()
plt.show()

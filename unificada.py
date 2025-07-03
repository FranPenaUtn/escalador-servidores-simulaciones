import numpy as np
import matplotlib.pyplot as plt

def run_simulation(cpu_target, min_pods, max_pods, cooldown_minutes, noise_std_dev=0, enable_delay=False, delay_minutes=0):
    total_time_minutes = 120
    dt = 0.5
    num_steps = int(total_time_minutes / dt) + 1
    cooldown_steps = int(cooldown_minutes / dt)

    def carga_sistema(t, current_noise_std_dev):
        carga = 0.5
        if 25 <= t < 35:
            carga += 1.5
        if 50 <= t < 55:
            carga += 0.8
        if 80 <= t < 90:
            carga += 1.5
        if current_noise_std_dev > 0:
            carga += np.random.normal(0, current_noise_std_dev)
        return carga

    tiempos = np.arange(0, total_time_minutes + 0.0001, dt)
    uso_cpu = np.zeros_like(tiempos)
    cantidad_pods = np.zeros_like(tiempos)
    carga_total_registrada = np.zeros_like(tiempos)  # NUEVO

    pods_actuales = min_pods
    ultimo_escaleo = -cooldown_steps

    if enable_delay:
        retardo_steps = int(delay_minutes / dt)
        escalado_pendiente = [min_pods] * retardo_steps
    else:
        escalado_pendiente = []

    for i, t in enumerate(tiempos):
        carga_total = carga_sistema(t, noise_std_dev)
        carga_total_registrada[i] = carga_total  # NUEVO

        uso_actual = carga_total / pods_actuales
        uso_cpu[i] = uso_actual
        cantidad_pods[i] = pods_actuales

        if enable_delay:
            if i - ultimo_escaleo >= cooldown_steps:
                replicas_deseadas = pods_actuales * (uso_actual / cpu_target)
                nuevos_pods = int(np.ceil(replicas_deseadas))
                nuevos_pods = min(max(nuevos_pods, min_pods), max_pods)
                if nuevos_pods != escalado_pendiente[-1] if escalado_pendiente else True:
                    escalado_pendiente.append(nuevos_pods)
                elif len(escalado_pendiente) < retardo_steps:
                    escalado_pendiente.append(pods_actuales)
                if escalado_pendiente:
                    pods_actuales = escalado_pendiente.pop(0)
                if (i - ultimo_escaleo >= cooldown_steps and (nuevos_pods != (cantidad_pods[i-1] if i > 0 else min_pods)) and not enable_delay) or \
                   (enable_delay and len(escalado_pendiente) == 0):
                    ultimo_escaleo = i
            elif enable_delay:
                if escalado_pendiente:
                    pods_actuales = escalado_pendiente.pop(0)
                    escalado_pendiente.append(pods_actuales)
                else:
                    escalado_pendiente.append(pods_actuales)
        else:
            if i - ultimo_escaleo >= cooldown_steps:
                replicas_deseadas = pods_actuales * (uso_actual / cpu_target)
                nuevos_pods = int(np.ceil(replicas_deseadas))
                nuevos_pods = min(max(nuevos_pods, min_pods), max_pods)
                if nuevos_pods != pods_actuales:
                    pods_actuales = nuevos_pods
                    ultimo_escaleo = i

    # Gráficos
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    ax1.plot(tiempos, uso_cpu * 100, color='orange', label='Utilización CPU (%)')
    ax1.axhline(cpu_target * 100, color='r', linestyle='--', label=f'Objetivo CPU ({cpu_target*100:.0f}%)')
    ax1.set_ylabel('CPU por pod (%)')
    ax1.set_title('Utilización promedio de CPU por pod en el tiempo')
    ax1.legend(loc='upper right')
    ax1.grid(True)

    ax2.plot(tiempos, cantidad_pods, color='orange', label='Número de Pods')
    ax2.set_ylabel('Pods activos')
    ax2.set_title(f'Número de pods activos (Min: {min_pods}, Max: {max_pods}' + (f', Retardo: {delay_minutes}min' if enable_delay else '') + ')')
    ax2.set_ylim(0, max_pods + 1)
    ax2.legend(loc='upper right')
    ax2.grid(True)

    ax3.plot(tiempos, carga_total_registrada, color='blue', label='Carga Total del Sistema')
    ax3.set_ylabel('Carga de trabajo')
    ax3.set_xlabel('Tiempo (minutos)')
    ax3.set_title('Carga total del sistema (Perturbación externa)')
    ax3.legend(loc='upper right')
    ax3.grid(True)

    plt.tight_layout()
    plt.show()

# --------- Entrada por consola ---------

if __name__ == "__main__":
    print("--- Configuración de la Simulación del Autoscaler ---")

    while True:
        try:
            cpu_target_input = float(input("Objetivo de CPU (ej. 0.60 para 60%): "))
            if not (0 < cpu_target_input <= 1):
                raise ValueError("Debe estar entre 0 y 1.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            min_pods_input = int(input("Número mínimo de pods: "))
            if min_pods_input < 1:
                raise ValueError("Debe ser al menos 1.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            max_pods_input = int(input("Número máximo de pods: "))
            if max_pods_input < min_pods_input:
                raise ValueError("No puede ser menor que el mínimo.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            cooldown_minutes_input = int(input("Tiempo de enfriamiento (minutos): "))
            if cooldown_minutes_input < 0:
                raise ValueError("No puede ser negativo.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        add_noise_choice = input("¿Agregar ruido a la carga? (s/n): ").lower()
        if add_noise_choice in ['s', 'n']:
            break
        else:
            print("Ingrese 's' o 'n'.")

    noise_std_dev_input = 0
    if add_noise_choice == 's':
        while True:
            try:
                noise_std_dev_input = float(input("Desviación estándar del ruido (ej. 0.05): "))
                if noise_std_dev_input < 0:
                    raise ValueError("Debe ser >= 0.")
                break
            except ValueError as e:
                print(f"Error: {e}")

    while True:
        enable_delay_choice = input("¿Habilitar retardo en escalado? (s/n): ").lower()
        if enable_delay_choice in ['s', 'n']:
            break
        else:
            print("Ingrese 's' o 'n'.")

    delay_minutes_input = 0
    if enable_delay_choice == 's':
        while True:
            try:
                delay_minutes_input = int(input("Retardo en minutos: "))
                if delay_minutes_input < 0:
                    raise ValueError("No puede ser negativo.")
                break
            except ValueError as e:
                print(f"Error: {e}")

    print("\nIniciando simulación con los parámetros:")
    print(f"  Objetivo CPU: {cpu_target_input * 100:.0f}%")
    print(f"  Pods Mínimos: {min_pods_input}")
    print(f"  Pods Máximos: {max_pods_input}")
    print(f"  Tiempo de Enfriamiento: {cooldown_minutes_input} min")
    print(f"  Ruido en Carga: {'Sí' if add_noise_choice == 's' else 'No'}")
    if add_noise_choice == 's':
        print(f"    Desviación estándar: {noise_std_dev_input}")
    print(f"  Retardo en Escalado: {'Sí' if enable_delay_choice == 's' else 'No'}")
    if enable_delay_choice == 's':
        print(f"    Retardo: {delay_minutes_input} minutos")
    print("-" * 40)

    run_simulation(
        cpu_target_input,
        min_pods_input,
        max_pods_input,
        cooldown_minutes_input,
        noise_std_dev_input,
        enable_delay_choice == 's',
        delay_minutes_input
    )

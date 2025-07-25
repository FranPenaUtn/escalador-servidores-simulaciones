﻿# Simulación de Control de Autoescalado de Pods en Kubernetes

Este proyecto implementa una **simulación interactiva** de un sistema de control automático con **retroalimentación negativa**, basado en el ajuste del número de pods en función de la utilización de CPU. Está inspirado en el comportamiento del `Horizontal Pod Autoscaler (HPA)` de Kubernetes.

## 🎯 Objetivo

Controlar el uso promedio de CPU por pod, ajustando dinámicamente la cantidad de pods activos en función de la carga de trabajo, mediante un **controlador proporcional** configurable en tiempo real.

## 🖥️ Requisitos

Este script está desarrollado en Python y utiliza `matplotlib` para la visualización interactiva. Asegurate de tener instalado lo siguiente:

### 🔧 Instalación de Python (si no lo tenés)

#### 🔹 Windows

1. Descargá el instalador desde:  
   👉 [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

2. Ejecutá el instalador y asegurate de **marcar la opción** ✅ “Add Python to PATH” antes de instalar.

3. Luego hacé clic en "Install Now".

#### 🔹 macOS

1. Descargá el instalador desde:  
   👉 [https://www.python.org/downloads/mac-osx/](https://www.python.org/downloads/mac-osx/)

2. Seguí los pasos del instalador.

> Alternativamente, si usás Homebrew:  
```bash
brew install python
```
#### 🔹 Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 📦 Dependencias

- Python 3.8 o superior
- matplotlib
- numpy

Podés instalar los paquetes con:

```bash
pip install matplotlib numpy
```

## 🚀 Cómo ejecutar la simulación

1. Cloná el repositorio:

```bash
git clone https://github.com/FranPenaUtn/escalador-servidores-simulaciones
cd escalador-servidores-simulaciones
```

2. Ejecutá el script principal:

```bash
python simulacion_final.py
```

> Asegurate de tener un entorno gráfico disponible (no funciona desde terminal sin entorno gráfico, como WSL puro o servidores sin X11).

## 🧩 Características

- Visualización de:
  - Utilización promedio de CPU por pod
  - Cantidad de pods activos
  - Carga total del sistema

- Controles interactivos:
  - 🎚️ Slider y caja de entrada para modificar la **carga** en tiempo real
  - 🎚️ Slider y caja de entrada para ajustar la **ganancia proporcional (Kp)**
  - ⚠️ Botón para simular un **ataque DDoS**
  - 🎲 Botón para activar/desactivar **ruido aleatorio**
  - 🔁 Botón para **resetear** la simulación a su estado inicial

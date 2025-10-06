# Dungeon Mapa Generator

## 🗺️ Visión General del Proyecto

`Dungeon Map Generator` es un proyecto de simulación en Python que implementa un **juego de exploración de mazmorras (dungeon) basado en texto**. El sistema genera un **Mapa** proceduralmente, donde el **Explorador** navega entre habitaciones, gestiona su vida e interactúa con el **Contenido** (Monstruos, Tesoros, Jefes y Eventos).

El proyecto está diseñado de forma modular, con clases dedicadas para la generación de la estructura, la lógica del personaje y las interacciones de contenido.

---

## 🚀 Requisitos e Instalación

### Requisitos Previos

Necesitas tener **Python 3.x** instalado.

### 1. Instalación de Dependencias

Este proyecto utiliza la biblioteca `rich` para una salida de texto enriquecida y con formato en la terminal.

Navega al directorio raíz (`dungeonmapa`) e instala la dependencia:

```bash
pip install rich


2. Estructura del Directorio

El código se organiza en un paquete llamado dungeon_generator y un script principal main.py:

dungeonmapa/
├── dungeon_generator/
│   ├── __init__.py      # (vacío, para definir el paquete.)
│   ├── contenido.py     # Monstruos, Jefes, Tesoros, Eventos (Trampa, Portal, Curacion).
│   ├── explorador.py    # Clase del personaje principal.
│   ├── habitacion.py    # Clase para cada celda del mapa.
│   ├── mapa.py          # Lógica de generación de la mazmorra y colocación de contenido.
│   └── ... (otros módulos como objeto.py)
└── main.py              # Punto de entrada del juego.

🎮 Cómo Jugar

Iniciar la Simulación

Ejecuta el archivo principal desde el directorio raíz (dungeonmapa):
Bash

python3 main.py

El juego inicializará el mapa (10x10) con 30 habitaciones y distribuirá el contenido aleatoriamente, incluyendo un Jefe final.

Comandos de Interacción

El juego funciona por turnos. En cada turno, se te pedirá una acción:
Comando	Función
NORTE, SUR, ESTE, OESTE	Intenta mover al Explorador a una habitación adyacente conectada.
EXPLORAR	Activa la interacción con el contenido de la habitación actual (lucha, abre tesoro, activa evento, etc.).
ESTADO	Muestra la vida actual, la ubicación y el inventario del Explorador.
MAPA	Muestra una representación de las habitaciones visitadas y tu posición actual (X).
GUARDAR	Simula el guardado del estado del juego.
SALIR	Termina la sesión de juego.

Objetivo del Juego

Encuentra la habitación del Jefe y derrótalo usando el comando EXPLORAR para ganar el juego.


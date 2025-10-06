rom dungeon_generator.mapa import Mapa
from dungeon_generator.explorador import Explorador
from dungeon_generator.objeto import Objeto
from rich.console import Console
from rich.panel import Panel
from rich import print
from typing import Tuple, Optional
import os
import time
import random

ANCHO_MAPA = 10
ALTO_MAPA = 10
NUM_HABITACIONES = 30
VIDA_INICIAL = 10

console = Console()

def mostrar_bienvenida(explorador: Explorador):
    explorador.habitacion_actual.visitada = True
    
    print(Panel(
        f"[bold green]¡Bienvenido al Dungeon Mapa Generador![/bold green]\n"
        f"Tu aventura comienza en la habitación {explorador.posicion_actual}.\n"
        f"Explorador [yellow]{explorador.vida}/{explorador.vida_max}[/yellow] HP. "
        f"Encuentra la habitación del Jefe para ganar."
    ))

def mostrar_estado(explorador: Explorador):
    inventario_str = ", ".join([obj.nombre for obj in explorador.inventario]) if explorador.inventario else "Vacío"
    
    print(Panel(
        f"[bold blue]-- ESTADO DEL EXPLORADOR --[/bold blue]\n"
        f"Ubicación: {explorador.posicion_actual}\n"
        f"Vida: [red]{explorador.vida}/{explorador.vida_max}[/red]\n"
        f"Inventario: {inventario_str}"
    ))

def mostrar_mapa(mapa: Mapa, explorador: Explorador):
    mapa_str = ""
    for y in range(mapa.alto):
        for x in range(mapa.ancho):
            hab = mapa.obtener_habitacion(x, y)
            
            if (x, y) == explorador.posicion_actual:
                mapa_str += "[bold magenta]X[/bold magenta]"
            elif hab and hab.visitada:
                simbolo = ""
                if hab.estado == "Jefe": simbolo = "[bold red]J[/bold red]"
                elif hab.estado == "Monstruo": simbolo = "[bold yellow]M[/bold yellow]"
                elif hab.estado == "Tesoro": simbolo = "[bold green]T[/bold green]"
                elif hab.estado == "Evento": simbolo = "[bold cyan]E[/bold cyan]"
                else: simbolo = "[grey]#[/grey]"
                mapa_str += simbolo
            elif hab:
                mapa_str += "[dim]?[/dim]"
            else:
                mapa_str += " "
                
        mapa_str += "\n"
        
    print(Panel(mapa_str, title="Mapa del Dungeon"))
    
    adyacentes = explorador.habitacion_actual.obtener_conexiones()
    print(f"Conexiones disponibles: [bold yellow]{', '.join(adyacentes)}[/bold yellow]")


def inicializar_juego() -> Tuple[Mapa, Explorador]:
    
    random.seed(42)
    
    console.print("Generando estructura de {} habitaciones...".format(NUM_HABITACIONES))
    mapa = Mapa(ANCHO_MAPA, ALTO_MAPA)
    mapa.generar_estructura(NUM_HABITACIONES)
    
    recompensa_final = Objeto(nombre="Amuleto de Leyenda", descripcion="Objeto clave para la victoria.", valor=1000)
    mapa.colocar_jefe(recompensa_final)

    console.print("Distribuyendo contenido (Tesoros, Monstruos, Eventos)...")
    mapa.colocar_contenido()
    
    explorador = Explorador(
        mapa=mapa,
        posicion_inicial=mapa.entrada_segura,
        vida_max=VIDA_INICIAL
    )
    
    explorador.habitacion_actual.visitada = True
    
    return mapa, explorador

def simular_interaccion(explorador: Explorador, visualizador: Console):
    
    opciones_validas = {"ESTE", "NORTE", "SUR", "OESTE", "SALIR", "ESTADO", "MAPA", "GUARDAR", "EXPLORAR"}
    turno = 1
    
    while explorador.vida > 0:
        visualizador.print(f"\n[bold]-- TURNO {turno} --[/bold]")
        
        hab_actual = explorador.habitacion_actual
        desc_contenido = hab_actual.contenido.descripcion if hab_actual.contenido else "Vacía"
        visualizador.print(f"Estás en la habitación {hab_actual.x, hab_actual.y}. Estado: {hab_actual.estado}. Contenido: {desc_contenido}")
        
        comando = visualizador.input("¿Qué deseas hacer? (Opciones: ESTE, SUR, SALIR, ESTADO, MAPA, GUARDAR, EXPLORAR): ").upper()
        
        if comando not in opciones_validas:
            visualizador.print("[bold red]Comando inválido.[/bold red] Intenta de nuevo.")
            continue
            
        if comando == "SALIR":
            visualizador.print("[bold cyan]¡Adiós! Gracias por jugar.[/bold cyan]")
            break
        elif comando == "ESTADO":
            mostrar_estado(explorador)
        elif comando == "MAPA":
            mostrar_mapa(explorador.mapa, explorador)
        elif comando == "EXPLORAR":
            interaccion = explorador.explorar_habitacion()
            visualizador.print(interaccion)
            
            if hab_actual.estado == "Jefe" and hab_actual.contenido is None:
                   visualizador.print("[bold yellow blink]¡HAS DERROTADO AL JEFE Y GANADO EL JUEGO![/bold yellow blink]")
                   break
            
            if explorador.vida <= 0: break
            
        elif comando in {"NORTE", "SUR", "ESTE", "OESTE"}:
            if explorador.moverse(comando.upper()):
                visualizador.print(f"Te has movido a la habitación {explorador.posicion_actual} en dirección {comando}.")
            else:
                visualizador.print("[bold red]No hay conexión[/bold red] en esa dirección.")
        
        elif comando == "GUARDAR":
            try:
                stats = "Información del mapa (simulado)"
                with open("juego_guardado.txt", "w") as f:
                    f.write(f"Estado de Explorador - Vida: {explorador.vida}/{explorador.vida_max}, Posición: {explorador.posicion_actual}\n")
                    f.write(f"Estadísticas del Mapa: {stats}\n")
                visualizador.print("[bold green]Juego guardado[/bold green] en 'juego_guardado.txt'.")
            except Exception as e:
                 visualizador.print(f"[bold red]Error al guardar:[/bold red] {e}")


        turno += 1
    
    if explorador.vida <= 0:
        visualizador.print("\n[bold red]GAME OVER. Tu vida llegó a cero.[/bold red]")

def main():
    mapa_base, explorador_base = inicializar_juego()
    mostrar_bienvenida(explorador_base)
    mostrar_mapa(mapa_base, explorador_base)
    simular_interaccion(explorador_base, console)

if __name__ == "__main__":
    main()


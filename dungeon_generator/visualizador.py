

from rich import print
from rich.table import Table
from typing import TYPE_CHECKING, Optional

# Importaciones circulares para tipado
if TYPE_CHECKING:
    from .explorador import Explorador
    from .mapa import Mapa
    from .habitacion import Habitacion

class Visualizador:
    """Clase encargada de la salida y visualización de la información."""
    
    def __init__(self, mapa: 'Mapa'):
        self.mapa = mapa

    def mostrar_habitacion_actual(self, explorador: 'Explorador'):
        """Muestra los detalles de la habitación actual y las conexiones disponibles."""
        hab = explorador.habitacion_actual
        
        # --- Cabecera de la habitación ---
        print(f"\n╭────────────────────────────────────────────────────────────────────────────────────────────── HABITACIÓN ACTUAL ({hab.x},{hab.y}) ───────────────────────────────────────────────────────────────────────────────────────────────╮")
        
        # --- Detalles de la habitación ---
        print(f"│ ID: {hab.id:<20} Estado: {hab.estado:<20} Visitada: {'Sí' if hab.visitada else 'No':<20} Distancia Manhattan: {hab.distancia_manhattan:<20} │")
        
        # --- Contenido ---
        contenido_desc = hab.contenido.descripcion if hab.contenido else "Nada aparente."
        print(f"│ Contenido: {contenido_desc}")
        
        # --- Conexiones ---
        conexiones_desc = ", ".join(hab.conexiones.keys()).upper()
        if not conexiones_desc:
            conexiones_desc = "NINGUNA (Habitación sin salida)"
        
        print(f"│ Direcciones disponibles: {conexiones_desc:<100}")
        
        print("╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯")
        
        self.mostrar_minimapa(explorador)


    # (mostrar_estadisticas_mapa) ---
    def mostrar_estadisticas_mapa(self, mapa: 'Mapa'):
        """Muestra las estadísticas estructurales y de contenido del mapa (Req. 7)."""
        stats = mapa.obtener_estadisticas_mapa()
        
        print("\n" * 2) # Espacio para claridad
        
        # Tabla de Métricas Generales
        table_metricas = Table(title="ESTADÍSTICAS DEL MAPA", show_header=True, header_style="bold magenta")
        table_metricas.add_column("Métrica", style="cyan")
        table_metricas.add_column("Valor", style="yellow")
        
        table_metricas.add_row("Habitaciones Totales", str(stats['habitaciones_totales']))
        table_metricas.add_row("Promedio Conexiones", f"{stats['promedio_conexiones']:.2f}")

        print(table_metricas)

        # Tabla de Distribución de Contenido
        table_contenido = Table(title="DISTRIBUCIÓN DE CONTENIDO", show_header=True, header_style="bold green")
        table_contenido.add_column("Tipo", style="cyan")
        table_contenido.add_column("Cantidad", style="yellow")
        
        # Imprime la distribución de contenido
        for tipo, cantidad in stats['distribucion_contenido'].items():
            # Capitalizar el tipo para mejor presentación
            table_contenido.add_row(tipo.capitalize(), str(cantidad)) 

        print(table_contenido)
        print("\n")


    def mostrar_explorador_estado(self, explorador: 'Explorador'):
        """Muestra la vida y el inventario del explorador."""
        
        table_estado = Table(title="ESTADO DEL EXPLORADOR", show_header=True, header_style="bold blue")
        table_estado.add_column("Métrica", style="cyan")
        table_estado.add_column("Valor", style="yellow")
        
        table_estado.add_row("Vida", f"{explorador.vida}/{explorador.vida_max}")
        table_estado.add_row("Posición Actual", str(explorador.posicion))
        
        # Resumen de inventario
        inventario_resumen = ", ".join([f"{obj.nombre} ({obj.valor})" for obj in explorador.inventario])
        
        table_estado.add_row("Inventario", "Vacío" if not explorador.inventario else f"{len(explorador.inventario)} items")
        table_estado.add_row("Valor Total Inventario", str(explorador.obtener_inventario_valor()))
        
        print(table_estado)
        
    def mostrar_minimapa(self, explorador: 'Explorador'):
        """Muestra una representación visual simple del minimapa (solo visitadas)."""
        
        print("╭────────────────────────────────────────────────────────────────────────────────────────────── MINIMAPA (Visitado) ───────────────────────────────────────────────────────────────────────────────────────────────╮")
        
        # Lógica para determinar los límites del minimapa (por ejemplo, 6x6 alrededor del explorador)
        cx, cy = explorador.posicion
        mapa_width = self.mapa.ancho
        mapa_height = self.mapa.alto
        
        # Muestra una ventana de 6x6, centrada o ajustada
        size = 6
        start_x = max(0, cx - size // 2)
        end_x = min(mapa_width, cx + size // 2 + 1)
        start_y = max(0, cy - size // 2)
        end_y = min(mapa_height, cy + size // 2 + 1)
        
        # Asegurarse de tener al menos 6x6 si es posible
        if end_x - start_x < size and mapa_width >= size: end_x = start_x + size
        if end_y - start_y < size and mapa_height >= size: end_y = start_y + size

        output = []
        for y in range(mapa_height):
            line = []
            for x in range(mapa_width):
                hab = self.mapa.obtener_habitacion(x, y)
                
                # Símbolos
                if (x, y) == (cx, cy):
                    line.append(" @ ") # Posición del explorador
                elif hab and hab.visitada:
                    # Usamos un símbolo simple para la habitación visitada, por ejemplo un punto.
                    if hab.contenido and hab.contenido.tipo == 'jefe':
                        line.append(" J ") # Jefe
                    elif hab.contenido and hab.contenido.tipo == 'monstruo':
                        line.append(" M ") # Monstruo
                    elif hab.contenido and hab.contenido.tipo == 'tesoro':
                        line.append(" T ") # Tesoro
                    elif hab.inicial:
                        line.append(" I ") # Inicial
                    else:
                        line.append(" . ") 
                else:
                    line.append("   ") # No visitada (espacio vacío)
            
            # Imprime solo las filas dentro de la ventana de visualización
            if start_y <= y < end_y:
                 output.append("".join(line))
        
        # Imprime el minimapa
        print("\n".join(output))

        print("╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯")

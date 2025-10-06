

from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING, Optional, List
# Importar Objeto (asumido)
from .objeto import Objeto 

# Usamos TYPE_CHECKING para evitar la dependencia circular con Mapa y Explorador
if TYPE_CHECKING:
    from .explorador import Explorador
    from .mapa import Mapa 

class ContenidoHabitacion(ABC):
    """Clase base abstracta para todo el contenido de las habitaciones."""
    
    @property
    @abstractmethod
    def descripcion(self) -> str:
        pass

    @property
    @abstractmethod
    def tipo(self) -> str:
        pass

    @abstractmethod
    def interactuar(self, explorador: 'Explorador') -> str:
        pass

class Tesoro(ContenidoHabitacion):
    def __init__(self, recompensa: Objeto):
        self.recompensa = recompensa

    @property
    def tipo(self) -> str:
        return "tesoro"
    
    @property
    def descripcion(self) -> str:
        return f"Un tesoro brillante: {self.recompensa.nombre}."

    def interactuar(self, explorador: 'Explorador') -> str:
        explorador.inventario.append(self.recompensa)
        explorador.habitacion_actual.contenido = None 
        return f"[bold green]¡TESORO RECIBIDO![/bold green] Has encontrado {self.recompensa.nombre} (Valor: {self.recompensa.valor})."

class Monstruo(ContenidoHabitacion):
    def __init__(self, vida: int, ataque: int, nombre: str = "Orco Salvaje"):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self._vida_max = vida 

    @property
    def tipo(self) -> str:
        return "monstruo"
    
    @property
    def descripcion(self) -> str:
        return f"Un Monstruo ({self.nombre}) con {self.vida} HP te bloquea el camino."

    def interactuar(self, explorador: 'Explorador') -> str:
        if self.vida <= 0:
            return f"El {self.nombre} ya fue derrotado."
            
        dano_a_explorador = self.ataque
        
        # Asumiendo un combate simplificado: 60% de probabilidad de golpe para el explorador
        if random.random() < 0.6: 
            self.vida = 0
            explorador.habitacion_actual.contenido = None
            return f"[bold green]¡VICTORIA![/bold green] Has derrotado al {self.nombre}."
        else:
            explorador.recibir_dano(dano_a_explorador)
            # CORRECCIÓN: Usar explorador.vida_max
            return f"[bold red]¡ATAQUE RECIBIDO![/bold red] El {self.nombre} te golpea. Pierdes {dano_a_explorador} vida. Tu vida: {explorador.vida}/{explorador.vida_max}"


class Jefe(Monstruo):
    def __init__(self, vida: int, ataque: int, recompensa_especial: Objeto):
        super().__init__(vida, ataque, nombre="Gran Jefe Oscuro")
        self.recompensa_especial = recompensa_especial
        
    @property
    def tipo(self) -> str:
        return "jefe"
    
    @property
    def descripcion(self) -> str:
        return f"El Jefe final ({self.nombre}) con {self.vida} HP. ¡Peligro!"
    
    def interactuar(self, explorador: 'Explorador') -> str:
        if self.vida <= 0:
            return f"El {self.nombre} (Jefe) ya fue derrotado."
            
        dano_a_explorador = self.ataque
        
        # Combate de Jefe simplificado: 30% de probabilidad de golpe para el explorador
        if random.random() < 0.3: 
            self.vida = 0
            explorador.inventario.append(self.recompensa_especial)
            explorador.habitacion_actual.contenido = None
            return f"[bold yellow]¡ÉPICA VICTORIA![/bold yellow] Has derrotado al {self.nombre} y has obtenido el {self.recompensa_especial.nombre}."
        else:
            explorador.recibir_dano(dano_a_explorador)
            # CORRECCIÓN: Usar explorador.vida_max
            return f"[bold red]¡GOLPE DE JEFE![/bold red] El {self.nombre} te inflige {dano_a_explorador} daño. Tu vida: {explorador.vida}/{explorador.vida_max}"

class Evento(ContenidoHabitacion):
    """Clase base para Eventos Aleatorios."""
    
    @property
    def tipo(self) -> str:
        return "evento"
    
    @property
    def descripcion(self) -> str:
        return self._nombre_evento

    def __init__(self, nombre: str, efecto: str):
        self._nombre_evento = nombre
        self._efecto = efecto

    def interactuar(self, explorador: 'Explorador') -> str:
        return f"[bold yellow]EVENTO: {self._nombre_evento}[/bold yellow] - {self._efecto}"


class Trampa(Evento):
    """Subclase de Evento: Trampa que reduce vida."""
    def __init__(self, dano: int):
        super().__init__("Trampa Oculta", f"Una trampa se activa y pierdes {dano} de vida.")
        self.dano = dano

    def interactuar(self, explorador: 'Explorador') -> str:
        explorador.recibir_dano(self.dano)
        explorador.habitacion_actual.contenido = None
        return f"[bold red]¡TRAMPA![/bold red] Se activa una trampa. Pierdes {self.dano} vida. Vida restante: {explorador.vida}."

class Curacion(Evento):
    """Subclase de Evento: Fuentes que restauran vida."""
    def __init__(self, cura: int):
        super().__init__("Fuente de Vida", f"Una fuente mágica restaura {cura} de tu vida.")
        self.cura = cura

    def interactuar(self, explorador: 'Explorador') -> str:
        # Usamos explorador.vida_max (corregido previamente)
        vida_recuperada = min(self.cura, explorador.vida_max - explorador.vida) 
        
        explorador.vida += vida_recuperada
        explorador.habitacion_actual.contenido = None
        
        return f"[bold green]¡CURACIÓN![/bold green] Bebes de la fuente y recuperas {vida_recuperada} vida. Vida actual: {explorador.vida}/{explorador.vida_max}."

class Portal(Evento):
    """Subclase de Evento: Portales que teletransportan."""
    
    # El tipo 'mapa' se omite en el constructor para evitar la dependencia circular
    def __init__(self, mapa): 
        super().__init__("Portal Dimensional", "Un portal te teletransporta a un lugar aleatorio del dungeon.")
        self.mapa = mapa 

    def interactuar(self, explorador: 'Explorador') -> str:
        habitaciones_keys = list(self.mapa.habitaciones.keys())
        if not habitaciones_keys:
             return "[bold yellow]El portal parpadea[/bold yellow], pero no encuentra destino."
             
        nueva_posicion = random.choice(habitaciones_keys)
        
        nueva_habitacion = self.mapa.obtener_habitacion(nueva_posicion[0], nueva_posicion[1])
        # Asignar nueva posición
        explorador.posicion_actual = nueva_posicion 
        explorador.habitacion_actual.visitada = True
        explorador.habitacion_actual.contenido = None 
        
        return f"[bold magenta]¡TELETRANSPORTE![/bold magenta] El portal te ha movido a {nueva_posicion}."

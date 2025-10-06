

from typing import Tuple, List, Optional, TYPE_CHECKING
from .objeto import Objeto 

if TYPE_CHECKING:
    from .mapa import Mapa
    from .habitacion import Habitacion

class Explorador:
    """Representa al personaje que explora el dungeon."""

    def __init__(self, mapa: 'Mapa', vida: int = 5):
        self.vida = vida
        self.vida_max = vida 
        self.inventario: List[Objeto] = []
        self.mapa = mapa
        
        # Esta línea ahora funciona porque Habitacion tiene la propiedad 'coordenadas'
        self.posicion_actual: Tuple[int, int] = mapa.habitacion_inicial.coordenadas if mapa.habitacion_inicial else (0, 0)
        
        self.bonificacion_combate = 0 

    @property
    def habitacion_actual(self) -> 'Habitacion':
        """Retorna la habitación actual basada en las coordenadas."""
        return self.mapa.obtener_habitacion(self.posicion_actual[0], self.posicion_actual[1])

    @property
    def esta_vivo(self) -> bool:
        """Verifica si el explorador tiene vida restante."""
        return self.vida > 0

    def mover(self, direccion: str) -> bool:
        """Moverse entre habitaciones conectadas."""
        hab_actual = self.habitacion_actual
        if direccion in hab_actual.conexiones:
            nueva_hab = hab_actual.conexiones[direccion]
            self.posicion_actual = nueva_hab.coordenadas
            
            if self.bonificacion_combate > 0:
                self.bonificacion_combate -= 1
            
            return True
        return False

    def explorar_habitacion(self) -> str:
        """Interactuar con el contenido de la habitación."""
        hab_actual = self.habitacion_actual
        hab_actual.visitada = True
        
        if hab_actual.contenido:
            return hab_actual.contenido.interactuar(self)
        
        return "La habitación está vacía. No hay nada que hacer aquí."

    def obtener_habitaciones_adyacentes(self) -> List[str]:
        """Listar direcciones disponibles."""
        return list(self.habitacion_actual.conexiones.keys())

    def recibir_dano(self, cantidad: int):
        """Reducir vida del explorador."""
        self.vida = max(0, self.vida - cantidad)
        if not self.esta_vivo:
            print("[bold red]¡HAS MUERTO![/bold red] Tu aventura termina aquí.")

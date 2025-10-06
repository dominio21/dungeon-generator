
from typing import Dict, Tuple, Optional, TYPE_CHECKING
# Importaciones necesarias (asumiendo que ContenidoHabitacion está en otro archivo)
if TYPE_CHECKING:
    from .contenido import ContenidoHabitacion

class Habitacion:
    """Representa una celda en el mapa del dungeon."""
    
    def __init__(self, id: int, x: int, y: int, inicial: bool = False):
        self.id = id
        self.x = x
        self.y = y
        self.inicial = inicial
        self.conexiones: Dict[str, 'Habitacion'] = {}
        self.contenido: Optional['ContenidoHabitacion'] = None
        self.visitada = False
        self.distancia_manhattan = 0
        self.estado = "Vacía"
        
    @property
    def coordenadas(self) -> Tuple[int, int]:
        
        return (self.x, self.y)

 

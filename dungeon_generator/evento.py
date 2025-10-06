
from .contenido import ContenidoHabitacion
import random



class Evento(ContenidoHabitacion):
    """Clase base abstracta para todos los eventos."""
    
    @property
    def tipo(self) -> str:
        return 'evento'

    @property
    def descripcion(self) -> str:
        raise NotImplementedError("La descripción del evento debe ser implementada.")

    def interactuar(self, explorador) -> str:
        raise NotImplementedError("El método interactuar del evento debe ser implementado.")


class EventoTeletransporte(Evento):
    """Teletransporta al explorador a una habitación visitada aleatoria."""
    def __init__(self, mapa):
        super().__init__(tipo='evento', descripcion="Un portal inestable te espera.")
        self.mapa = mapa # Necesita la referencia del mapa para teletransportar
        
    @property
    def descripcion(self) -> str:
        return "Un portal inestable te espera: ¡podrías terminar en cualquier lugar!"

    def interactuar(self, explorador) -> str:
        habitaciones_visitadas = [
            h for h in self.mapa.habitaciones.values() 
            if h.visitada and h.current_pos != explorador.current_pos
        ]
        
        if habitaciones_visitadas:
            destino = random.choice(habitaciones_visitadas)
            
            # Mover el explorador directamente (sin usar el método mover)
            explorador.current_pos = (destino.x, destino.y)
            return f"¡Un rayo de energía te golpea! Has sido teletransportado a ({destino.x}, {destino.y})."
        else:
            return "El portal parpadea pero no encuentra un destino viable. No pasa nada."


class EventoCuracion(Evento):
    """Cura al explorador una cantidad fija de vida."""
    def __init__(self, curacion: int):
        super().__init__(tipo='evento', descripcion=f"Encuentras una fuente mágica (+{curacion} Vida).")
        self.curacion = curacion
        
    @property
    def descripcion(self) -> str:
        return f"Encuentras una fuente mágica que irradia curación (+{self.curacion} Vida)."

    def interactuar(self, explorador) -> str:
        vida_antes = explorador.vida
        explorador.vida += self.curacion
        
        if explorador.vida > 10: # Asumimos 10 como vida máxima
            explorador.vida = 10 
            return f"Te has curado {explorador.vida - vida_antes} puntos de vida. ¡Estás al máximo!"
        
        return f"Te sumerges en la fuente. Has recuperado {self.curacion} puntos de vida."


class EventoTrampa(Evento):
    """Causa daño al explorador."""
    def __init__(self, dano: int):
        super().__init__(tipo='evento', descripcion=f"¡Es una trampa oculta! (-{dano} Vida).")
        self.dano = dano
        
    @property
    def descripcion(self) -> str:
        return f"¡Una placa de presión activa una trampa oculta! Cuidado."

    def interactuar(self, explorador) -> str:
        explorador.recibir_dano(self.dano)
        
        if explorador.is_alive:
            return f"¡Ay! Has caído en una trampa y recibido {self.dano} de daño. Vida restante: {explorador.vida}."
        else:
            return f"¡La trampa te golpea con {self.dano} de daño! [bold red]Has muerto.[/bold red]"



import random
from typing import TYPE_CHECKING, Optional, List, Dict, Tuple
from collections import Counter
from .habitacion import Habitacion
# Importación de contenido (incluyendo todas las subclases)
from .contenido import Tesoro, Monstruo, Jefe, Evento, ContenidoHabitacion, Trampa, Curacion, Portal 
from .objeto import Objeto 


if TYPE_CHECKING:
   
    from .explorador import Explorador 

class Mapa:
    """Representa la estructura del dungeon, conteniendo todas las habitaciones."""
    
    def __init__(self, ancho: int, alto: int):
        self.ancho = ancho
        self.alto = alto
        self.habitaciones: Dict[Tuple[int, int], Habitacion] = {} 
        self.habitacion_inicial: Optional[Habitacion] = None
        self.habitacion_id_counter = 1

    def obtener_habitacion(self, x: int, y: int) -> Optional[Habitacion]:
        return self.habitaciones.get((x, y))

  --
    def generar_estructura(self, n_habitaciones: int):
        """Crea la estructura del dungeon, asegura borde inicial y accesibilidad."""
        
        borde_opciones = []
        for x in range(self.ancho):
            borde_opciones.extend([(x, 0), (x, self.alto - 1)])
        for y in range(1, self.alto - 1):
            borde_opciones.extend([(0, y), (self.ancho - 1, y)])
        borde_opciones = list(set(borde_opciones)) 

        start_x, start_y = random.choice(borde_opciones)
        
        self.habitacion_inicial = Habitacion(
            id=self.habitacion_id_counter, 
            x=start_x, 
            y=start_y, 
            inicial=True
        )
        self.habitaciones[(start_x, start_y)] = self.habitacion_inicial
        self.habitacion_id_counter += 1
        self.habitacion_inicial.distancia_manhattan = 0
        self.habitacion_inicial.estado = "Entrada Segura"
        
        cola = [self.habitacion_inicial]
        habitaciones_creadas = 1
        
        while cola and habitaciones_creadas < n_habitaciones:
            actual: Habitacion = cola.pop(random.randrange(len(cola)))
            
            direcciones = ["norte", "sur", "este", "oeste"]
            random.shuffle(direcciones)
            
            for direccion in direcciones:
                if habitaciones_creadas >= n_habitaciones: break

                dx, dy = self._obtener_delta(direccion)
                new_x, new_y = actual.x + dx, actual.y + dy
                
                if (0 <= new_x < self.ancho and 0 <= new_y < self.alto and 
                    (new_x, new_y) not in self.habitaciones and
                    random.random() < 0.6):
                    
                    nueva_hab = Habitacion(
                        id=self.habitacion_id_counter, 
                        x=new_x, 
                        y=new_y, 
                        inicial=False
                    )
                    self.habitaciones[(new_x, new_y)] = nueva_hab
                    self.habitacion_id_counter += 1
                    habitaciones_creadas += 1
                    
                    self._conectar(actual, nueva_hab, direccion)
                    
                    nueva_hab.distancia_manhattan = self._calcular_manhattan(new_x, new_y, start_x, start_y)
                    nueva_hab.estado = "Vacía"
                    
                    cola.append(nueva_hab)

    def _obtener_delta(self, direccion: str) -> Tuple[int, int]:
        return {"norte": (0, -1), "sur": (0, 1), "este": (1, 0), "oeste": (-1, 0)}.get(direccion, (0, 0))

    def _conectar(self, hab1: Habitacion, hab2: Habitacion, direccion: str):
        opuesto = {"norte": "sur", "sur": "norte", "este": "oeste", "oeste": "este"}[direccion]
        hab1.conexiones[direccion] = hab2
        hab2.conexiones[opuesto] = hab1

    def _calcular_manhattan(self, x1: int, y1: int, x2: int, y2: int) -> int:
        return abs(x1 - x2) + abs(y1 - y2)

    # --- REQUISITO 6, 11: COLOCACIÓN DE CONTENIDO (RESOLUCIÓN DEL SESGO) ---
    def colocar_contenido(self):
        """Distribuye el contenido (Monstruos, Tesoros, Jefes, Eventos)."""
        
        habitaciones_restantes: List[Habitacion] = [hab for hab in self.habitaciones.values() if not hab.inicial]

        if not habitaciones_restantes: return 
            
        # 1. COLOCAR AL JEFE
        habitaciones_ordenadas = sorted(
            habitaciones_restantes, 
            key=lambda h: h.distancia_manhattan, 
            reverse=True
        )
        jefe_habitacion = random.choice(habitaciones_ordenadas[:min(3, len(habitaciones_ordenadas))])
        self._colocar_jefe(jefe_habitacion)
        
        # 2. PREPARAR LISTA PARA ASIGNACIÓN ALEATORIA 
        habitaciones_elegibles = [hab for hab in habitaciones_restantes if hab.contenido is None]
        random.shuffle(habitaciones_elegibles) # Rompe el sesgo del Sur
        
        n_elegibles = len(habitaciones_elegibles)
        
        # 3. CALCULAR CANTIDADES
        n_monstruos = random.randint(int(n_elegibles * 0.20), int(n_elegibles * 0.30))
        n_tesoros = random.randint(int(n_elegibles * 0.15), int(n_elegibles * 0.25))
        n_eventos = random.randint(int(n_elegibles * 0.05), int(n_elegibles * 0.10))
        
        # Ajuste por límite total
        total_contenido = n_monstruos + n_tesoros + n_eventos
        if total_contenido > n_elegibles:
            n_eventos = int(n_eventos * n_elegibles / total_contenido)
            n_tesoros = int(n_tesoros * n_elegibles / total_contenido)
            n_monstruos = n_elegibles - n_tesoros - n_eventos 
            
        # 4. ASIGNACIÓN SECUENCIAL
        idx = 0
        
        for _ in range(n_monstruos):
            hab = habitaciones_elegibles[idx]; idx += 1
            hab.contenido = self._crear_contenido("monstruo", hab.distancia_manhattan)
            hab.estado = hab.contenido.tipo.capitalize()
            
        for _ in range(n_tesoros):
            hab = habitaciones_elegibles[idx]; idx += 1
            hab.contenido = self._crear_contenido("tesoro", hab.distancia_manhattan)
            hab.estado = hab.contenido.tipo.capitalize() 
            
        for _ in range(n_eventos):
            hab = habitaciones_elegibles[idx]; idx += 1
            hab.contenido = self._crear_contenido("evento", hab.distancia_manhattan)
            hab.estado = hab.contenido.tipo.capitalize() 

    def _colocar_jefe(self, habitacion: Habitacion):
        """Helper para colocar el jefe, usando la dificultad (Requisito 11)."""
        d = habitacion.distancia_manhattan
        
        recompensa = Objeto(
            nombre="Corona del Jefe", 
            valor=500 + d * 50, 
            descripcion="El tesoro final del dungeon: un símbolo de poder."
        )
        
        vida = 20 + d * 5
        ataque = 5 + d * 2
        
        habitacion.contenido = Jefe(vida=vida, ataque=ataque, recompensa_especial=recompensa)
        habitacion.estado = "Jefe"

    def _crear_contenido(self, tipo: str, distancia: int) -> ContenidoHabitacion:
        """Helper para crear Monstruo, Tesoro o Evento según el tipo y distancia."""
        
        if tipo == "monstruo":
            vida = 5 + distancia * 2
            ataque = 2 + int(distancia / 2)
            return Monstruo(vida=vida, ataque=ataque) 
            
        elif tipo == "tesoro":
            valor = 50 + distancia * 10
            recompensa = Objeto(
                nombre=f"Joya Dist. {distancia}", 
                valor=valor,
                descripcion=f"Una joya con un brillo tenue, encontrada lejos (Distancia: {distancia})."
            )
            return Tesoro(recompensa=recompensa)
            
        elif tipo == "evento":
            eventos_posibles = [
                Trampa(dano=2), 
                Curacion(cura=3), 
                Portal(self) # Pasa la instancia del Mapa (self)
            ]
            return random.choice(eventos_posibles)
            
        raise ValueError(f"Tipo de contenido desconocido: {tipo}")

-
    def obtener_estadisticas_mapa(self) -> Dict[str, int | float]:
        n_habitaciones = len(self.habitaciones)
        contador_contenido = Counter()
        total_conexiones = 0
        
        for hab in self.habitaciones.values():
            tipo_contenido = hab.contenido.tipo if hab.contenido else "vacía"
            contador_contenido[tipo_contenido] += 1
            total_conexiones += len(hab.conexiones)

        promedio_conexiones = total_conexiones / n_habitaciones if n_habitaciones > 0 else 0
        
        return {
            "habitaciones_totales": n_habitaciones,
            "distribucion_contenido": dict(contador_contenido),
            "promedio_conexiones": promedio_conexiones
        }

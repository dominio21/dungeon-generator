
import json
import os
from typing import TYPE_CHECKING, Any, Callable, Union 
from rich import print

# IMPORTACIONES NECESARIAS PARA DEFINIR TIPOS Y LÓGICA

from .mapa import Mapa          
from .explorador import Explorador 
from .habitacion import Habitacion # Necesario para reconstruir habitaciones
from .objeto import Objeto # Necesario para reconstruir el inventario

# Contenido de combate y tesoro desde .contenido
from .contenido import Tesoro, Monstruo, Jefe, ContenidoHabitacion
# Contenido de eventos desde .evento
from .evento import EventoTeletransporte, EventoCuracion, EventoTrampa

# --- AUXILIARES DE SERIALIZACIÓN ---

def _objeto_a_diccionario(obj: Any) -> dict:
    """Convierte un objeto complejo a un diccionario con metadatos de clase."""
    
    # 1. Clases con __dict__ simple (Contenido, Objeto)
    if isinstance(obj, (Tesoro, Monstruo, Jefe, 
                        EventoTeletransporte, EventoCuracion, EventoTrampa, 
                        ContenidoHabitacion, Objeto)):
        
        data = obj.__dict__.copy()
        
        # Excepción: EventoTeletransporte no debe serializar la referencia del mapa
        if isinstance(obj, EventoTeletransporte):
            # Usamos getattr para verificar si existe la referencia interna
            if getattr(obj, 'mapa', None): 
                del data['mapa']

        return {
            '__clase__': obj.__class__.__name__,
            '__data__': data
        }
    
    # 2. Habitacion
    elif isinstance(obj, Habitacion):
        data = obj.__dict__.copy()
        
        # Convertir objetos de conexión a tuplas de coordenadas
        if 'conexiones' in data:
            data['conexiones'] = {
                direccion: (hab.x, hab.y) 
                for direccion, hab in data['conexiones'].items()
            }
        
        return {
            '__clase__': 'Habitacion',
            '__data__': data
        }
    
    # 3. Mapa (Serializa el mapa sin el dict 'habitaciones' para evitar recursividad)
    elif isinstance(obj, Mapa):
        data = obj.__dict__.copy()
        
        if 'habitaciones' in data:
             del data['habitaciones'] 
        
        # Guardamos la posición de la inicial y jefe en tupla
        data['habitacion_inicial_pos'] = obj.habitacion_inicial.x, obj.habitacion_inicial.y if obj.habitacion_inicial else None
        data['habitacion_jefe_pos'] = obj.habitacion_jefe.x, obj.habitacion_jefe.y if obj.habitacion_jefe else None
        
        return {
            '__clase__': 'Mapa',
            '__data__': data
        }

    # 4. Explorador (Serializa sin la referencia al mapa)
    elif isinstance(obj, Explorador):
        data = obj.__dict__.copy()
        if 'mapa' in data:
            del data['mapa']
        return {
            '__clase__': 'Explorador',
            '__data__': data
        }

    # Permitir que el codificador JSON maneje tipos básicos
    return obj

# --- AUXILIAR DE DESERIALIZACIÓN ---

CLASES_MAPEO: dict[str, Any] = {
    'Tesoro': Tesoro,
    'Monstruo': Monstruo,
    'Jefe': Jefe,
    'EventoTeletransporte': EventoTeletransporte,
    'EventoCuracion': EventoCuracion,
    'EventoTrampa': EventoTrampa,
    'ContenidoHabitacion': ContenidoHabitacion,
    'Objeto': Objeto,
    'Habitacion': Habitacion,
    'Mapa': Mapa,
    'Explorador': Explorador,
}

def _diccionario_a_objeto(diccionario: dict) -> Any:
    """Convierte un diccionario con metadatos de clase de vuelta a un objeto."""
    if '__clase__' in diccionario:
        clase_nombre = diccionario['__clase__']
        data = diccionario['__data__']
        
        if clase_nombre in CLASES_MAPEO:
            clase = CLASES_MAPEO[clase_nombre]
            
            # Usamos object.__new__ para crear la instancia sin llamar al constructor (__init__)
            instance = object.__new__(clase)
            instance.__dict__.update(data)
            
            # Las instancias de Mapa, Explorador y Habitacion se procesan en cargar_partida
            if clase_nombre in ['Mapa', 'Explorador', 'Habitacion']:
                return {'__clase__': clase_nombre, '__data__': instance}
            
            return instance # Retorna el objeto reconstruido (Tesoro, Monstruo, Objeto, etc.)

    return diccionario

# --- GUARDAR Y CARGAR PARTIDA (REQ. 8) ---

def guardar_partida(mapa: Mapa, explorador: Explorador, archivo: str):
    """Guarda el estado completo del mapa y del explorador en JSON o YAML."""
    
    estado_juego = {
        'mapa': mapa,
        'explorador': explorador,
        'habitaciones': mapa.habitaciones # Guardamos las habitaciones completas aquí
    }

    if archivo.lower().endswith('.json'):
        with open(archivo, 'w') as f:
            json.dump(estado_juego, f, default=_objeto_a_diccionario, indent=4)
            
    elif archivo.lower().endswith('.yaml') or archivo.lower().endswith('.yml'):
        try:
            import yaml
            with open(archivo, 'w') as f:
                yaml.dump(estado_juego, f, default=_objeto_a_diccionario, sort_keys=False)
        except ImportError:
            print("[bold red]ADVERTENCIA:[/bold red] PyYAML no está instalado. No se puede guardar en YAML.")


# Tipado corregido, sin comillas simples
def cargar_partida(archivo: str) -> tuple[Mapa | None, Explorador | None]:
    """Carga una partida completa desde un archivo JSON o YAML."""
    
    data = None
    if archivo.lower().endswith('.json'):
        with open(archivo, 'r') as f:
            data = json.load(f, object_hook=_diccionario_a_objeto)
    
    elif archivo.lower().endswith('.yaml') or archivo.lower().endswith('.yml'):
        try:
            import yaml
            with open(archivo, 'r') as f:
                data = yaml.load(f, Loader=yaml.SafeLoader) 
        except ImportError:
            print("[bold red]ERROR:[/bold red] PyYAML no está instalado. No se puede cargar YAML.")
            return None, None
        except Exception as e:
            print(f"[bold red]ERROR:[/bold red] Error al cargar YAML: {e}")
            return None, None
            
    if not data or 'mapa' not in data or 'explorador' not in data or 'habitaciones' not in data:
        return None, None
--
    
    # 1. Obtener instancias reconstruidas (
    mapa = data['mapa']['__data__']
    explorador = data['explorador']['__data__']
    habitaciones_data = data['habitaciones']
    
    # 2. Reconstruir Habitaciones e Inventario
    habitaciones_instancias = {}
    for pos_str, hab_dict in habitaciones_data.items():
        pos_tuple = eval(pos_str) 
        hab = hab_dict['__data__']
        habitaciones_instancias[pos_tuple] = hab
    
    # 3. Asignar Referencias Circulares
    mapa.habitaciones = habitaciones_instancias
    
    # 4. Asignar Habitacion Inicial/Jefe al mapa (usan las referencias ya existentes)
    mapa.habitacion_inicial = habitaciones_instancias.get(mapa.habitacion_inicial_pos)
    mapa.habitacion_jefe = habitaciones_instancias.get(mapa.habitacion_jefe_pos)
    
    # 5. Reconstruir Conexiones entre Habitaciones (usando las instancias)
    for hab in habitaciones_instancias.values():
        conexiones_temp = {}
        for direccion, pos_adj in hab.conexiones.items():
            conexiones_temp[direccion] = habitaciones_instancias[pos_adj]
        hab.conexiones = conexiones_temp

    # 6. Reconstruir EventoTeletransporte (necesita la referencia del mapa)
    for hab in habitaciones_instancias.values():
         if isinstance(hab.contenido, EventoTeletransporte):
             hab.contenido.mapa = mapa


    # 7. Asignar la referencia del mapa al explorador
    explorador.mapa = mapa 

    return mapa, explorador

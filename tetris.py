import random

ANCHO_JUEGO, ALTO_JUEGO = 9, 18
IZQUIERDA, DERECHA = -1, 1
VACIO = ""
SUPERFICIE = "X"
CUBO = 0
Z = 1
S = 2
I = 3
L = 4
L_INV = 5
T = 6

PIEZAS = (
    ((0, 0), (1, 0), (0, 1), (1, 1)), # Cubo
    ((0, 0), (1, 0), (1, 1), (2, 1)), # Z (zig-zag)
    ((0, 0), (0, 1), (1, 1), (1, 2)), # S (-Z)
    ((0, 0), (0, 1), (0, 2), (0, 3)), # I (línea)
    ((0, 0), (0, 1), (0, 2), (1, 2)), # L
    ((0, 0), (1, 0), (2, 0), (2, 1)), # -L
    ((0, 0), (1, 0), (2, 0), (1, 1)), # T
)

def generar_pieza(pieza=None):
    """
    Genera una nueva pieza de entre PIEZAS al azar. Si se especifica el parámetro pieza
    se generará una pieza del tipo indicado. Los tipos de pieza posibles
    están dados por las constantes CUBO, Z, S, I, L, L_INV, T.

    El valor retornado es una tupla donde cada elemento es una posición
    ocupada por la pieza, ubicada en (0, 0). 
    """

    if pieza == None:
        pieza = random.randint(0,6) 

    return PIEZAS[pieza]

def trasladar_pieza(pieza, dx, dy):
    """
    Traslada la pieza de su posición actual a (posicion + (dx, dy)).

    La pieza está representada como una tupla de posiciones ocupadas,
    donde cada posición ocupada es una tupla (x, y). 
    Por ejemplo para la pieza ( (0, 0), (0, 1), (0, 2), (0, 3) ) y
    el desplazamiento dx=2, dy=3 se devolverá la pieza 
    ( (2, 3), (2, 4), (2, 5), (2, 6) ).
    """
    pieza_desplazada = [] 
    
    for i in pieza:
        x = i[0] + dx
        y = i[1] + dy
        pieza_desplazada.append((x,y))

    return tuple(pieza_desplazada)

def crear_juego(pieza_inicial):
    """
    Crea y devuelve un nuevo juego de Tetris el cual consta de una grilla (lista de listas) y una pieza_centrada (tupla de tuplas).
    El parámetro pieza_inicial es una pieza obtenida a través de generar_pieza.
    """
    
    pieza_centrada = trasladar_pieza(pieza_inicial, ANCHO_JUEGO // 2, 0) 
    grilla = crear_grilla_vacia() 

    return grilla, pieza_centrada

def crear_grilla_vacia():
    """
    Devuelve una grilla vacía a partir de las variables globales ANCHO_JUEGO y ALTO_JUEGO
    """
    grilla = []
    for y in range(ALTO_JUEGO):
        fila = []
        for x in range(ANCHO_JUEGO):
            fila.append(VACIO)
        grilla.append(fila)
    return grilla

def dimensiones(juego):
    """
    Devuelve las dimensiones de la grilla del juego como una tupla (ancho, alto).
    """
    return ANCHO_JUEGO, ALTO_JUEGO

def pieza_actual(juego):
    """
    Devuelve una tupla de tuplas (x, y) con todas las posiciones de la
    grilla ocupadas por la pieza actual.

    Se entiende por pieza actual a la pieza que está cayendo y todavía no
    fue consolidada con la superficie.
    """
    _, pieza = juego
    return pieza

def hay_superficie(juego, x, y):
    
    """
    Devuelve True si la celda (x, y) está ocupada por la superficie consolidada.
    
    La coordenada (0, 0) se refiere a la posición que está en la esquina 
    superior izquierda de la grilla.
    """
    grilla, _ = juego
    
    return grilla[y][x] == SUPERFICIE

def fuera_de_limites(coordenada):
    """
    Recibe una coordenada de la pieza en forma de tupla y devuelve en booleano si está fuera de los limites de la grilla o no
    """
    return coordenada[0] < 0 or coordenada[0] >= ANCHO_JUEGO or coordenada[1] >= ALTO_JUEGO

def mover(juego, direccion):
    """
    Mueve la pieza actual hacia la derecha o izquierda, si es posible.
    Devuelve un nuevo estado de juego con la pieza movida o el mismo estado 
    recibido si el movimiento no se puede realizar.

    El parámetro direccion debe ser una de las constantes DERECHA o IZQUIERDA.
    """
    grilla, pieza = juego
    pieza_desplazada = []

    for i in range(len(pieza)): #creo pieza desplazada
        pieza_desplazada.append((pieza[i][0] + direccion, pieza[i][1]))
        if fuera_de_limites(pieza_desplazada[i]) or hay_superficie(juego, pieza_desplazada[i][0], pieza_desplazada[i][1]):
            return juego
    juego = grilla, tuple(pieza_desplazada)    
    return juego

def avanzar(juego, siguiente_pieza):
    """
    Avanza al siguiente estado de juego a partir del estado actual.
    
    Devuelve una tupla (juego_nuevo, cambiar_pieza) donde el primer valor
    es el nuevo estado del juego y el segundo valor es un booleano que indica
    si se debe cambiar la siguiente_pieza (es decir, se consolidó la pieza
    actual con la superficie).
    
    Avanzar el estado del juego significa:
     - Descender una posición la pieza actual.
     - Si al descender la pieza no colisiona con la superficie, simplemente
       devolver el nuevo juego con la pieza en la nueva ubicación.
     - En caso contrario, se debe
       - Consolidar la pieza actual con la superficie.
       - Eliminar las líneas que se hayan completado.
       - Cambiar la pieza actual por siguiente_pieza.

    Si se debe agregar una nueva pieza, se utilizará la pieza indicada en
    el parámetro siguiente_pieza. El valor del parámetro es una pieza obtenida 
    llamando a generar_pieza().

    Si el juego está terminado (no se pueden agregar más piezas), la funcion no hace nada, 
    devuelve el mismo juego que se recibió.
    """
    grilla, pieza_actual = juego
    cambiar_pieza = False
    
    if terminado(juego):
        return juego, cambiar_pieza      
    
    pieza_descendida = trasladar_pieza(pieza_actual, 0, 1)  #Desciende la pieza en una posición
    
    for coordenada in pieza_descendida: #Valido la pieza descendida
        if fuera_de_limites(coordenada) or hay_superficie(juego, coordenada[0], coordenada[1]):
            grilla = eliminar_linea(consolidar_superficie(juego))  #Consolido pieza actual y elimino linea si es el caso
            cambiar_pieza = True
            siguiente_pieza = trasladar_pieza(siguiente_pieza, ANCHO_JUEGO // 2, 0) #Centro la siguiente_pieza
            return (grilla, siguiente_pieza), cambiar_pieza

    return (grilla, pieza_descendida), cambiar_pieza   #Pudo bajar sin problema

def consolidar_superficie(juego):
    """
    Consolida la superficie del estado de juego actual, es decir la pieza actual pasa a ser superficie.
    Devuelve la nueva grilla
    """
    grilla, pieza = juego
    for c in range(len(pieza)):
        grilla[pieza[c][1]][pieza[c][0]] = SUPERFICIE
    return grilla

def eliminar_linea(grilla):
    """
    Recibe una grilla y verifica si hay que eliminar lineas, en caso de que no devuelve la misma grilla
    """
    for y in range(ALTO_JUEGO): 
        if not VACIO in grilla[y]:   #En caso de no haber alguna coordenada vacía
            for f in range(y, 1, -1):    #Todas las filas (desde la llena hasta la segunda) copian a la de arriba
                grilla[f] = grilla[f-1].copy()  
            for x in range(len(grilla[0])): #Vacío la primera fila
                grilla[0][x] = VACIO        
    return grilla

def terminado(juego):
    """
    Devuelve True si el juego terminó, es decir no se pueden agregar
    nuevas piezas, o False si se puede seguir jugando.
    """
    grilla, pieza = juego
    for c in range(len(pieza)):
        if hay_superficie(juego, pieza[c][0], pieza[c][1]):
            return True
    return False
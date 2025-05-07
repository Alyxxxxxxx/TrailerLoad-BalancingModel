class Nodo:
    
    def __init__(self, identificador_nodo, coordenadas):
        self.identificador_nodo = identificador_nodo
        self.coordenadas_nodo = coordenadas
        self.montacargas_en_nodo = None
        self.conexiones_nodo = []
    
    def agregar_conexion(self, nodo):
        if nodo not in self.conexiones_nodo:
            self.conexiones_nodo.append(nodo)
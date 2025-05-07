from Nodo import *
import numpy 
from Utilidades import calculateCenter
from OpenGL.GL import *
import heapq

class Malla:
    def __init__(self, filas, columnas, dimension_malla):
        self.filas = filas
        self.columnas = columnas
        self.dimension_malla = dimension_malla
        self.ancho_casilla = (2* self.dimension_malla) / self.filas
        self.alto_casilla = (2 * self.dimension_malla) / self.columnas
        self.nodos = {}
        self.matriz_adyacencia =  numpy.zeros((self.filas * self.columnas, self.filas * self.columnas))
        
        self.generar_malla()
    
    def generar_malla(self):
        identificador_nodo = 0
        
        #Generar nodos en la malla
        for fila in range(self.filas):
            for columna in range(self.columnas):
                coordenadas_nodo_nuevo = calculateCenter(fila, columna, self.ancho_casilla, self.alto_casilla, self.dimension_malla)
                nodo_nuevo = Nodo(identificador_nodo, coordenadas_nodo_nuevo) 
                self.nodos[identificador_nodo] = nodo_nuevo
                identificador_nodo += 1
        
        #Crear matriz de adyacencia
        for fila in range(self.filas):
            for columna in range(self.columnas):
                identificador_nodo_actual = fila * self.columnas + columna
                nodo_actual = self.nodos[identificador_nodo_actual]
                
                if columna + 1 < self.columnas:
                    identificador_nodo_vecino = fila * self.columnas + (columna + 1)
                    self.matriz_adyacencia[identificador_nodo_actual, identificador_nodo_vecino] = 1
                    nodo_actual.agregar_conexion(self.nodos[identificador_nodo_vecino])
                    
                if columna - 1 >= 0:
                    identificador_nodo_vecino = fila * self.columnas + (columna - 1)
                    self.matriz_adyacencia[identificador_nodo_actual, identificador_nodo_vecino] = 1
                    nodo_actual.agregar_conexion(self.nodos[identificador_nodo_vecino])  
                    
                if fila + 1 < self.filas:
                    identificador_nodo_vecino = (fila + 1) * self.columnas + columna
                    self.matriz_adyacencia[identificador_nodo_actual, identificador_nodo_vecino] = 1
                    nodo_actual.agregar_conexion(self.nodos[identificador_nodo_vecino])

                if fila - 1 >= 0:
                    identificador_nodo_vecino = (fila - 1) * self.columnas + columna
                    self.matriz_adyacencia[identificador_nodo_actual, identificador_nodo_vecino] = 1
                    nodo_actual.agregar_conexion(self.nodos[identificador_nodo_vecino])
                    
    def renderizar_nodos(self, tamaño_punto = 5.0, color=(0.000, 0.808, 0.820)):
        glColor3fv(color)
        
        for nodo in self.nodos.values():
            x, y, z = nodo.coordenadas_nodo
            glPointSize(tamaño_punto)
            glBegin(GL_POINTS)
            glVertex3d(x, y, z)  
            glEnd()  
            
    def dijkstra(self, identificador_nodo_inicio, identificador_nodo_final):
        distancias = {nodo: float('inf') for nodo in self.nodos}
        distancias[identificador_nodo_inicio] = 0
        prev_nodos = {nodo: None for nodo in self.nodos}
        pq = [(0, identificador_nodo_inicio)]  

        while pq:
            current_dist, nodo_actual = heapq.heappop(pq)
            
            if nodo_actual == identificador_nodo_final:
                break

            for vecino in self.nodos[nodo_actual].conexiones_nodo:
                vecino_id = vecino.identificador_nodo
                dist = current_dist + 1  

                if dist < distancias[vecino_id]:
                    distancias[vecino_id] = dist
                    prev_nodos[vecino_id] = nodo_actual
                    heapq.heappush(pq, (dist, vecino_id))

        path = []
        nodo_actual = identificador_nodo_final
        while nodo_actual is not None:
            path.append(nodo_actual)
            nodo_actual = prev_nodos[nodo_actual]

        path.reverse()
        return path

    def encontrar_rutas_bidireccionales(self, identificador_nodo_inicio, identificador_nodo_final):
        camino_ida = self.dijkstra(identificador_nodo_inicio, identificador_nodo_final)
        nodos_bloqueados = set(camino_ida[1:-1]) 
        
        def dijkstra_revertido(identificador_nodo_inicio, identificador_nodo_final, nodos_bloqueados):
            distancias = {nodo: float('inf') for nodo in self.nodos}
            distancias[identificador_nodo_inicio] = 0
            prev_nodos = {nodo: None for nodo in self.nodos}
            pq = [(0, identificador_nodo_inicio)] 

            while pq:
                current_dist, nodo_actual = heapq.heappop(pq)
                
                if nodo_actual == identificador_nodo_final:
                    break
                
                for vecino in self.nodos[nodo_actual].conexiones_nodo:
                    vecino_id = vecino.identificador_nodo
                    if vecino_id in nodos_bloqueados: 
                        continue
                    dist = current_dist + 1 
                    
                    if dist < distancias[vecino_id]:
                        distancias[vecino_id] = dist
                        prev_nodos[vecino_id] = nodo_actual
                        heapq.heappush(pq, (dist, vecino_id))
                        
            path = []
            nodo_actual = identificador_nodo_final
            while nodo_actual is not None:
                path.append(nodo_actual)
                nodo_actual = prev_nodos[nodo_actual]
                
            path.reverse()
            return path
        
        camino_vuelta = dijkstra_revertido(identificador_nodo_final, identificador_nodo_inicio, nodos_bloqueados)
        return camino_ida, camino_vuelta

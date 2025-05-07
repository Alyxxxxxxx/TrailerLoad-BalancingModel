import numpy
from OpenGL.GL import *

def calculateCenter(fila, columna, ancho_casilla, alto_casilla, dimension_malla):
    x_centro = columna * ancho_casilla + ancho_casilla / 2
    z_centro = fila * alto_casilla + alto_casilla / 2
    
    x_centro = -dimension_malla + columna * ancho_casilla + ancho_casilla / 2
    z_centro = -dimension_malla + fila * alto_casilla + alto_casilla / 2
    
    coordenadas_centro = numpy.asarray([x_centro, 0, z_centro], dtype=numpy.float64)
    return tuple(coordenadas_centro)

def dibujar_cuadrado(coordenadas, square_size = 50.0):
    x, y, z = coordenadas
    
    glColor3f(0.275, 0.510, 0.706) 
    half_size = square_size / 2.0
    
    glBegin(GL_QUADS)

    glVertex3d(x - half_size, y, z - half_size)  
    glVertex3d(x - half_size, y, z + half_size) 
    glVertex3d(x + half_size, y, z + half_size)  
    glVertex3d(x + half_size, y, z - half_size)  
    glEnd()

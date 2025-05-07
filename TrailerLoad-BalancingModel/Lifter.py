import math, numpy
from pygame.locals import *
from Cubo import Cubo
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

montacargas = []

class Lifter:
	numero_cajas = None
	montacargas_creados = []

	def __init__(self, dim, vel, textures, idx, position, currentNode, ruta_ida, ruta_regreso, mapeo_nodos, distancia_montacargas, primer_montacargas, numero_cajas):
		Lifter.numero_cajas = numero_cajas
		self.dim = dim
		self.idx = idx
		self.Position = position
		self.nuevo_montacargas = True

		self.Direction = numpy.zeros(3)
		self.angle = 0
		self.vel = vel

		self.currentNode = currentNode
		self.nextNode = currentNode
		self.textures = textures

		#Distancia entre Montacargas
		self.distancia_montacargas = distancia_montacargas
		self.primer_montacargas = primer_montacargas

		#Rutas de Carga y Descarga de Cajas
		self.rutas = ruta_ida + ruta_regreso
		self.mapeo_nodos = mapeo_nodos 
		self.posicion_descarga = position

		self.distancia_ruta = self.calcular_distancia_total()

		#Control variables for platform movement
		self.platformHeight = -1.5
		self.platformUp = False
		self.platformDown = False

		#Control variable for collisions
		self.radiusCol = 5

		#Control variables for animations
		self.status = "searching"
		self.trashID = -1

	def search(self):
		# Change direction randomly
		u = numpy.random.rand(3)
		u[1] = 0
		u /= numpy.linalg.norm(u)
		self.Direction = u

	def calcular_max_lifters(self):
		max_lifters = int(self.distancia_ruta / self.distancia_montacargas) - 2
		return max_lifters

	def calcular_distancia_total(self):
		distancia_total = 0
		num_nodos = len(self.rutas)
        
		for i in range(num_nodos-1):
			nodo_actual = self.rutas[i]
			nodo_siguiente = self.rutas[i + 1] 
			coord_actual = numpy.array(self.mapeo_nodos[nodo_actual].coordenadas_nodo)
			coord_siguiente = numpy.array(self.mapeo_nodos[nodo_siguiente].coordenadas_nodo)
			distancia_total += numpy.linalg.norm(coord_actual - coord_siguiente)

		return distancia_total

	def calcular_distancia_recorrida(self):
		distancia_recorrida = 0
		for i in range(self.currentNode):
			nodo_actual = self.rutas[i]
			nodo_siguiente = self.rutas[i + 1]
			coord_actual = numpy.array(self.mapeo_nodos[nodo_actual].coordenadas_nodo)
			coord_siguiente = numpy.array(self.mapeo_nodos[nodo_siguiente].coordenadas_nodo)
			distancia_recorrida += numpy.linalg.norm(coord_actual - coord_siguiente)
		

		coord_actual = numpy.array(self.mapeo_nodos[self.rutas[self.currentNode]].coordenadas_nodo)
		distancia_recorrida += numpy.linalg.norm(coord_actual - self.Position) 
		return distancia_recorrida

	def calcular_progreso(self):
		distancia_recorrida = self.calcular_distancia_recorrida()
		progreso = distancia_recorrida / self.distancia_ruta  
		return progreso
    
	def crear_montacargas(self, montacargas_totales):
		global montacargas
		montacargas = montacargas_totales

		if not self.existe_colision() and self.se_puede_crear_montacarga(self):
			self.nuevo_montacargas = False
			Lifter.montacargas_creados.append(self)
			return True
		else:
			return False

	def es_ultimo_montacargas(self):
		if self.calcular_progreso() >= 0.8:
			return True

	def se_puede_crear_montacarga(self, montacarga):
		if len(self.montacargas_creados) < self.calcular_max_lifters() or not montacarga.nuevo_montacargas:
			return True
		else:
			return False

	def existe_colision(self):
		for otro_montacargas in montacargas:
			if otro_montacargas.idx != self.idx:
				distancia = numpy.linalg.norm(numpy.array(self.Position) - numpy.array(otro_montacargas.Position))
				montacarga_adelante = self.montacargas_adelante(otro_montacargas)
    
				if self.es_ultimo_montacargas():
					if distancia <= self.distancia_montacargas and montacarga_adelante and self.se_puede_crear_montacarga(otro_montacargas):
							return True 
				elif otro_montacargas.nextNode <= self.nextNode + 2: 
					if not self.nuevo_montacargas:
						if distancia <= self.distancia_montacargas and montacarga_adelante:
							return True  
					elif self.nuevo_montacargas:
						if distancia <= self.distancia_montacargas and montacarga_adelante:
							return True

		return False

	def montacargas_adelante(self, otro_montacargas):
		if otro_montacargas.calcular_progreso() > self.calcular_progreso():
			return True
		elif self.calcular_progreso() >= 0.8 and otro_montacargas.calcular_progreso() <= 0.05:
			return True

		return False

	def ComputeDirection(self, Posicion, NodoSiguiente):
		coordenadas_siguientes = self.mapeo_nodos[self.rutas[NodoSiguiente]].coordenadas_nodo
		Direccion = tuple(cs - p for cs, p in zip(coordenadas_siguientes, Posicion))
		Direccion = numpy.asarray(Direccion)
		Distancia = numpy.linalg.norm(Direccion)
		Direccion /= Distancia
		return Direccion, Distancia		

	def RetrieveNextNode(self, NodoActual):
		if NodoActual == len(self.rutas) - 1:
			return 0
		else:
			return NodoActual + 1

	def update(self, delta):
		self.nextNode = self.RetrieveNextNode(self.currentNode)
		Direccion, Distancia =  self.ComputeDirection(self.Position, self.nextNode)

		if Distancia < 1:
			self.currentNode = self.nextNode

		if not self.existe_colision():
			match self.status:
				case "searching":
					# Update position
					self.Position += Direccion * self.vel
					self.Direction = Direccion
					self.angle = math.acos(self.Direction[0]) * 180 / math.pi
					if self.Direction[2] > 0:
						self.angle = 360 - self.angle				

					# Move platform
					if self.platformUp:
						if self.platformHeight >= 0:
							self.platformUp = False
						else:
							self.platformHeight += delta
					elif self.platformDown:
						if self.platformHeight <= -1.5:
							self.platformUp = True
						else:
							self.platformHeight -= delta		
				case "lifting":
					if self.platformHeight >= 0:
						self.status = "delivering"
					else:
						self.platformHeight += delta
				case "delivering":
					tolerancia = 0.5

					if abs(self.Position[0] - self.posicion_descarga[0]) < tolerancia and abs(self.Position[2] - self.posicion_descarga[2]) < tolerancia:
						self.status = "dropping"
					else:
						self.Position += Direccion * self.vel
						self.Direction = Direccion
						self.angle = math.acos(self.Direction[0]) * 180 / math.pi
						if self.Direction[2] > 0:
							self.angle = 360 - self.angle	
				case "dropping":
					if self.platformHeight <= -1.5:
						Lifter.numero_cajas -= 1
						self.status = "searching"
					else:
						self.platformHeight -= delta
				case "returning":
					if (self.Position[0] <= 20 and self.Position[0] >= -20) and (self.Position[2] <= 20 and self.Position[2] >= -20):
						self.Position[0] -= (self.Direction[0] * (self.vel/4))
						self.Position[2] -= (self.Direction[2] * (self.vel/4))
					else:
						self.search()
						self.status = "searching"

	def draw(self):
		glPushMatrix()
		glTranslatef(self.Position[0], self.Position[1], self.Position[2])
		glRotatef(self.angle, 0, 1, 0)
		glScaled(7, 7, 7)
		glColor3f(1.0, 1.0, 1.0)
		# front face
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[2])
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, 1)

		# 2nd face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-2, -1, 1)

		# 3rd face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-2, -1, -1)

		# 4th face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, -1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, -1)

		# top
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, -1)
		glEnd()

		# Head

		glPushMatrix()
		glTranslatef(0, 1.5, 0)
		glScaled(0.8, 0.8, 0.8)
		glColor3f(1.0, 1.0, 1.0)
		head = Cubo(self.textures, 0)
		head.draw()
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)

		# Wheels
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[3])
		glPushMatrix()
		glTranslatef(-1.2, -1, 1)
		glScaled(0.3, 0.3, 0.3)
		glColor3f(1.0, 1.0, 1.0)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(0.5, -1, 1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(0.5, -1, -1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(-1.2, -1, -1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)

		# Lifter
		glPushMatrix()
		if self.status in ["lifting","delivering","dropping"]:
			self.drawTrash()
		glColor3f(0.0, 0.0, 0.0)
		glTranslatef(0, self.platformHeight, 0)  # Up and down
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(3, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(3, 1, 1)
		glEnd()
		glPopMatrix()
		glPopMatrix()

	def drawTrash(self):
		glPushMatrix()
		glTranslatef(2, (self.platformHeight + 1.5), 0)
		glScaled(0.5, 0.5, 0.5)
		glColor3f(1.0, 1.0, 1.0)

		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[1])

		glBegin(GL_QUADS)

		# Front face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-1, -1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, -1, 1)

		# Back face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, -1)

		# Left face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, 1)

		# Right face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, -1, -1)

		# Top face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, 1, -1)

		# Bottom face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, -1)

		glEnd()
		glDisable(GL_TEXTURE_2D)

		glPopMatrix()
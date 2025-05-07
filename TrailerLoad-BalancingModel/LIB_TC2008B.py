import yaml, pygame, glob, math
from Lifter import Lifter
from Caja import Caja
from Malla import Malla
from datetime import datetime
import csv
from Utilidades import dibujar_cuadrado

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

textures = []
lifters = []
cajas = []
delta = 0
posicion_cajas = None
posicion_montacargas = None

def loadSettingsYAML(File):
	class Settings: pass
	with open(File) as f:
		docs = yaml.load_all(f, Loader = yaml.FullLoader)
		for doc in docs:
			for k, v in doc.items():
				setattr(Settings, k, v)
	return Settings


Settings = loadSettingsYAML("Settings.yaml");	
malla = Malla(5, 5, Settings.DimBoard)

def Texturas(filepath):
    # Arreglo para el manejo de texturas
    global textures
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init(Options):
    global textures, cajas, lifters, malla, posicion_cajas, posicion_montacargas

    screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidencia 1: Alyson Melissa Sánchez Serratos")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(Settings.FOVY, Settings.screen_width/Settings.screen_height, Settings.ZNEAR, Settings.ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
    Settings.EYE_X,
    Settings.EYE_Y,
    Settings.EYE_Z,
    Settings.CENTER_X,
    Settings.CENTER_Y,
    Settings.CENTER_Z,
    Settings.UP_X,
    Settings.UP_Y,
    Settings.UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    for File in glob.glob(Settings.Materials + "*.*"):
        Texturas(File)
        
    mapeo_nodos = malla.nodos
    
    #Variables relacionadas con los Montacargas
    numero_montacargas = Options.Numero_de_Montacargas
    velocidad_montacargas = Options.Velocidad_de_Montacargas
    indice_nodo_zona_descarga = Options.Nodo_de_Zona_de_Descarga
    distancia_montacargas = Options.Distancia_Minima_entre_Montacargas
    
    nodo_zona_descarga = mapeo_nodos[indice_nodo_zona_descarga]
    posicion_montacargas = nodo_zona_descarga.coordenadas_nodo
    
    #Variables relacionadas con las Cajas
    numero_cajas = Options.Numero_de_Cajas
    indice_nodo_zona_cajas = Options.Nodo_de_Zona_de_Trailer
    
    nodo_zona_cajas = mapeo_nodos[indice_nodo_zona_cajas]
    posicion_cajas = nodo_zona_cajas.coordenadas_nodo
    
    ruta_ida, ruta_regreso = malla.encontrar_rutas_bidireccionales(indice_nodo_zona_descarga, indice_nodo_zona_cajas)
    primer_montacargas = None
    
    for i in range(numero_montacargas):
        if i == 0:
            primer_montacargas = True
        else:
            primer_montacargas = False
            
        lifters.append(Lifter(Settings.DimBoard, velocidad_montacargas, textures, i, posicion_montacargas, 0, ruta_ida, ruta_regreso, mapeo_nodos, distancia_montacargas, primer_montacargas, numero_cajas))

    for i in range(numero_cajas):
        # i es el identificador de la carga: sirve para realizar el inventario
        cajas.append(Caja(Settings.DimBoard,1,textures, 1, i, posicion_cajas))
    
    #Inicializar CSV
    if not os.path.exists("Reporte_A01771843.csv"):
        with open("Reporte_A01771843.csv", mode="a", newline="") as archivo:
            nombres_columnas = ["Identificador de Simulacion", "Numero de Agentes Deseados", "Numero de Agentes Creados", "Numero de Cajas", "Coordenada x de Zona de Descarga", "Coordenada y de Zona de Descarga", "Coordenada z de Zona de Descarga", "Coordenada x de Zona de Recoleccion", "Coordenada y de Zona de Recoleccion", "Coordenada z de Zona de Recoleccion", "Distancia Minima entre Agentes", "Tiempo Total de Simulacion"]
            escritor_csv = csv.DictWriter(archivo, fieldnames=nombres_columnas)
            escritor_csv.writeheader()
        
def renderizar_malla():
    global malla
    malla.renderizar_nodos()

def checkCollisions():
    for c in lifters:
        for b in cajas:
            distance = math.sqrt(math.pow((b.Position[0] - c.Position[0]), 2) + math.pow((b.Position[2] - c.Position[2]), 2))
            if distance <= c.radiusCol:
                if c.status == "searching" and b.alive:
                    b.alive = False
                    c.status = "lifting"

def display():
    global lifters, cajas, delta, posicion_cajas, posicion_montacargas
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #Se dibuja cubos
    for obj in lifters:
        if obj.nuevo_montacargas == True:
            if obj.crear_montacargas(lifters):
                obj.draw()
                obj.update(delta)
        else:
            obj.draw()
            obj.update(delta)
    
    #Se dibujan cajas
    for obj in cajas:
        obj.draw()

    dibujar_cuadrado(posicion_montacargas)
    dibujar_cuadrado(posicion_cajas)
    
    renderizar_malla()
    
    glColor3f(0.184, 0.310, 0.310)
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glEnd()
    
    # Draw the walls bounding the plane
    wall_height = 50.0  # Adjust the wall height as needed
    
    glColor3f(0.529, 0.808, 0.922)  
    
    # Draw the left wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()
    
    # Draw the right wall
    glBegin(GL_QUADS)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()
    
    # Draw the front wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, Settings.DimBoard)
    glEnd()
    
    # Draw the back wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()

    checkCollisions()
    
def lookAt(theta):
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = Settings.EYE_X * math.cos(rad) + Settings.EYE_Z * math.sin(rad)
    newZ = -Settings.EYE_X * math.sin(rad) + Settings.EYE_Z * math.cos(rad)
    gluLookAt(
    newX,
    Settings.EYE_Y,
    newZ,
    Settings.CENTER_X,
    Settings.CENTER_Y,
    Settings.CENTER_Z,
    Settings.UP_X,
    Settings.UP_Y,
    Settings.UP_Z)	

def generar_csv(identificador_simulacion, numero_agentes_deseados, numero_agentes_creados,numero_cajas, posicion_descarga, posicion_recoleccion, distancia_agentes, tiempo_total_simulacion):
    x_zona_descarga, y_zona_descarga, z_zona_descarga =  posicion_descarga
    x_zona_recoleccion, y_zona_recoleccion, z_zona_recoleccion = posicion_recoleccion
    
    datos = [{"Identificador de Simulacion": identificador_simulacion, "Numero de Agentes Deseados": numero_agentes_deseados, "Numero de Agentes Creados": numero_agentes_creados,"Numero de Cajas": numero_cajas, "Coordenada x de Zona de Descarga": x_zona_descarga, "Coordenada y de Zona de Descarga": y_zona_descarga,"Coordenada z de Zona de Descarga": z_zona_descarga ,"Coordenada x de Zona de Recoleccion": x_zona_recoleccion, "Coordenada y de Zona de Recoleccion": y_zona_recoleccion, "Coordenada z de Zona de Recoleccion":z_zona_recoleccion, "Distancia Minima entre Agentes": distancia_agentes, "Tiempo Total de Simulacion": tiempo_total_simulacion}]
    
    with open("Reporte_A01771843.csv", mode="a", newline="") as archivo:
        nombres_columnas = ["Identificador de Simulacion", "Numero de Agentes Deseados", "Numero de Agentes Creados", "Numero de Cajas", "Coordenada x de Zona de Descarga", "Coordenada y de Zona de Descarga", "Coordenada z de Zona de Descarga", "Coordenada x de Zona de Recoleccion", "Coordenada y de Zona de Recoleccion", "Coordenada z de Zona de Recoleccion", "Distancia Minima entre Agentes", "Tiempo Total de Simulacion"]
        escritor_csv = csv.DictWriter(archivo, fieldnames=nombres_columnas)
        escritor_csv.writerows(datos) 
    
def Simulacion(Options):
	# Variables para el control del observador
    tiempo_inicio = datetime.now()
    global delta
    theta = Options.theta
    delta = Options.Delta

    Init(Options)
    while True:
        if Lifter.numero_cajas == 0:
            tiempo_final = datetime.now()
            tiempo_total_simulacion = tiempo_final - tiempo_inicio
            print("Tiempo Total de Ejecucion:", tiempo_total_simulacion)
            generar_csv(Options.Identificador_de_Simulacion, Options.Numero_de_Montacargas, len(Lifter.montacargas_creados), Options.Numero_de_Cajas, posicion_montacargas, posicion_cajas, Options.Distancia_Minima_entre_Montacargas, tiempo_total_simulacion)
            exit()
            
        keys = pygame.key.get_pressed()  # Checking pressed keys
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                    pygame.quit()	
                    return
        if keys[pygame.K_RIGHT]:
            if theta > 359.0:
                theta = 0
            else:
                theta += 1.0
        lookAt(theta)
        if keys[pygame.K_LEFT]:
            if theta < 1.0:
                theta = 360.0
            else:
                theta -= 1.0
        lookAt(theta)
        display()
        display()
        pygame.display.flip()
        pygame.time.wait(10)



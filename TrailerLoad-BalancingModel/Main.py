import argparse, datetime, LIB_TC2008B

def main():
	parser = argparse.ArgumentParser("Evidencia 1 - A01771843", description = "Evidencia 1 - A01771843")
	subparsers = parser.add_subparsers()
	
	subparser = subparsers.add_parser("Simulacion",  description = "Corre simulacion")
	subparser.add_argument("--Identificador_de_Simulacion", required = True, type = int, help = "Numero de Simulacion a Ejecutar")
	subparser.add_argument("--Numero_de_Montacargas", required = True, type = int, help = "Numero de Montacargas")
	subparser.add_argument("--Velocidad_de_Montacargas", required = True, type = float, help = "Velocidad con la que un Montacargas se desplaza")
	subparser.add_argument("--Numero_de_Cajas", required = True, type = int, help = "Numero de cajas a Descargar")
	subparser.add_argument("--Nodo_de_Zona_de_Descarga", required = True, type = int, help = "Nodo donde se localizará la Zona de Descarga")
	subparser.add_argument("--Nodo_de_Zona_de_Trailer", required = True, type = int, help = "Nodo donde se localizará el Trailer con las Cajas por Descargar")	
	subparser.add_argument("--Distancia_Minima_entre_Montacargas", required = True, type = int, help = "Espacio que debe haber entre los Montacargas para evitar colisiones o interferencias durante su operación")
	subparser.add_argument("--Delta", required = False, type = float, default = 0.05, help = "")
	subparser.add_argument("--theta", required = False, type = float, default = 0, help = "")
	subparser.set_defaults(func = LIB_TC2008B.Simulacion)
	
	Options = parser.parse_args()
	
	print(str(Options) + "\n")

	Options.func(Options)


if __name__ == "__main__":
	print("\n" + "\033[0;32m" + "[start] " + str(datetime.datetime.now()) + "\033[0m" + "\n")
	print("Estudiante: Alyson Melissa Sánchez Serratos")
	print("Matricula de Estudiante: A01771843")
	print("Profesor: Roberto Marcial Leyva Fernández")
	print("Asignación: Evidencia 1. Actividad Integradora")
	main()
	print("\n" + "\033[0;32m" + "[end] "+ str(datetime.datetime.now()) + "\033[0m" + "\n")




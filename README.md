# TrailerLoad-BalancingModel
Python-based multi-agent simulation to optimize forklift usage for trailer unloading, minimizing time and congestion. Uses OpenGL/Pygame for visualization, NumPy for calculations, and outputs CSV results with an analytical forklift optimization model.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Methodology and Scope](#methodology-and-scope)
4. [Simulation Model](#simulation-model)
   - [Model Description](#model-description)
   - [Forklift Movement](#forklift-movement)
   - [Route Generation with Dijkstra’s Algorithm](#route-generation-with-dijkstras-algorithm)
   - [Forklift Interactions and Minimum Distance](#forklift-interactions-and-minimum-distance)
   - [Automatic Forklift Number Adjustment](#automatic-forklift-number-adjustment)
   - [CSV Results File](#csv-results-file)
5. [Code Structure](#code-structure)
   - [Command-Line Interface](#command-line-interface)
   - [Lifter Class](#lifter-class)
   - [Simulation Initialization and Rendering](#simulation-initialization-and-rendering)
   - [Grid and Pathfinding](#grid-and-pathfinding)
   - [Configuration Settings](#configuration-settings)
6. [Installation and Usage](#installation-and-usage)
   - [Prerequisites](#prerequisites)
   - [Setup](#setup)
   - [Running the Simulation](#running-the-simulation)
   - [Output](#output)
7. [Results](#results)
8. [License](#license)
9. [Credits](#credits)

## Project Overview
This project develops a sophisticated simulation to determine the optimal number of forklifts required to efficiently unload a trailer. The optimal number is defined as the point where adding more forklifts no longer reduces unloading time by more than 25% or causes congestion due to excessive interactions. The simulation also evaluates the impact of the distance between the loading and unloading zones on efficiency, aiming to identify an optimal distance that minimizes unloading time while maintaining compatibility with the forklift count.

## Problem Statement
The simulation models a scenario where a trailer is unloaded by a variable number of forklifts, governed by the following parameters:
- Number of boxes to be unloaded.
- Number of available forklifts.
- Forklift speed and minimum inter-forklift distance.
- Nodes representing the trailer (loading zone) and unloading zone within a 5x5 grid.

### Key Constraints
1. Only one forklift can unload a box at a time.
2. Forklifts must maintain a minimum distance to prevent collisions.

The objective is to identify the ideal number of forklifts that maximizes unloading efficiency without causing diminishing returns or system overload.

## Methodology and Scope
A multi-agent system is employed, with each forklift modeled as an autonomous agent interacting within a simulated environment. The implementation leverages Python, utilizing specialized libraries:
- **OpenGL** and **Pygame**: For rendering a graphical representation of the simulation plane and forklift movements.
- **NumPy**: For efficient numerical computations, including distances, speeds, and movement times.
- **YAML**: For configuration management.

Multiple simulation runs systematically vary the number of forklifts and the distance between loading and unloading zones to analyze their impact on efficiency. Results are exported to a CSV file, and an analytical expression is derived to calculate the optimal forklift count based on input parameters.

## Simulation Model

### Model Description
The model simulates the unloading process on a 5x5 grid, where each cell represents a node. The trailer (loading zone) and unloading zone are assigned to specific nodes. Forklifts navigate between these zones along dynamically generated routes, adhering to collision-avoidance protocols.

### Forklift Movement
Forklift movement is computed using the **Dijkstra algorithm** to determine the shortest path between nodes. Two distinct routes are defined:
1. **Outbound Route**: From the unloading zone to the trailer.
2. **Return Route**: From the trailer to the unloading zone.

These routes are separated to prevent collisions, with movement logic designed to avoid mutual blocking.

### Route Generation with Dijkstra’s Algorithm
The Dijkstra algorithm operates on an adjacency matrix representing connections in the 5x5 grid. Each node connects to its immediate neighbors (up, down, left, right), with a matrix value of 1 indicating a direct connection and 0 otherwise. This matrix facilitates efficient pathfinding between the trailer and unloading zone.

### Forklift Interactions and Minimum Distance
Forklifts maintain a minimum distance to ensure safe operations. If the distance between two forklifts falls below the threshold, the trailing forklift pauses until sufficient space is available. The Euclidean distance is calculated using `numpy.linalg.norm`:

```
d = √((x₂ - x₁)² + (y₂ - y₁)²)
```

Separated outbound and return routes further minimize collision risks.

### Automatic Forklift Number Adjustment
If the requested number of forklifts or specified minimum distance is incompatible with the simulation plane, the system adjusts the forklift count using the `calcular_max_lifters()` method in the `Lifter` class. This method calculates the maximum feasible number of forklifts by dividing the total route distance by the minimum inter-forklift distance, ensuring compliance with spatial and operational constraints.

### CSV Results File
The simulation generates a CSV file (`Reporte_A01771843.csv`) with the following columns:
1. **Simulation ID**: Unique identifier for each run.
2. **Desired Agents**: User-requested number of forklifts.
3. **Created Agents**: Number of forklifts generated, adjusted for constraints.
4. **Number of Boxes**: Total boxes to unload.
5. **Unloading Zone X/Y/Z**: Coordinates of the unloading zone.
6. **Loading Zone X/Y/Z**: Coordinates of the trailer.
7. **Minimum Distance Between Agents**: Required minimum distance between forklifts.
8. **Total Simulation Time**: Duration of the simulation (hours, minutes, seconds, microseconds).

## Code Structure

### Command-Line Interface
The simulation is configured via a command-line interface using the `argparse` module. The main script accepts the following arguments:

```python
parser = argparse.ArgumentParser("Evidencia 1 - A01771843", description="Evidencia 1 - A01771843")
subparser = subparsers.add_parser("Simulacion", description="Corre simulacion")
subparser.add_argument("--Identificador_de_Simulacion", required=True, type=int, help="Numero de Simulacion a Ejecutar")
subparser.add_argument("--Numero_de_Montacargas", required=True, type=int, help="Numero de Montacargas")
subparser.add_argument("--Velocidad_de_Montacargas", required=True, type=float, help="Velocidad con la que un Montacargas se desplaza")
subparser.add_argument("--Numero_de_Cajas", required=True, type=int, help="Numero de cajas a Descargar")
subparser.add_argument("--Nodo_de_Zona_de_Descarga", required=True, type=int, help="Nodo donde se localizará la Zona de Descarga")
subparser.add_argument("--Nodo_de_Zona_de_Trailer", required=True, type=int, help="Nodo donde se localizará el Trailer con las Cajas por Descargar")
subparser.add_argument("--Distancia_Minima_entre_Montacargas", required=True, type=int, help="Espacio que debe haber entre los Montacargas para evitar colisiones o interferencias durante su operación")
subparser.add_argument("--Delta", required=False, type=float, default=0.05, help="")
subparser.add_argument("--theta", required=False, type=float, default=0, help="")
```

The script outputs simulation metadata, including student and assignment details, and logs the start and end times.

### Lifter Class
The `Lifter` class represents a forklift agent, managing its movement, collision detection, and box handling. Key methods include:
- `calcular_max_lifters()`: Determines the maximum number of forklifts based on route distance and minimum distance.
- `calcular_distancia_total()`: Computes the total route distance using Euclidean distances between nodes.
- `existe_colision()`: Checks for collisions by comparing forklift positions.
- `update()`: Updates forklift position and state (searching, lifting, delivering, dropping, returning).
- `draw()`: Renders the forklift and its cargo using OpenGL with textured 3D models.

### Simulation Initialization and Rendering
The `Init` function sets up the Pygame and OpenGL environment, loads textures, initializes forklifts and boxes, and configures the grid. The `display` function renders the scene, including:
- Forklifts and boxes.
- The 5x5 grid with nodes and connections.
- Colored squares marking the loading and unloading zones.
- A bounded plane with walls to visualize the simulation space.

The `checkCollisions` function detects when a forklift reaches a box, triggering the lifting state.

### Grid and Pathfinding
The `Malla` class manages the 5x5 grid and pathfinding:
- `generar_malla()`: Creates nodes and the adjacency matrix.
- `dijkstra()`: Implements Dijkstra’s algorithm for shortest-path calculation.
- `encontrar_rutas_bidireccionales()`: Generates separate outbound and return routes, avoiding node overlaps.

The `Nodo` class represents grid nodes, storing coordinates and connections.

### Configuration Settings
Simulation parameters are loaded from a `Settings.yaml` file, defining:
- Screen dimensions (`screen_width`, `screen_height`).
- Camera settings (`FOVY`, `ZNEAR`, `ZFAR`, `EYE_X/Y/Z`, etc.).
- Plane dimensions (`DimBoard`).
- Material paths for textures.

Example `Settings.yaml`:
```yaml
Materials: ./Materials/
screen_width: 1100
screen_height: 800
FOVY: 60.0
ZNEAR: 0.01
ZFAR: 1800.0
EYE_X: -150.0
EYE_Y: 400.0
EYE_Z: 200.0
CENTER_X: 0
CENTER_Y: 0
CENTER_Z: 0
UP_X: 0
UP_Y: 1
UP_Z: 0
DimBoard: 400
```

## Installation and Usage

### Prerequisites
- Python 3.8 or higher
- Required libraries: `numpy`, `pygame`, `pyopengl`, `pyyaml`

### Setup
Install dependencies:
```bash
pip install numpy pygame pyopengl pyyaml
```

Ensure the `Materials` directory contains texture files and `Settings.yaml` is configured.

### Running the Simulation
Run the simulation with command-line arguments, e.g.:
```bash
python main.py Simulacion --Identificador_de_Simulacion 1 --Numero_de_Montacargas 3 --Velocidad_de_Montacargas 2.0 --Numero_de_Cajas 10 --Nodo_de_Zona_de_Descarga 0 --Nodo_de_Zona_de_Trailer 24 --Distancia_Minima_entre_Montacargas 10
```

### Output
- A graphical simulation is displayed using Pygame and OpenGL, showing forklifts, boxes, and the grid.
- Results are saved in `Reporte_A01771843.csv` for analysis.
- Console output includes simulation metadata and total execution time.

  https://github.com/user-attachments/assets/e89996e6-9fbc-4689-8c9a-d953e8bba11d

## Results
The simulation provides insights into the optimal number of forklifts and the ideal distance between loading and unloading zones to minimize unloading time while avoiding congestion. An analytical expression is derived to calculate the optimal forklift count, enabling scalable application of the findings.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits
- **Author**: Alyson Melissa Sánchez Serratos
- **Student ID**: A01771843
- **Instructor**: Roberto Marcial Leyva Fernández
- **Assignment**: Evidencia 1 - Actividad Integradora

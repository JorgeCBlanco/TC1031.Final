# dijkstra.py
"""
Implementación de Dijkstra
Autores: Jorge Cardenas Blanco, Juan Carlos Arevalo Gomez, Juan Pablo Hernandez Lopez, Luis Fernando Kunze
ENLACE AL VIDEO DE YT: https://youtu.be/HzqYDuXLy5c
ENLACE AL DOCUMENTO: https://drive.google.com/file/d/17SoQMrOlcHMU8OUXDvoWQsCGurwhqOs6/view?usp=drive_link
UF: Estructura de Datos y Algoritmos fundamentales.
"""
import time
import os
import heapq
import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, names, pos=None):
        self.names = names
        self.n = len(names)
        self.adj = {i: [] for i in range(self.n)}
        self.dist = [float('inf')] * self.n
        self.parent = [-1] * self.n
        self.G = nx.Graph()
        for i, name in enumerate(names):
            self.G.add_node(i, label=name)

        # posiciones para dibujo (si no se dan, se crea en círculo)
        if pos is None:
            self.pos = {i: (2 * (i % 5), -1.5 * (i // 5)) for i in range(self.n)}
        else:
            self.pos = pos

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(12, 9))

    def add_edge(self, u, v, w):
        # agregar arista en ambas direcciones
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))
        self.G.add_edge(u, v, weight=w)

    def print_graph(self):
        print("\nGrafo (lista de adyacencia):\n")
        for u in range(self.n):
            print(f"{u} - {self.names[u]}")
            for v, w in self.adj[u]:
                print(f"   -> {v} - {self.names[v]} [{w} m]")
            print()

    def _node_display_labels(self, distances, visited):
        # devuelve etiquetas con nombre y distancia para cada nodo
        labels = {}
        for i in range(self.n):
            d = distances[i]
            if d == float('inf'):
                dstr = "INF"
            else:
                dstr = f"{int(d)} m"
            # etiqueta en dos líneas: índice/nombre y distancia
            labels[i] = f"{i} {self.names[i].split()[0]}\n{dstr}"
        return labels

    def draw(self, distances=None, visited=None, current=None, path_edges=None, title_extra=""):
        # dibuja el grafo con colores según el estado
        if distances is None:
            distances = [float('inf')] * self.n
        if visited is None:
            visited = [False] * self.n
        if path_edges is None:
            path_edges = []

        self.ax.clear()

        # colores para los nodos
        node_colors = []
        for i in range(self.n):
            if current is not None and i == current:
                node_colors.append("red")
            elif (i in path_nodes(path_edges)) and path_edges:
                node_colors.append("blue")
            elif visited[i]:
                node_colors.append("lightgreen")
            else:
                node_colors.append("lightgray")

        # colores y grosores para las aristas
        edge_colors = []
        edge_widths = []
        for u, v in self.G.edges():
            if (u, v) in path_edges or (v, u) in path_edges:
                edge_colors.append("blue")
                edge_widths.append(3.0)
            else:
                edge_colors.append("gray")
                edge_widths.append(1.0)

        # dibujar aristas y nodos
        nx.draw_networkx_edges(self.G, pos=self.pos, ax=self.ax, edge_color=edge_colors, width=edge_widths)
        nx.draw_networkx_nodes(self.G, pos=self.pos, ax=self.ax, node_color=node_colors, node_size=900)
        # etiquetas (nombre corto + distancia)
        labels = self._node_display_labels(distances, visited)
        nx.draw_networkx_labels(self.G, pos=self.pos, labels=labels, ax=self.ax, font_size=8, font_weight='bold')

        # pesos de las aristas
        edge_labels = nx.get_edge_attributes(self.G, "weight")
        edge_labels = {(u, v): f"{w}m" for (u, v), w in edge_labels.items()}
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, ax=self.ax, font_size=8)

        # leyenda
        legend_text = []
        legend_text.append("Rojo = nodo actual")
        legend_text.append("Verde claro = visitado")
        legend_text.append("Azul = camino final resaltado")
        self.ax.set_title("Grafo de Guadalajara " + title_extra, fontsize=14)
        self.ax.axis("off")
        # cuadro de leyenda
        self.ax.text(1.02, 0.95, "\n".join(legend_text), transform=self.ax.transAxes, fontsize=9,
                     verticalalignment='top', bbox=dict(boxstyle="round", fc="wheat", ec="0.5", alpha=0.9))

        self.fig.canvas.draw()
        plt.pause(0.01)

    def dijkstra(self, start, animate_steps=True, step_delay=0.7):
        # inicializar distancias y padres
        self.dist = [float('inf')] * self.n
        self.parent = [-1] * self.n
        self.dist[start] = 0

        pq = [(0, start)]
        visited = [False] * self.n

        # guardar estados para animar
        snapshots = []
        snapshots.append((self.dist.copy(), visited.copy(), start))

        while pq:
            d, u = heapq.heappop(pq)
            if visited[u]:
                continue
            # descartar entradas obsoletas de la cola
            if d != self.dist[u]:
                continue
            visited[u] = True

            # revisar vecinos
            for v, w in self.adj[u]:
                if self.dist[u] + w < self.dist[v]:
                    self.dist[v] = self.dist[u] + w
                    self.parent[v] = u
                    heapq.heappush(pq, (self.dist[v], v))

            # guardar estado actual
            snapshots.append((self.dist.copy(), visited.copy(), u))

        # mostrar animación paso a paso
        if animate_steps:
            for dist_s, vis_s, cur_s in snapshots:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"Dijkstra desde: {self.names[start]}\n")
                if cur_s is not None:
                    print(f"Nodo actual: {cur_s} - {self.names[cur_s]}\n")
                print("Distancias actuales:")
                for i in range(self.n):
                    val = "INF" if dist_s[i] == float('inf') else f"{int(dist_s[i])} m"
                    mark = " [visitado]" if vis_s[i] else ""
                    print(f" {i} - {self.names[i]}: {val}{mark}")
                print()
                self.draw(distances=dist_s, visited=vis_s, current=cur_s, title_extra=f"(inicio en {self.names[start]})")
                time.sleep(step_delay)

        # dibujar resultado final
        self.draw(distances=self.dist, visited=[True]*self.n, current=None, title_extra=f"(terminado desde {self.names[start]})")
        print("\nDistancias finales:")
        for i in range(self.n):
            val = "no alcanzable" if self.dist[i] == float('inf') else f"{int(self.dist[i])} m"
            print(f" - {self.names[i]}: {val}")
        print()

    def print_shortest_path(self, dest, show_animation=True):
        # verificar si hay camino
        if self.dist[dest] == float('inf'):
            print("No hay camino.\n")
            return

        # reconstruir el camino
        path = []
        cur = dest
        while cur != -1:
            path.append(cur)
            cur = self.parent[cur]
        path.reverse()

        print(f"Camino más corto hacia {self.names[dest]}:")
        print(" -> ".join(self.names[i] for i in path))
        print(f"Distancia total: {int(self.dist[dest])} m\n")

        # obtener aristas del camino
        path_edges = []
        for i in range(len(path) - 1):
            path_edges.append((path[i], path[i + 1]))

        # animar el camino
        if show_animation:
            # primero mostrar todo el grafo
            self.draw(distances=self.dist, visited=[True]*self.n, path_edges=path_edges,
                      title_extra=f"(camino a {self.names[dest]})")
            # resaltar cada arista del camino
            for i in range(len(path_edges)):
                partial = path_edges[:i+1]
                self.draw(distances=self.dist, visited=[True]*self.n, path_edges=partial,
                          title_extra=f"(camino a {self.names[dest]})")
                time.sleep(0.7)
        else:
            self.draw(distances=self.dist, visited=[True]*self.n, path_edges=path_edges,
                      title_extra=f"(camino a {self.names[dest]})")
            time.sleep(1.2)

def path_nodes(edge_list):
    # obtener nodos únicos de una lista de aristas
    s = set()
    for u, v in edge_list:
        s.add(u)
        s.add(v)
    return s

if __name__ == "__main__":
    # definir ubicaciones de Guadalajara
    names = [
        "Catedral de Guadalajara",            #0
        "Plaza de Armas",                     #1
        "Mercado San Juan de Dios",           #2
        "Teatro Degollado",                   #3
        "Hospicio Cabañas",                   #4
        "Parque Agua Azul",                   #5
        "Parque Revolución",                  #6
        "Bosque Los Colomos",                 #7
        "Estación Juárez",                    #8
        "Glorieta Minerva",                   #9
        "Expiatorio",                         #10
        "Andares",                            #11
        "Zapopan Centro",                     #12
        "Plaza Patria",                       #13
        "Universidad de Guadalajara",         #14
    ]

    # coordenadas para el dibujo
    pos = {
        0: (3.5, 3.0),
        1: (3.5, 2.2),
        2: (4.5, 1.5),
        3: (2.5, 2.6),
        4: (1.0, 2.8),
        5: (4.0, 0.2),
        6: (2.0, 1.0),
        7: (0.0, 3.8),
        8: (5.8, 2.6),
        9: (6.2, 1.5),
        10: (1.0, 1.7),
        11: (7.5, 0.8),
        12: (8.2, 2.8),
        13: (6.5, 2.8),
        14: (2.0, -0.2),
    }

    g = Graph(names, pos=pos)

    # conexiones entre ubicaciones (distancia en metros)
    edges = [
        (0, 1, 180),
        (0, 3, 260),
        (1, 2, 450),
        (1, 9, 1200),
        (2, 8, 900),
        (3, 4, 600),
        (3, 6, 700),
        (4, 7, 1500),
        (4, 10, 900),
        (5, 6, 500),
        (5, 11, 3400),
        (6, 10, 400),
        (6, 14, 1100),
        (7, 12, 4200),
        (8, 9, 600),
        (9, 11, 1400),
        (11, 12, 800),
        (12, 13, 900),
        (13, 9, 1000),
        (10, 14, 600),
        (2, 5, 1600),
        (1, 3, 330),
        (0, 2, 700),
        (12, 11, 800),
    ]

    for u, v, w in edges:
        g.add_edge(u, v, w)

    print("Nodos del grafo:")
    for i, n in enumerate(names):
        print(f"{i} -> {n}")
    print()

    g.print_graph()

    # pedir nodo de inicio
    while True:
        try:
            start = int(input(f"Selecciona nodo origen (0-{g.n - 1}): "))
            if 0 <= start < g.n:
                break
        except Exception:
            pass
        print("Entrada inválida. Intenta de nuevo.")

    print()
    # ejecutar Dijkstra
    g.dijkstra(start, animate_steps=True, step_delay=0.6)

    # consultar caminos específicos
    while True:
        try:
            dest = int(input(f"Destino (0-{g.n - 1}, -1 para salir): "))
        except Exception:
            print("Entrada inválida.")
            continue
        if dest == -1:
            break
        if 0 <= dest < g.n:
            g.print_shortest_path(dest, show_animation=True)
        else:
            print("Destino fuera de rango.")

    plt.ioff()
#RoundRobin.py
"""
Balanceador de carga: Round Robin
Autores: Jorge Cardenas Blanco, Juan Carlos Arevalo Gomez, Juan Pablo Hernandez Lopez, Luis Fernando Kunze
ENLACE AL VIDEO DE YT: https://youtu.be/J5jFKc-k4mw
ENLACE AL DOCUMENTO: https://drive.google.com/file/d/1PRpTfHEriegFlfSh2ikupNdjuNdkAtm2/view?usp=drive_link
UF: Estructura de Datos y Algoritmos fundamentales.
"""
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys

class Node:
    def __init__(self, server_name):
        self.server_name = server_name
        self.requests_handled = 0
        self.next = None

class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_server(self, server_name):
        # crear nuevo nodo para el servidor
        new_node = Node(server_name)
        
        if self.head is None:
            self.head = new_node
            new_node.next = new_node
            self.current = self.head
        else:
            # insertar al final y mantener la circularidad
            temp = self.head
            while temp.next != self.head:
                temp = temp.next
            temp.next = new_node
            new_node.next = self.head
        
        self.size += 1

    def get_next_server(self):
        # obtener el servidor actual y avanzar al siguiente
        if self.current is None:
            return None
        
        server = self.current
        self.current = self.current.next
        return server

    def get_all_servers(self):
        # retornar lista con todos los servidores
        if self.head is None:
            return []
        
        servers = []
        temp = self.head
        while True:
            servers.append(temp)
            temp = temp.next
            if temp == self.head:
                break
        return servers

class LoadBalancer:
    def __init__(self, num_servers):
        self.servers = CircularLinkedList()
        self.request_history = []
        self.total_requests = 0
        
        # inicializar servidores
        for i in range(num_servers):
            self.servers.add_server(f"Servidor-{i+1}")

    def process_request(self, request_id):
        # asignar request al siguiente servidor disponible
        server = self.servers.get_next_server()
        server.requests_handled += 1
        self.total_requests += 1
        
        # guardar en historial
        self.request_history.append({
            'request_id': request_id,
            'server': server.server_name,
            'timestamp': time.time()
        })
        
        return server.server_name

    def get_statistics(self):
        # obtener estadísticas de carga
        servers = self.servers.get_all_servers()
        stats = []
        
        for server in servers:
            percentage = (server.requests_handled / self.total_requests * 100) if self.total_requests > 0 else 0
            stats.append({
                'name': server.server_name,
                'requests': server.requests_handled,
                'percentage': percentage
            })
        
        return stats

    def print_statistics(self):
        # mostrar estadísticas en consola
        print("\n" + "=" * 60)
        print("ESTADÍSTICAS DEL BALANCEADOR DE CARGA")
        print("=" * 60)
        print(f"\nTotal de solicitudes procesadas: {self.total_requests}")
        print(f"Número de servidores: {self.servers.size}\n")
        
        stats = self.get_statistics()
        
        print(f"{'Servidor':<20} {'Requests':<15} {'Porcentaje':<15}")
        print("-" * 60)
        
        for stat in stats:
            print(f"{stat['name']:<20} {stat['requests']:<15} {stat['percentage']:.2f}%")
        
        print("=" * 60 + "\n")

    def visualize_distribution_static(self):
        # gráfica de barras con la distribución final
        stats = self.get_statistics()
        
        names = [s['name'] for s in stats]
        requests = [s['requests'] for s in stats]
        
        plt.figure(figsize=(14, 7))
        
        # generar suficientes colores para cualquier número de servidores
        colors = plt.cm.Set3(range(len(names)))
        bars = plt.bar(names, requests, color=colors, edgecolor='black', linewidth=1.5)
        
        # añadir valores encima de las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xlabel('Servidores', fontsize=12, fontweight='bold')
        plt.ylabel('Número de Solicitudes', fontsize=12, fontweight='bold')
        plt.title(f'Distribución de Carga - Round Robin\n(Total: {self.total_requests} requests)', 
                 fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        return plt

class LoadBalancerAnimated:
    def __init__(self, num_servers, num_requests):
        self.num_servers = num_servers
        self.num_requests = num_requests
        self.servers = CircularLinkedList()
        self.current_request = 0
        
        # inicializar servidores
        for i in range(num_servers):
            self.servers.add_server(f"S{i+1}")
        
        # datos para la visualización
        self.server_list = self.servers.get_all_servers()
        self.server_names = [s.server_name for s in self.server_list]
        self.requests_data = [0] * num_servers
        
        # optimización: actualizar solo cada N frames
        if num_requests > 1000:
            self.update_every = max(1, num_requests // 200)  # máximo 200 frames
        elif num_requests > 500:
            self.update_every = max(1, num_requests // 150)
        else:
            self.update_every = 1
        
        # calcular cuántos frames realmente vamos a mostrar
        self.total_frames = (num_requests + self.update_every - 1) // self.update_every
        
        # historial para gráfica de líneas (solo guardar puntos que se muestran)
        self.history_x = []
        self.history_y = {name: [] for name in self.server_names}
        
        # configurar colores dinámicamente
        self.colors = plt.cm.tab20(range(num_servers))
        
        # configurar la figura
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(16, 7))
        self.fig.suptitle(f'Balanceador de Carga - Round Robin (Actualizando cada {self.update_every} requests)', 
                         fontsize=16, fontweight='bold')

    def animate_frame(self, frame):
        # procesar varios requests a la vez para acelerar
        requests_to_process = min(self.update_every, self.num_requests - self.current_request)
        
        for _ in range(requests_to_process):
            if self.current_request >= self.num_requests:
                break
            server = self.servers.get_next_server()
            server.requests_handled += 1
            self.current_request += 1
        
        # actualizar datos
        for idx, s in enumerate(self.server_list):
            self.requests_data[idx] = s.requests_handled
        
        # actualizar gráfica de barras
        self.ax1.clear()
        bars = self.ax1.bar(self.server_names, self.requests_data, 
                           color=self.colors, edgecolor='black', linewidth=1.5)
        
        # valores encima de barras
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        self.ax1.set_xlabel('Servidores', fontsize=11, fontweight='bold')
        self.ax1.set_ylabel('Requests', fontsize=11, fontweight='bold')
        self.ax1.set_title(f'\nRequest #{self.current_request}/{self.num_requests}', 
                          fontsize=12, fontweight='bold')
        max_val = max(self.requests_data) if self.requests_data else 1
        self.ax1.set_ylim(0, max_val + max(5, max_val * 0.1))
        self.ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # rotar etiquetas solo si hay muchos servidores
        if self.num_servers > 8:
            plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # actualizar historial para gráfica de líneas
        self.history_x.append(self.current_request)
        for idx, name in enumerate(self.server_names):
            self.history_y[name].append(self.requests_data[idx])
        
        # actualizar gráfica de líneas
        self.ax2.clear()
        for idx, name in enumerate(self.server_names):
            # no mostrar marcadores si hay muchos puntos
            show_markers = len(self.history_x) <= 50
            self.ax2.plot(self.history_x, self.history_y[name], 
                         marker='o' if show_markers else '', 
                         label=name, color=self.colors[idx], 
                         linewidth=2, markersize=4)
        
        self.ax2.set_xlabel('Número de Request', fontsize=11, fontweight='bold')
        self.ax2.set_ylabel('Requests Acumulados', fontsize=11, fontweight='bold')
        self.ax2.set_title('Evolución de Carga por Servidor', fontsize=12, fontweight='bold')
        
        # ajustar leyenda según el número de servidores
        if self.num_servers <= 12:
            self.ax2.legend(loc='upper left', fontsize=9, ncol=1)
        else:
            self.ax2.legend(loc='upper left', fontsize=7, ncol=2)
        
        self.ax2.grid(True, alpha=0.3, linestyle='--')

    def start_animation(self):
        # intervalo muy corto para animación rápida
        interval = 10  # 10ms entre frames
        
        print(f"Mostrando {self.total_frames} frames de animación...")
        print(f"Procesando {self.update_every} request(s) por frame...\n")
        
        anim = FuncAnimation(self.fig, self.animate_frame, 
                           frames=self.total_frames,
                           interval=interval, 
                           repeat=False,
                           cache_frame_data=False)  # no cachear para ahorrar memoria
        
        plt.tight_layout()
        plt.show()
        
        return anim

def main():
    print("\n" + "="*60)
    print("SIMULADOR DE BALANCEADOR DE CARGA - ROUND ROBIN")
    print("="*60 + "\n")
    
    # configuración
    while True:
        try:
            num_servers = int(input("¿Cuántos servidores quieres simular?: "))
            if num_servers > 0:
                break
            print("Debe ser mayor a 0")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    while True:
        try:
            num_requests = int(input("¿Cuántas solicitudes quieres procesar?: "))
            if num_requests > 0:
                break
            print("Debe ser mayor a 0")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    print(f"\nConfigurando balanceador con {num_servers} servidores...")
    print(f"Se procesarán {num_requests} solicitudes\n")
    
    # mostrar advertencia si hay muchos requests
    if num_requests > 5000:
        print(" Nota: Con muchos requests, la animación procesará varios")
        print("   requests por frame para acelerar la visualización.\n")
    
    input("Presiona ENTER para iniciar la simulación...")
    
    # crear y ejecutar animación
    print("\nIniciando animación del balanceador...\n")
    lb_anim = LoadBalancerAnimated(num_servers, num_requests)
    lb_anim.start_animation()
    
    # después de cerrar la animación, crear resumen final
    print("\nGenerando estadísticas finales...")
    
    # crear un balanceador nuevo para las estadísticas finales
    lb_final = LoadBalancer(num_servers)
    for i in range(num_requests):
        lb_final.process_request(i + 1)
    
    lb_final.print_statistics()
    

if __name__ == "__main__":
    main()
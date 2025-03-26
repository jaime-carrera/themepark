import simpy
import random
import csv
from collections import defaultdict
import datetime

# Establecer semilla global para reproducibilidad
random.seed(42)

# -----------------------------
# Clase: ConfiguracionParque
# -----------------------------
class ConfiguracionParque:
    def __init__(self, path_csv):
        self.atracciones = []
        self.capacidad_taquilla = 3
        self.precio_entrada = 20
        self.tasa_llegada = 0.5

        with open(path_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Nombre'] == 'CONFIG':
                    self.capacidad_taquilla = int(row['Num_Modulos'])
                    self.precio_entrada = float(row['Capacidad_por_Modulo'])
                    self.tasa_llegada = float(row['Tiempo_por_Turno'])
                else:
                    self.atracciones.append({
                        'nombre': row['Nombre'],
                        'num_modulos': int(row['Num_Modulos']),
                        'capacidad_por_modulo': int(row['Capacidad_por_Modulo']),
                        'tiempo_por_turno': float(row['Tiempo_por_Turno']),
                        'publico_permitido': row['Publico_Permitido'].split(',')
                    })

# -----------------------------
# Clase: DataCollector
# -----------------------------
class DataCollector:
    def __init__(self):
        self.visitantes_data = []
        self.ventas_efectivas = 0
        self.ventas_fallidas = 0
        self.ventas_online = 0
        self.entradas_online_utilizadas = 0
        self.tiempos_taquilla = []

    def registrar_visitante(self, data):
        self.visitantes_data.append(data)
        self.ventas_efectivas += 1

    def registrar_fallo(self):
        self.ventas_fallidas += 1

    def registrar_venta_online(self, utilizada):
        self.ventas_online += 1
        if utilizada:
            self.entradas_online_utilizadas += 1

    def registrar_tiempo_taquilla(self, tiempo):
        self.tiempos_taquilla.append(tiempo)

    def exportar_csv(self, filename="datos_visitantes.csv"):
        if not self.visitantes_data:
            print("No hay datos para exportar.")
            return

        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.visitantes_data[0].keys())
            writer.writeheader()
            writer.writerows(self.visitantes_data)
            print(f"Datos exportados a {filename}")

    def resumen(self):
        prom_taquilla = sum(self.tiempos_taquilla) / len(self.tiempos_taquilla) if self.tiempos_taquilla else 0
        print(f"\nResumen del día:")
        print(f"Ventas efectivas (taquilla): {self.ventas_efectivas}")
        print(f"Ventas online: {self.ventas_online}")
        print(f"Entradas online utilizadas: {self.entradas_online_utilizadas}")
        print(f"Asistentes que no entraron: {self.ventas_fallidas}")
        print(f"Tiempo promedio en taquilla: {prom_taquilla:.2f} minutos")

# -----------------------------
# Clase: Atraccion
# -----------------------------
class Atraccion:
    def __init__(self, env, nombre, num_modulos, capacidad_por_modulo, tiempo_por_turno, publico_permitido):
        self.env = env
        self.nombre = nombre
        self.capacidad_por_modulo = capacidad_por_modulo
        self.tiempo_por_turno = tiempo_por_turno
        self.publico_permitido = publico_permitido
        self.resource = simpy.Resource(env, capacity=num_modulos)
        self.personal = simpy.Resource(env, capacity=num_modulos)
        self.visitantes = 0
        self.tiempos_espera = []
        self.tiempos_uso = []
        self.popularidad = 0
        self.estado = "operativa"
        self.tiempo_mantenimiento = random.randint(100, 500)
        self.uso_para_mantenimiento = random.randint(400, 600)

    def usar(self, visitante):
        if self.estado != "operativa" or visitante['tipo'] not in self.publico_permitido:
            return None

        tiempo_llegada = self.env.now
        with self.resource.request() as req, self.personal.request() as staff:
            yield req & staff
            tiempo_espera = self.env.now - tiempo_llegada
            self.tiempos_espera.append(tiempo_espera)
            if tiempo_espera > 5:
                visitante['satisfaccion'] -= int(tiempo_espera // 5) * 2

            yield self.env.timeout(self.tiempo_por_turno)
            tiempo_uso = self.tiempo_por_turno
            self.tiempos_uso.append(tiempo_uso)
            self.visitantes += 1
            self.popularidad += 1

            print(f"[{formato_hora(self.env.now)}] Visitante {visitante['id']} disfrutó de {self.nombre}")

            if self.visitantes % self.uso_para_mantenimiento == 0:
                self.estado = "mantenimiento"
                yield self.env.timeout(self.tiempo_mantenimiento)
                self.estado = "operativa"

            return {
                'atraccion': self.nombre,
                'espera': tiempo_espera,
                'uso': tiempo_uso
            }

    def estadisticas(self):
        return {
            'nombre': self.nombre,
            'visitantes': self.visitantes,
            'prom_espera': sum(self.tiempos_espera) / len(self.tiempos_espera) if self.tiempos_espera else 0,
            'prom_uso': sum(self.tiempos_uso) / len(self.tiempos_uso) if self.tiempos_uso else 0,
            'popularidad': self.popularidad,
            'estado': self.estado
        }

# -----------------------------
# Clase: Taquilla
# -----------------------------
class Taquilla:
    def __init__(self, env, capacidad, precio_entrada, data_collector):
        self.env = env
        self.precio_entrada = precio_entrada
        self.tornos = simpy.Resource(env, capacity=capacidad)
        self.recaudacion = 0
        self.data_collector = data_collector

    def comprar(self, visitante):
        if visitante['online']:
            self.data_collector.registrar_venta_online(utilizada=True)
            print(f"[{formato_hora(self.env.now)}] Visitante {visitante['id']} ingresó con entrada online.")
            return True

        if len(self.tornos.queue) > 10:
            visitante['satisfaccion'] -= 20
            if visitante['satisfaccion'] < 30:
                self.data_collector.registrar_fallo()
                print(f"[{formato_hora(self.env.now)}] Visitante {visitante['id']} se fue por esperar demasiado en taquilla.")
                return False

        tiempo_inicio = self.env.now
        with self.tornos.request() as req:
            yield req
            yield self.env.timeout(random.uniform(0.5, 2))
            tiempo_total = self.env.now - tiempo_inicio
            self.data_collector.registrar_tiempo_taquilla(tiempo_total)
            self.recaudacion += self.precio_entrada
            print(f"[{formato_hora(self.env.now)}] Visitante {visitante['id']} compró entrada en taquilla.")
            return True


# -----------------------------
# Clase: ParqueTematico
# -----------------------------
class ParqueTematico:
    def __init__(self, env, atracciones, taquilla, data_collector):
        self.env = env
        self.atracciones = atracciones
        self.taquilla = taquilla
        self.data_collector = data_collector

    def visitar(self, visitante):
        acceso = yield self.env.process(self.taquilla.comprar(visitante))
        if not acceso:
            return

        entrada = self.env.now
        interacciones = 0
        espera_total = 0
        uso_total = 0

        while visitante['fatiga'] < 10 and visitante['satisfaccion'] > 30:
            atracciones_disponibles = [a for a in self.atracciones if visitante['tipo'] in a.publico_permitido and a.estado == "operativa"]
            if not atracciones_disponibles:
                break

            atraccion = random.choice(atracciones_disponibles)
            resultado = yield self.env.process(atraccion.usar(visitante))
            if resultado:
                interacciones += 1
                espera_total += resultado['espera']
                uso_total += resultado['uso']

            visitante['fatiga'] += 1
            visitante['satisfaccion'] -= random.randint(5, 15)
            yield self.env.timeout(random.randint(1, 3))

        salida = self.env.now
        self.data_collector.registrar_visitante({
            'id': visitante['id'],
            'tipo': visitante['tipo'],
            'atracciones_usadas': interacciones,
            'tiempo_total': salida - entrada,
            'prom_espera': espera_total / interacciones if interacciones else 0,
            'prom_uso': uso_total / interacciones if interacciones else 0,
            'satisfaccion_final': visitante['satisfaccion']
        })


# -----------------------------
# Funciones auxiliares
# -----------------------------
def formato_hora(minutos):
    hora_base = datetime.datetime(2023, 1, 1, 10, 0)  # parque abre a las 10:00
    hora_simulada = hora_base + datetime.timedelta(minutes=minutos)
    return hora_simulada.strftime("%H:%M")

def generar_asistentes(env, parque, tasa):
    id_v = 0
    while True:
        yield env.timeout(random.expovariate(tasa))
        id_v += 1
        tipo = random.choice(["niño", "adulto", "anciano"])
        online = random.random() < 0.2
        visitante = {"id": f"V{id_v}", "tipo": tipo, "fatiga": 0, "satisfaccion": 100, "online": online}
        if online:
            parque.data_collector.registrar_venta_online(utilizada=False)
        env.process(parque.visitar(visitante))


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    env = simpy.Environment()
    data_collector = DataCollector()

    archivo_csv = "THEMEPARK_IA/src/themepark_big.csv"
    config = ConfiguracionParque(archivo_csv)
    atracciones = [Atraccion(env, **a) for a in config.atracciones]
    taquilla = Taquilla(env, capacidad=config.capacidad_taquilla, precio_entrada=config.precio_entrada, data_collector=data_collector)
    parque = ParqueTematico(env, atracciones, taquilla, data_collector)

    print("Inicio de la simulación del parque temático 🏰\n")
    env.process(generar_asistentes(env, parque, tasa=config.tasa_llegada))
    env.run(until=480)  # Simula 8 horas desde las 10:00 hasta las 18:00

    print(f"\nRecaudación total: {taquilla.recaudacion} €")
    print("\nEstadísticas de atracciones:")
    for atr in atracciones:
        stats = atr.estadisticas()
        print(f"{stats['nombre']} → Visitantes: {stats['visitantes']} | Espera Prom: {stats['prom_espera']:.2f} | Uso Prom: {stats['prom_uso']:.2f} | Popularidad: {stats['popularidad']}")

    data_collector.exportar_csv()
    data_collector.resumen()

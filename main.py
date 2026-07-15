import sys
from datetime import datetime
from pymongo import MongoClient, errors
from bson import Regex

def conectar_bd():
    try:
        # Intenta conectar al motor MongoDB local en el puerto estándar
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        return client["veterinaria_elite_db"], client
    except errors.ServerSelectionTimeoutError:
        print("[!] ERROR: No se detectó MongoDB en el puerto 27017. Levanta el servicio antes de correr.")
        sys.exit(1)

db, client = conectar_bd()
coleccion = db["mascotas"]

def precargar_datos():
    if coleccion.count_documents({}) == 0:
        # 8 Documentos iniciales con subdocumento (dueno), array de subdocumentos (atenciones) y fecha significativos
        mascotas = [
            {
                "nombre": "Thor", "especie": "Perro", "edad": 5, "fecha_ingreso": datetime(2026, 2, 10),
                "dueno": {"nombre": "Juan Carlos", "telefono": "+56911112222", "correo": "juan@mail.com"},
                "atenciones": [{"motivo": "Vacuna Antirrabica", "costo": 18000}, {"motivo": "Control Sano", "costo": 12000}]
            },
            {
                "nombre": "Luna", "especie": "Gato", "edad": 2, "fecha_ingreso": datetime(2026, 3, 15),
                "dueno": {"nombre": "Ana Maria", "telefono": "+56933334444", "correo": "ana@mail.com"},
                "atenciones": []
            },
            {
                "nombre": "Kira", "especie": "Perro", "edad": 7, "fecha_ingreso": datetime(2026, 3, 20),
                "dueno": {"nombre": "Pedro Pablo", "telefono": "+56955556666", "correo": "pedro@mail.com"},
                "atenciones": [{"motivo": "Limpieza Dental", "costo": 45000}]
            },
            {
                "nombre": "Felix", "especie": "Gato", "edad": 1, "fecha_ingreso": datetime(2026, 4, 2),
                "dueno": {"nombre": "Mia Colucci", "telefono": "+56977778888", "correo": "mia@mail.com"},
                "atenciones": [{"motivo": "Urgencia Obstruccion", "costo": 85000}, {"motivo": "Control Postop", "costo": 15000}]
            },
            {
                "nombre": "Max", "especie": "Perro", "edad": 4, "fecha_ingreso": datetime(2026, 4, 18),
                "dueno": {"nombre": "Luis Jara", "telefono": "+56999990000", "correo": "luis@mail.com"},
                "atenciones": [{"motivo": "Vacuna Octuple", "costo": 18000}]
            },
            {
                "nombre": "Toby", "especie": "Perro", "edad": 9, "fecha_ingreso": datetime(2026, 5, 05),
                "dueno": {"nombre": "Rosa Espinoza", "telefono": "+56912345678", "correo": "rosa@mail.com"},
                "atenciones": [{"motivo": "Cirugia Esterilizacion", "costo": 120000}]
            },
            {
                "nombre": "Pelusa", "especie": "Gato", "edad": 3, "fecha_ingreso": datetime(2026, 5, 22),
                "dueno": {"nombre": "Jose Miguel", "telefono": "+56987654321", "correo": "jose@mail.com"},
                "atenciones": []
            },
            {
                "nombre": "Rocky", "especie": "Perro", "edad": 6, "fecha_ingreso": datetime(2026, 6, 12),
                "dueno": {"nombre": "Clara Bella", "telefono": "+56911223344", "correo": "clara@mail.com"},
                "atenciones": [{"motivo": "Control Sano", "costo": 12000}]
            }
        ]
        coleccion.insert_many(mascotas)
        print("[+] Base de datos inicializada. 8 Fichas veterinarias cargadas con éxito.")

def crear_documento():
    print("\n--- REGISTRAR NUEVA FICHA VETERINARIA ---")
    try:
        nombre = input("Nombre de la Mascota: ")
        especie = input("Especie (Perro, Gato, etc.): ")
        edad = int(input("Edad: "))
        fecha_str = input("Fecha de Ingreso (YYYY-MM-DD): ")
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        
        # Subdocumento obligatorio
        d_nombre = input("Nombre Dueño: ")
        d_tel = input("Teléfono Dueño: ")
        d_correo = input("Correo Dueño: ")
        dueno = {"nombre": d_nombre, "telefono": d_tel, "correo": d_correo}
        
        # Array de subdocumentos obligatorio
        atenciones = []
        while input("¿Desea agregar un registro de atención? (s/n): ").lower() == 's':
            motivo = input("  Motivo/Tratamiento: ")
            costo = float(input("  Costo de atención ($): "))
            atenciones.append({"motivo": motivo, "costo": costo})
            
        doc = {
            "nombre": nombre, "especie": especie, "edad": edad, 
            "fecha_ingreso": fecha, "dueno": dueno, "atenciones": atenciones
        }
        resultado = coleccion.insert_one(doc)
        print(f"[+] Documento insertado con éxito en la Matrix. ID generado: {resultado.inserted_id}")
    except Exception as e:
        print(f"[!] ERROR al instanciar ficha: {e}")

def listar_documentos():
    print("\n--- LISTADO GENERAL DE MASCOTAS (CON PROYECCIÓN TÁCTICA) ---")
    # Proyección selectiva para cumplir nivel destacado sin ensuciar consola
    for doc in coleccion.find({}, {"nombre": 1, "especie": 1, "edad": 1, "dueno.nombre": 1, "_id": 0}):
        print(f"- {doc.get('nombre')} ({doc.get('especie')}) | Edad: {doc.get('edad')} años | Responsable: {doc.get('dueno', {}).get('nombre')}")

def buscar_operador():
    print("\n--- BUSCAR POR COMPARACIÓN DE EDAD (Operador $gte) ---")
    try:
        edad_min = int(input("Mostrar mascotas de edad mayor o igual a: "))
        for doc in coleccion.find({"edad": {"$gte": edad_min}}, {"nombre": 1, "especie": 1, "edad": 1, "_id": 0}):
            print(f"- {doc.get('nombre')} ({doc.get('especie')}) tiene {doc.get('edad')} años.")
    except ValueError:
        print("[!] Entrada no numérica.")

def buscar_regex():
    print("\n--- BUSQUEDA DE DUEÑO POR EXPRESIÓN REGULAR ---")
    patron = input("Ingrese patrón de búsqueda (Nombre Dueño): ")
    for doc in coleccion.find({"dueno.nombre": Regex(patron, "i")}):
        print(doc)

def buscar_fechas():
    print("\n--- BUSCAR POR RANGO DE FECHAS DE INGRESO ---")
    try:
        f_inicio = datetime.strptime(input("Fecha inicio (YYYY-MM-DD): "), "%Y-%m-%d")
        f_fin = datetime.strptime(input("Fecha fin (YYYY-MM-DD): "), "%Y-%m-%d")
        for doc in coleccion.find({"fecha_ingreso": {"$gte": f_inicio, "$lte": f_fin}}):
            print(doc)
    except ValueError:
        print("[!] Formato de fecha erróneo o inválido.")

def buscar_subdocumento_array():
    print("\n--- CONSULTAR EN ESTRUCTURAS ANIDADAS ---")
    print("1. Buscar por Correo de Dueño (Subdocumento)\n2. Buscar por Motivo de Atención (Array)")
    opc = input("Seleccione sub-búsqueda: ")
    if opc == "1":
        correo = input("Correo: ")
        for doc in coleccion.find({"dueno.correo": correo}): print(doc)
    elif opc == "2":
        motivo = input("Motivo/Tratamiento: ")
        for doc in coleccion.find({"atenciones.motivo": Regex(motivo, "i")}): print(doc)

def actualizar_raiz():
    print("\n--- ACTUALIZAR CAMPO DE DOCUMENTO RAÍZ ---")
    nombre = input("Nombre de la mascota a modificar: ")
    doc_antes = coleccion.find_one({"nombre": nombre})
    if doc_antes:
        print(f"Estado Pre-Operación:\n{doc_antes}")
        nueva_edad = int(input("Nueva Edad: "))
        coleccion.update_one({"_id": doc_antes["_id"]}, {"$set": {"edad": nueva_edad}})
        print(f"Estado Post-Operación:\n{coleccion.find_one({'_id': doc_antes['_id']})}")
    else:
        print("[!] Mascota no localizada.")

def actualizar_sub_array():
    print("\n--- ACTUALIZAR DENTRO DE SUBDOCUMENTO / ARRAY ---")
    nombre = input("Nombre de la mascota: ")
    doc = coleccion.find_one({"nombre": nombre})
    if doc:
        print(f"Estado Pre-Operación:\n{doc}")
        nuevo_motivo = input("Nuevo motivo de atención a registrar: ")
        nuevo_costo = float(input("Costo de la atención: "))
        # Inserta un elemento en el array de subdocumentos usando $push
        coleccion.update_one({"_id": doc["_id"]}, {"$push": {"atenciones": {"motivo": nuevo_motivo, "costo": nuevo_costo}}})
        print(f"Estado Post-Operación:\n{coleccion.find_one({'_id': doc['_id']})}")
    else:
        print("[!] No se encontró el registro.")

def eliminar_documento():
    print("\n--- ELIMINACIÓN DE DOCUMENTO CON CONFIRMACIÓN ---")
    nombre = input("Nombre de la mascota a dar de baja del sistema: ")
    doc = coleccion.find_one({"nombre": nombre})
    if doc:
        print(f"ATENCIÓN. Se procederá a eliminar la ficha de: {doc}")
        conf = input("¿Confirmar operación irreversible? (s/n): ")
        if conf.lower() == 's':
            resultado = coleccion.delete_one({"_id": doc["_id"]})
            print(f"[+] Operación completada. Documentos eliminados de la colección: {resultado.deleted_count}")
    else:
        print("[!] Registro no encontrado.")

def pipeline_agregacion():
    print("\n--- PIPELINE DE AGREGACIÓN DE ALTO RENDIMIENTO (3 ETAPAS) ---")
    # Desarrolla: $unwind del array -> $match para procesar solo Perros -> $group para calcular costos de atención por mascota
    pipeline = [
        {"$unwind": "$atenciones"},
        {"$match": {"especie": "Perro"}},
        {"$group": {
            "_id": "$nombre", 
            "total_gastado_atenciones": {"$sum": "$atenciones.costo"}, 
            "atenciones_recibidas": {"$sum": 1}
        }}
    ]
    resultados = list(coleccion.aggregate(pipeline))
    if resultados:
        for res in resultados:
            print(f"Mascota (Perro): {res['_id']} | Visitas Registradas: {res['atenciones_recibidas']} | Gasto Histórico: ${res['total_gastado_atenciones']:.2f}")
    else:
        print("[-] No hay datos de atenciones para procesar en el pipeline en este momento.")

def menu():
    precargar_datos()
    while True:
        print("\n" + "="*35)
        print(" VETERINARIA ELITE - CONTROL PANEL ")
        print("="*35)
        print("1. Crear Ficha Mascota\n2. Listar Mascotas\n3. Buscar por Edad ($gte)\n4. Buscar por Regex\n5. Buscar por Rango de Fechas\n6. Buscar en Subdocumento o Array\n7. Actualizar Edad (Raíz)\n8. Agregar Atención (Array)\n9. Eliminar Registro\n10. Ejecutar Pipeline de Costos\n11. Desconectar Terminal")
        opc = input("Ingrese Comando: ")
        if opc == "1": crear_documento()
        elif opc == "2": listar_documentos()
        elif opc == "3": buscar_operador()
        elif opc == "4": buscar_regex()
        elif opc == "5": buscar_fechas()
        elif opc == "6": buscar_subdocumento_array()
        elif opc == "7": actualizar_raiz()
        elif opc == "8": actualizar_sub_array()
        elif opc == "9": eliminar_documento()
        elif opc == "10": pipeline_agregacion()
        elif opc == "11": break

if __name__ == "__main__":
    menu()

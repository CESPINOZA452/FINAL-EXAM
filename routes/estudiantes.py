from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from pymongo import MongoClient, errors

# Creamos un Blueprint para agrupar las rutas de estudiantes
estudiantes_bp = Blueprint('students', __name__)

# Configuración de MongoDB
try:
    # Añadimos un timeout de 2 segundos para detectar errores rápido
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    db = client['cibertec_db']
    students_col = db['students']
    # Forzamos una llamada para verificar la conexión al inicio
    client.admin.command('ping')
except errors.ServerSelectionTimeoutError:
    print("❌ ERROR: No se pudo conectar a MongoDB. Verifica que el servicio esté activo.")
    students_col = None

def get_next_id():
    """Helper para simular autoincremento en MongoDB"""
    last_student = students_col.find_one(sort=[("id", -1)])
    if last_student:
        return last_student['id'] + 1
    return 1


# Helper function to get data from either JSON or form
def get_request_data():
    if request.is_json:
        return request.get_json()
    else:
        return request.form

# 1. CREAR UN ESTUDIANTE (POST /students)
@estudiantes_bp.route('/students', methods=['POST'])
def create_student():
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
        
    data = get_request_data()
    
    # Validación de campos obligatorios
    required_fields = ['name', 'grade', 'dni', 'age', 'is_approved']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Datos incompletos. Se requiere: {', '.join(required_fields)}"}), 400

    try:
        # Validación de DNI único
        if students_col.find_one({"dni": str(data['dni'])}):
            return jsonify({"error": "El DNI ya se encuentra registrado"}), 400
        
        nuevo_estudiante = {
            "id": get_next_id(),
            "name": data['name'],
            "dni": str(data['dni']),
            "age": int(data['age']),
            "is_approved": str(data.get('is_approved')).lower() in ['true', '1', 'on', 'yes'],
            "grade": float(data['grade']),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except ValueError:
        return jsonify({"error": "La edad y la nota deben ser valores numéricos válidos"}), 400
    
    students_col.insert_one(nuevo_estudiante)
    # Limpiamos el _id de Mongo para la respuesta JSON
    nuevo_estudiante.pop('_id', None)
    return jsonify(nuevo_estudiante), 201


# 2. OBTENER TODOS LOS ESTUDIANTES (GET /students)
@estudiantes_bp.route('/students', methods=['GET'])
def get_all_students():
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
    estudiantes = list(students_col.find({}, {'_id': 0}))
    return jsonify(estudiantes), 200


# 3. OBTENER UN ESTUDIANTE POR ID (GET /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['GET'])
def get_student_by_id(id):
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
    estudiante = students_col.find_one({"id": id}, {'_id': 0})
    if not estudiante:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    return jsonify(estudiante), 200


# 4. ACTUALIZAR UN ESTUDIANTE (PUT /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
        
    estudiante = students_col.find_one({"id": id})
    if not estudiante:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    
    data = get_request_data()
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

    update_fields = {}
    
    if 'dni' in data and data['dni'] != estudiante['dni']:
        if students_col.find_one({"dni": str(data['dni'])}):
            return jsonify({"error": "El nuevo DNI ya pertenece a otro estudiante"}), 400
        update_fields['dni'] = str(data['dni'])

    try:
        if 'name' in data: update_fields['name'] = data['name']
        if 'age' in data: update_fields['age'] = int(data['age'])
        if 'grade' in data: update_fields['grade'] = float(data['grade'])
        if 'is_approved' in data:
            update_fields['is_approved'] = str(data.get('is_approved')).lower() in ['true', '1', 'on', 'yes']
    except ValueError:
        return jsonify({"error": "La edad y la nota deben ser valores numéricos válidos"}), 400
        
    update_fields['updated_at'] = datetime.now().isoformat()
    
    students_col.update_one({"id": id}, {"$set": update_fields})
    actualizado = students_col.find_one({"id": id}, {'_id': 0})
    return jsonify(actualizado), 200


# 5. ELIMINAR UN ESTUDIANTE (DELETE /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
        
    result = students_col.delete_one({"id": id})
    if result.deleted_count == 0:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    
    return jsonify({"message": f"Estudiante con ID {id} eliminado correctamente"}), 200


# 6. CREACIÓN MASIVA (POST /students/bulk)
@estudiantes_bp.route('/students/bulk', methods=['POST'])
def bulk_insert_students():
    if students_col is None:
        return jsonify({"error": "Base de datos no disponible"}), 500
        
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "El cuerpo de la petición debe ser una lista de estudiantes"}), 400
    
    insertados = []
    start_id = get_next_id()
    # Definimos campos requeridos para consistencia
    required = ['name', 'grade', 'dni', 'age', 'is_approved']
    
    try:
        for item in data:
        # Validamos que el objeto tenga los campos mínimos
            if all(k in item for k in required):
                if students_col.find_one({"dni": str(item['dni'])}):
                    continue
                nuevo = {
                    "id": start_id,
                    "name": item['name'],
                    "dni": str(item['dni']),
                    "age": int(item['age']),
                    "is_approved": str(item.get('is_approved')).lower() in ['true', '1', 'on', 'yes'],
                    "grade": float(item['grade']),
                    "created_at": datetime.now().isoformat(), 
                    "updated_at": datetime.now().isoformat()
                }
                insertados.append(nuevo)
                start_id += 1
    except (ValueError, TypeError):
        return jsonify({"error": "Error en el formato de datos de uno o más estudiantes"}), 400
    
    if insertados:
        students_col.insert_many(insertados)
        for s in insertados: s.pop('_id', None)

    return jsonify({
        "message": f"Se registraron {len(insertados)} estudiantes con éxito",
        "students": insertados
    }), 201


# 7. PROMEDIO DE NOTAS (GET /students/average)
@estudiantes_bp.route('/students/average', methods=['GET'])
def get_students_average():
    if students_col is None:
        return jsonify({"average": 0.0, "total_students": 0}), 200
        
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_grade": {"$avg": "$grade"},
                "total": {"$sum": 1}
            }
        }
    ]
    stats = list(students_col.aggregate(pipeline))
    if not stats:
        return jsonify({"average": 0.0, "total_students": 0}), 200
    
    return jsonify({
        "average": round(stats[0]['avg_grade'], 2),
        "total_students": stats[0]['total']
    }), 200
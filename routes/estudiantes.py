from flask import Blueprint, jsonify, request, render_template
from datetime import datetime

# Creamos un Blueprint para agrupar las rutas de estudiantes
estudiantes_bp = Blueprint('students', __name__)

# Base de datos simulada en memoria (Lista de diccionarios)
# Cada estudiante tendrá: id, nombre, nota y fechas de auditoría
students_db = [
    {
        "id": 1, 
        "name": "Juan Perez", 
        "dni": "12345678",
        "age": 20,
        "is_approved": True,
        "grade": 15.5,
        "created_at": datetime.now().isoformat(), 
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": 2, 
        "name": "Maria Lopez", 
        "dni": "87654321",
        "age": 22,
        "is_approved": True,
        "grade": 18.0,
        "created_at": datetime.now().isoformat(), 
        "updated_at": datetime.now().isoformat()
    }
]

# Contador para autoincrementar el ID de nuevos estudiantes
current_id = 2

# Helper function to get data from either JSON or form
def get_request_data():
    if request.is_json:
        return request.get_json()
    else:
        return request.form

# 1. CREAR UN ESTUDIANTE (POST /students)
@estudiantes_bp.route('/students', methods=['POST'])
def create_student():
    global current_id
    data = get_request_data()
    
    # Validación de campos obligatorios
    required_fields = ['name', 'grade', 'dni', 'age', 'is_approved']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Datos incompletos. Se requiere: {', '.join(required_fields)}"}), 400

    # Validación de DNI único
    if any(s['dni'] == str(data['dni']) for s in students_db):
        return jsonify({"error": "El DNI ya se encuentra registrado"}), 400
    
    current_id += 1
    nuevo_estudiante = {
        "id": current_id,
        "name": data['name'],
        "dni": str(data['dni']),
        "age": int(data['age']),
        "is_approved": bool(data.get('is_approved')),
        "grade": float(data['grade']),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    students_db.append(nuevo_estudiante)
    return jsonify(nuevo_estudiante), 201
    # Si la petición viene de HTMX, podríamos devolver la tabla actualizada directamente
    # if request.headers.get('HX-Request') == 'true':
    #     return render_template('partials/tabla.html', estudiantes=students_db)
    # else:
    #     return jsonify(nuevo_estudiante), 201

# 2. OBTENER TODOS LOS ESTUDIANTES (GET /students)
@estudiantes_bp.route('/students', methods=['GET'])
def get_all_students():
    return jsonify(students_db), 200


# 3. OBTENER UN ESTUDIANTE POR ID (GET /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['GET'])
def get_student_by_id(id):
    estudiante = next((s for s in students_db if s['id'] == id), None)
    if not estudiante:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    return jsonify(estudiante), 200


# 4. ACTUALIZAR UN ESTUDIANTE (PUT /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['PUT', 'PATCH'])
def update_student(id):
    estudiante = next((s for s in students_db if s['id'] == id), None)
    if not estudiante:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
    
    # Si se intenta actualizar el DNI, verificar unicidad
    if 'dni' in data and data['dni'] != estudiante['dni']:
        if any(s['dni'] == str(data['dni']) for s in students_db):
            return jsonify({"error": "El nuevo DNI ya pertenece a otro estudiante"}), 400
        estudiante['dni'] = str(data['dni'])

    # Modificamos los campos provistos
    for field in ['name', 'age', 'is_approved']:
        if field in data:
            estudiante[field] = data[field]
    if 'grade' in data:
        estudiante['grade'] = float(data['grade'])
        
    # ⚠️ REQUERIMIENTO OBLIGATORIO: Actualizar la fecha de modificación
    estudiante['updated_at'] = datetime.now().isoformat()
    
    return jsonify(estudiante), 200


# 5. ELIMINAR UN ESTUDIANTE (DELETE /students/{id})
@estudiantes_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students_db
    estudiante = next((s for s in students_db if s['id'] == id), None)
    if not estudiante:
        return jsonify({"error": f"Estudiante con ID {id} no encontrado"}), 404
    
    # Modificamos la lista original para que main.py vea los cambios
    students_db[:] = [s for s in students_db if s['id'] != id]
    return jsonify({"message": f"Estudiante con ID {id} eliminado correctamente"}), 200


# 6. CREACIÓN MASIVA (POST /students/bulk)
@estudiantes_bp.route('/students/bulk', methods=['POST'])
def bulk_insert_students():
    global current_id
    data = request.get_json()  # Se espera una lista de estudiantes
    
    if not isinstance(data, list):
        return jsonify({"error": "El cuerpo de la petición debe ser una lista de estudiantes"}), 400
    
    insertados = []
    for item in data:
        # Validación simple para bulk: nombre, nota y dni obligatorio
        if all(k in item for k in ('name', 'grade', 'dni')):
            # Verificar unicidad de DNI incluso en carga masiva
            if any(s['dni'] == str(item['dni']) for s in students_db):
                continue
            current_id += 1
            nuevo = {
                "id": current_id,
                "name": item['name'],
                "dni": str(item['dni']),
                "age": item.get('age', 0),
                "is_approved": item.get('is_approved', False),
                "grade": float(item['grade']),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            students_db.append(nuevo)
            insertados.append(nuevo)
            
    return jsonify({
        "message": f"Se registraron {len(insertados)} estudiantes con éxito",
        "students": insertados
    }), 201


# 7. PROMEDIO DE NOTAS (GET /students/average)
@estudiantes_bp.route('/students/average', methods=['GET'])
def get_students_average():
    if not students_db:
        return jsonify({"average": 0.0, "total_students": 0}), 200
        
    # Extraemos solo las notas y calculamos el promedio aritmético
    notas = [s['grade'] for s in students_db]
    promedio = sum(notas) / len(notas)
    
    return jsonify({
        "average": round(promedio, 2),
        "total_students": len(students_db)
    }), 200
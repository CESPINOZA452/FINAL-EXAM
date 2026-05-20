# Gestión de Estudiantes - Flask & MongoDB

Examen final usando **Flask** y **MongoDB** para la gestión de datos.

## Funcionalidades

- Gestión de datos de estudiantes (Nombre, DNI, Edad, Nota, Estado de aprobación).
- **Creación de datos de estudiante particular**
- **Creación masiva de datos de estudiantes**
- **Obtención de datos de alumno particular**
- **Obtención masiva de datos de estudiantes**
- **Actualización de datos de estudiante particular**
- **Eliminación de datos de estudiante particular**
- **Promedio de notas en general**

## Requisitos

1. Tener instalado Python 3.x y MongoDB Server.
2. **Instalar dependencias:**
   ```bash
   pip install flask pymongo
   ```
3. **Base de Datos:**
   Asegúrate de que el servicio de MongoDB esté activo

## Ejecución

Para iniciar el servidor de desarrollo:
```bash
python main.py
```

## 📁 Estructura del Proyecto

- `main.py`: Punto de entrada y configuración de la app Flask.
- `routes/estudiantes.py`: Lógica de negocio, validaciones y acceso a datos.
- `templates/`: Vistas HTML y componentes dinámicos.
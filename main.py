from flask import Flask, render_template
from routes.estudiantes import estudiantes_bp, students_col

app = Flask(__name__)

# Registramos las rutas de estudiantes en la app de Flask
app.register_blueprint(estudiantes_bp)

# Define la ruta principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para visualizar la tabla
@app.route('/view/students')
def view_students():
    if students_col is not None:
        estudiantes = list(students_col.find({}, {'_id': 0}))
    else:
        estudiantes = []
    return render_template('partials/tabla.html', estudiantes=estudiantes)

# Ejecución del aplicativo
if __name__ == '__main__':
    app.run(debug=True)
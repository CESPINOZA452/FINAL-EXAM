from flask import Flask, render_template
# Importamos también la lista students_db para poder mostrarla en la tabla
from routes.estudiantes import estudiantes_bp, students_db

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
    return render_template('tabla.html', estudiantes=students_db)

# Ejecución del aplicativo
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template
from db import get_db_connection

app = Flask(__name__)

# Ruta para index
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para Login
@app.route('/login')
def login():
    return render_template('login.html')

# Ruta de prueba de ls Base de Datos conecte 
@app.route('/test-db')
def test_db():
    db = get_db_connection()
    if db and db.is_connected():
        db.close()
        return "¡Conexión a MySQL exitosa de forma correcta!"
    return "Error al conectar a la base de datos. Intente de nuevo."

if __name__ == '__main__':
    # Ejecuta el servidor en modo desarrollo para ver cambios en vivo
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from controllers.user_controller import buscar_usuario_por_correo, crear_nuevo_usuario, registrar_token_real, actualizar_contrasena_real

app = Flask(__name__)
# Llave de cifrado obligatoria para proteger la sesión del usuario logueado
app.secret_key = 'clave_secretaEPF'


#Página de inicio (Index)

@app.route('/')
def index():
    return render_template('index.html')


# RUTA DEL LOGIN, Formulario de acceso

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #recuperar contraseña,
        if 'recuperar_email' in request.form:
            correo_recuperar = request.form.get('recuperar_email')
            token = registrar_token_real(correo_recuperar)
            
            if token:
                # El controlador creó el token en MySQL
                return redirect(url_for('restablecer', token=token))
            else:
                return "<h3>El correo no está registrado o se encuentra inactivo.</h3>"

        # cuadro de inicio de sesion 
        correo_usuario = request.form.get('email')
        contrasena_usuario = request.form.get('password')   
        usuario = buscar_usuario_por_correo(correo_usuario)
        
        if usuario:
            hash_bd = usuario['contrasena_hash']
            if isinstance(hash_bd, (bytes, bytearray)):
                hash_bd = hash_bd.decode('utf-8')
            
            # Validación de la pass en la BD
            if check_password_hash(hash_bd, contrasena_usuario):
                session['id_usuario'] = usuario['id_usuario']
                session['nombre_usuario'] = usuario['nombre']
                session['rol_usuario'] = usuario['nombre_rol']
                return redirect(url_for('dashboard'))
        
        return render_template('login.html', error_login=True)
            
    return render_template('login.html')


# RUTA DEL REGISTRO, Crear estudiante

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        correo = request.form.get('email')
        
        #Solo permite correos institucionales oficiales
        # (Cambiar '@escuela.com' por el dominio oficial de tu institución, pero mas adelante supongo)
        if not correo.endswith('@escuela.com'):
            return "<h3>Error: El registro está restringido únicamente para correos institucionales autorizados.</h3>"

        nombre = request.form.get('nombre')
        apellido1 = request.form.get('apellido1')
        apellido2 = request.form.get('apellido2')
        correo = request.form.get('email')
        contrasena = request.form.get('password')
        telefono = request.form.get('telefono')
        id_rol = request.form.get('id_rol') # como 1=Admin, 2=Docente, 3=Estudiante, 4=Padre, 5=Personal administrativo
        
        # Guardamos en la base de datos
        exito = crear_nuevo_usuario(nombre, apellido1, apellido2, correo, contrasena, telefono, id_rol)
        
        if exito:
            # Si se creó bien, el flujo te manda directo al Login a meter nuevas credenciales
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error_registro=True)
            
    return render_template('register.html')


#pantalla para ingresar el correo para la recuperacion de contraseña

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form.get('email')
        
        # El controlador busca el usuario en MySQL y genera el token 
        token = registrar_token_real(correo)
        
        if token:
            return redirect(url_for('restablecer', token=token))
        else:
            return "<h3>El correo electrónico ingresado no existe en el sistema escolar.</h3>"
            
    return render_template('forgot_password.html')


#Pantalla para asignar clave nueva

@app.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer(token):
    if request.method == 'POST':
        nueva_clave = request.form.get('password')
        # El controlador hace el UPDATE del hash en la tabla usuarios
        exito = actualizar_contrasena_real(token, nueva_clave)
        
        if exito:
            return "<h3>Contraseña restablecida con éxito en MySQL. Ya puedes ir a <a href='/login'>Iniciar Sesión</a> con tu nueva clave.</h3>"
        return "<h3>Error: El enlace de recuperación es inválido, caducó o ya fue utilizado.</h3>"
        
    return render_template('reset_password.html', token=token)


#Panel de Control Escolar (Dashboard), de prueba para ver si pasa la paagina 

@app.route('/dashboard')
def dashboard():
    #Si no ha iniciado sesión, se redirige al Login
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
        
    # Si la sesión es válida, se muestra la pag con este mensaje de bienvenida y el rol del usuario
    return f"""
        <h1>Bienvenido al Sistema Escolar, {session['nombre_usuario']}</h1>
        <p>Tu rol asignado es: <strong>{session['rol_usuario']}</strong></p>
        <br>
        <a href="{url_for('logout')}" style="padding: 10px 20px; background-color: #e53e3e; color: white; text-decoration: none; border-radius: 5px; font-family: sans-serif;">
            Cerrar Sesión 
        </a>
    """

#Ruta de cerrar sesion desde cualquier pantalla

@app.route('/logout')
def logout():
    # Se borra la memoria del navegador
    session.clear()
    # Expulsamos al usuario directo al Login
    return redirect(url_for('login'))


#Ruta de prueba de conexión

@app.route('/test-db')
def test_db():
    from db import get_db_connection
    db = get_db_connection()
    if db and db.is_connected():
        db.close()
        return "¡Conexión a MySQL exitosa de forma correcta!"
    return "Error al conectar a la base de datos."

if __name__ == '__main__':
    app.run(debug=True)

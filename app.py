from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

from controllers.user_controller import (
    buscar_usuario_por_correo,
    crear_nuevo_usuario,
    registrar_token_real,
    actualizar_contrasena_real
)

from db import get_db_connection

from controllers.admin_required import admin_required

from controllers.permission_required import permission_required

from controllers.role_controller import (
    obtener_roles,
    crear_rol,
    editar_rol,
    eliminar_rol,
    obtener_permisos,
    obtener_permisos_por_rol,
    guardar_permisos_rol
)


from controllers.group_controller import (
    obtener_grupos,
    obtener_docentes,
    crear_grupo,
    obtener_grupo_por_id,
    editar_grupo,
    eliminar_grupo
)


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

        # todo registro público se crea como estudiante

        id_rol = 3
        
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

    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    rol_usuario = session.get('rol_usuario')

    # ======================================================
    # DASHBOARD ADMINISTRADOR
    # ======================================================

    if rol_usuario == 'Administrador':

        connection = get_db_connection()

        total_usuarios = 0
        total_estudiantes = 0
        total_docentes = 0
        total_grupos = 0

        if connection:

            try:

                cursor = connection.cursor(dictionary=True)

                # Usuarios
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM usuarios
                """)

                total_usuarios = cursor.fetchone()['total']


                # Estudiantes
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM estudiantes
                """)

                total_estudiantes = cursor.fetchone()['total']


                # Docentes
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM docentes
                """)

                total_docentes = cursor.fetchone()['total']


                # Grupos
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM grupos
                """)

                total_grupos = cursor.fetchone()['total']


            except Exception as e:

                print(
                    f"Error al cargar estadísticas del dashboard: {e}"
                )

            finally:

                try:
                    cursor.close()
                    connection.close()
                except Exception:
                    pass


        return render_template(
            'admin/dashboard.html',
            total_usuarios=total_usuarios,
            total_estudiantes=total_estudiantes,
            total_docentes=total_docentes,
            total_grupos=total_grupos
        )


    # ======================================================
    # OTROS PERFILES
    # ======================================================

    return render_template(
        'dashboard.html',
        nombre=session.get('nombre_usuario'),
        rol=rol_usuario
    )



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


# GESTION DE ROLES
@app.route('/admin/roles', methods=['GET'])
@admin_required
def admin_roles():

    roles = obtener_roles()

    permisos = obtener_permisos()

    permisos_por_rol = obtener_permisos_por_rol()

    return render_template(
        'admin/roles.html',
        roles=roles,
        permisos=permisos,
        permisos_por_rol=permisos_por_rol
    )



# ============================================================
# EPF-01-04 - CREAR ROL
# ============================================================

@app.route('/admin/roles/crear', methods=['POST'])
@admin_required
def admin_roles_crear():

    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        return redirect(
            url_for(
                'admin_roles',
                error='El nombre del rol es obligatorio.'
            )
        )

    if len(nombre) > 100:
        return redirect(
            url_for(
                'admin_roles',
                error='El nombre del rol no puede superar los 100 caracteres.'
            )
        )

    exito, mensaje = crear_rol(
        nombre,
        descripcion
    )

    if exito:
        return redirect(
            url_for(
                'admin_roles',
                success='creado'
            )
        )

    return redirect(
        url_for(
            'admin_roles',
            error=mensaje
        )
    )


# ============================================================
# EPF-01-04 - EDITAR ROL
# ============================================================

@app.route('/admin/roles/editar/<int:id_rol>', methods=['POST'])
@admin_required
def admin_roles_editar(id_rol):

    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        return redirect(
            url_for(
                'admin_roles',
                error='El nombre del rol es obligatorio.'
            )
        )

    if len(nombre) > 100:
        return redirect(
            url_for(
                'admin_roles',
                error='El nombre del rol no puede superar los 100 caracteres.'
            )
        )

    exito, mensaje = editar_rol(
        id_rol,
        nombre,
        descripcion
    )

    if exito:
        return redirect(
            url_for(
                'admin_roles',
                success='editado'
            )
        )

    return redirect(
        url_for(
            'admin_roles',
            error=mensaje
        )
    )


# ============================================================
# EPF-01-04 - ELIMINAR ROL
# ============================================================

@app.route('/admin/roles/eliminar/<int:id_rol>', methods=['POST'])
@admin_required
def admin_roles_eliminar(id_rol):

    exito, mensaje = eliminar_rol(id_rol)

    if exito:
        return redirect(
            url_for(
                'admin_roles',
                success='eliminado'
            )
        )

    return redirect(
        url_for(
            'admin_roles',
            error=mensaje
        )
    )


# ============================================================
# EPF-01-04 - GESTIONAR PERMISOS
# ============================================================

@app.route(
    '/admin/roles/permisos/<int:id_rol>',
    methods=['POST']
)
@admin_required
def admin_roles_permisos(id_rol):

    permisos = request.form.getlist('permisos')

    exito, mensaje = guardar_permisos_rol(
        id_rol,
        permisos
    )

    if exito:

        return redirect(
            url_for(
                'admin_roles',
                success='permisos'
            )
        )

    return redirect(
        url_for(
            'admin_roles',
            error=mensaje
        )
    )


# ============================================================
# EPF-02-01 - GESTION DE GRUPOS Y SECCIONES
# ============================================================


@app.route('/admin/grupos', methods=['GET'])
@permission_required('grupos.ver')
def admin_grupos():

    grupos = obtener_grupos()
    docentes = obtener_docentes()

    return render_template(
        'admin/grupos.html',
        grupos=grupos,
        docentes=docentes,
        puede_editar=True,
        puede_eliminar=True
    )

    


# ============================================================
# EPF-02-01 - CREAR GRUPO
# ============================================================

@app.route('/admin/grupos/nuevo', methods=['GET', 'POST'])
@permission_required('grupos.crear')
def admin_grupos_nuevo():

    docentes = obtener_docentes()

    if request.method == 'POST':

        nivel = request.form.get('nivel', '').strip()
        seccion = request.form.get('seccion', '').strip()
        anio_lectivo = request.form.get('anio_lectivo', '').strip()
        id_docente_guia = request.form.get('id_docente_guia', '').strip()

        exito, mensaje = crear_grupo(
            nivel,
            seccion,
            anio_lectivo,
            id_docente_guia
        )

        if exito:
            return redirect(
                url_for(
                    'admin_grupos',
                    success='creado'
                )
            )

        return redirect(
            url_for(
                'admin_grupos',
                error=mensaje
            )
        )

    return render_template(
        'admin/grupo_form.html',
        docentes=docentes
    )


@app.route('/admin/grupos/editar/<int:id_grupo>', methods=['POST'])
@permission_required('grupos.editar')
def admin_grupos_editar(id_grupo):
    nivel = request.form.get('nivel', '').strip()
    seccion = request.form.get('seccion', '').strip()
    anio_lectivo = request.form.get('anio_lectivo', '').strip()
    id_docente_guia = request.form.get('id_docente_guia', '').strip()

    exito, mensaje = editar_grupo(
        id_grupo,
        nivel,
        seccion,
        anio_lectivo,
        id_docente_guia
    )

    if exito:
        return redirect(
            url_for('admin_grupos', success='editado')
        )

    return redirect(
        url_for('admin_grupos', error=mensaje)
    )


@app.route('/admin/grupos/eliminar/<int:id_grupo>', methods=['POST'])
@permission_required('grupos.eliminar')
def admin_grupos_eliminar(id_grupo):
    exito, mensaje = eliminar_grupo(id_grupo)

    if exito:
        return redirect(
            url_for('admin_grupos', success='eliminado')
        )

    return redirect(
        url_for('admin_grupos', error=mensaje)
    )

if __name__ == '__main__':
    app.run(debug=True)
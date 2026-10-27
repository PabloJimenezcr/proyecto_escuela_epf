from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask import send_file

from controllers.teacher_controller import actualizar_docente, obtener_lista_docentes
from controllers.user_controller import (
    actualizar_contrasena_real,
    buscar_usuario_por_correo,
    crear_nuevo_usuario,
    registrar_token_real,
    registrar_usuario_por_admin
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
    obtener_estudiantes_por_grupo,
    obtener_grupos,
    obtener_docentes,
    obtener_materias,
    obtener_grupo_por_id,
    obtener_detalle_grupo,
    obtener_estudiantes_disponibles,
    crear_grupo,
    editar_grupo,
    eliminar_grupo,
    asignar_estudiante_a_grupo,
    asignar_docente_a_grupo,
    quitar_docente_de_grupo
)

from controllers.report_controller import (
    TIPOS,
    obtener_periodos,
    generar_reporte,
    exportar_csv
)

from controllers.teacher_controller import (
    obtener_lista_docentes,
    actualizar_docente,
    registrar_docente
)

from controllers.parent_controller import (
    PARENTESCOS,
    obtener_padres,
    obtener_estudiantes_activos,
    obtener_vinculos,
    registrar_padre_familia,
    crear_vinculo,
    eliminar_vinculo
)

from controllers.student_controller import (
    registrar_estudiante,
    obtener_estudiantes_registrados,
    obtener_grupos_para_estudiantes,
    actualizar_estudiante
)


app = Flask(__name__)
# llave de cifrado para proteger la sesion del usuario
app.secret_key = 'clave_secretaEPF'


# pagina de inicio

@app.route('/')
def index():
    return render_template('index.html')


# inicio de sesion

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        if 'recuperar_email' in request.form:

            correo_recuperar = request.form.get('recuperar_email')
            token = registrar_token_real(correo_recuperar)

            if token:
                return redirect(
                    url_for('restablecer', token=token)
                )

            return "<h3>El correo no está registrado o se encuentra inactivo.</h3>"

        correo_usuario = request.form.get('email')
        contrasena_usuario = request.form.get('password')

        usuario = buscar_usuario_por_correo(correo_usuario)

        if usuario:

            hash_bd = usuario['contrasena_hash']

            if isinstance(hash_bd, (bytes, bytearray)):
                hash_bd = hash_bd.decode('utf-8')

            if check_password_hash(hash_bd, contrasena_usuario):

                session['id_usuario'] = usuario['id_usuario']
                session['nombre_usuario'] = usuario['nombre']
                session['rol_usuario'] = usuario['nombre_rol']

                return redirect(url_for('dashboard'))

        return render_template(
            'login.html',
            error_login=True
        )

    return render_template('login.html')


# registro publico de usuarios

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        correo = request.form.get('email', '')

        if not correo.lower().endswith('@escuela.com'):
            return (
                "<h3>Error: El registro está restringido "
                "únicamente para correos institucionales autorizados.</h3>"
            )

        nombre = request.form.get('nombre')
        apellido1 = request.form.get('apellido1')
        apellido2 = request.form.get('apellido2')
        contrasena = request.form.get('password')
        telefono = request.form.get('telefono')

        id_rol = 3

        exito = crear_nuevo_usuario(
            nombre,
            apellido1,
            apellido2,
            correo,
            contrasena,
            telefono,
            id_rol
        )

        if exito:
            return redirect(url_for('login'))

        return render_template(
            'register.html',
            error_registro=True
        )

    return render_template('register.html')


# recuperacion de contraseña

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():

    if request.method == 'POST':

        correo = request.form.get('email')
        token = registrar_token_real(correo)

        if token:
            return redirect(
                url_for('restablecer', token=token)
            )

        return (
            "<h3>El correo electrónico ingresado "
            "no existe en el sistema escolar.</h3>"
        )

    return render_template('forgot_password.html')


# restablecer contraseña

@app.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer(token):

    if request.method == 'POST':

        nueva_clave = request.form.get('password')

        exito = actualizar_contrasena_real(
            token,
            nueva_clave
        )

        if exito:
            return (
                "<h3>Contraseña restablecida con éxito. "
                "Ya puedes ir a <a href='/login'>Iniciar Sesión</a>.</h3>"
            )

        return (
            "<h3>Error: El enlace de recuperación es inválido "
            "caducó o ya fue utilizado.</h3>"
        )

    return render_template(
        'reset_password.html',
        token=token
    )


# dashboard

@app.route('/dashboard')
def dashboard():

    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    rol_usuario = session.get('rol_usuario')

    if rol_usuario == 'Administrador':

        connection = get_db_connection()

        total_usuarios = 0
        total_estudiantes = 0
        total_docentes = 0
        total_grupos = 0
        cursor = None

        if connection:

            try:

                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM usuarios
                """)

                total_usuarios = cursor.fetchone()['total']

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM estudiantes
                """)

                total_estudiantes = cursor.fetchone()['total']

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM docentes
                """)

                total_docentes = cursor.fetchone()['total']

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

                if cursor:
                    cursor.close()

                connection.close()

        return render_template(
            'admin/dashboard.html',
            total_usuarios=total_usuarios,
            total_estudiantes=total_estudiantes,
            total_docentes=total_docentes,
            total_grupos=total_grupos
        )

    return render_template(
        'admin/dashboard.html',
        nombre=session.get('nombre_usuario'),
        rol=rol_usuario
    )


# cerrar sesion

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


# prueba de conexion

@app.route('/test-db')
def test_db():

    db = get_db_connection()

    if db and db.is_connected():
        db.close()
        return "¡Conexión a MySQL exitosa de forma correcta!"

    return "Error al conectar a la base de datos."


# gestion y consulta de usuarios

@app.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def users():

    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        nombre = request.form.get('nombre', '').strip()
        apellido1 = request.form.get('apellido1', '').strip()
        apellido2 = request.form.get('apellido2', '').strip()
        correo = request.form.get('email', '').strip()
        contrasena = request.form.get('password', '')
        telefono = request.form.get('telefono', '').strip()
        id_rol = request.form.get('id_rol', '').strip()

        if not correo or not correo.lower().endswith('@escuela.com'):

            flash(
                'El correo debe pertenecer al dominio @escuela.com',
                'danger'
            )

            return redirect(url_for('users'))

        if not id_rol.isdigit():

            flash(
                'Selecciona un rol válido',
                'danger'
            )

            return redirect(url_for('users'))

        exito = registrar_usuario_por_admin(
            nombre,
            apellido1,
            apellido2,
            correo,
            contrasena,
            telefono,
            int(id_rol)
        )

        if exito:
            flash(
                'Usuario registrado exitosamente',
                'success'
            )
        else:
            flash(
                'No fue posible registrar el usuario',
                'danger'
            )

        return redirect(url_for('users'))

    rol_seleccionado = request.args.get('rol', '').strip()

    if not rol_seleccionado.isdigit():
        rol_seleccionado = ''

    connection = get_db_connection()

    if not connection:

        flash(
            'No se pudo conectar a la base de datos',
            'danger'
        )

        return render_template(
            'admin/usuarios.html',
            users=[],
            roles=obtener_roles(),
            rol_seleccionado=rol_seleccionado
        )

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.apellido1,
                u.apellido2,
                u.correo,
                u.telefono,
                u.estado,
                u.id_rol,
                r.nombre AS nombre_rol
            FROM usuarios u
            INNER JOIN roles r
                ON u.id_rol = r.id_rol
        """

        parametros = ()

        if rol_seleccionado:

            query += """
                WHERE u.id_rol = %s
            """

            parametros = (
                int(rol_seleccionado),
            )

        query += """
            ORDER BY u.id_usuario DESC
        """

        cursor.execute(
            query,
            parametros
        )

        usuarios_bd = cursor.fetchall()
        roles_disponibles = obtener_roles()

        return render_template(
            'admin/usuarios.html',
            users=usuarios_bd,
            roles=roles_disponibles,
            rol_seleccionado=rol_seleccionado
        )

    except Exception as e:

        print(
            f'Error al consultar usuarios: {e}'
        )

        flash(
            'No fue posible consultar los usuarios',
            'danger'
        )

        return render_template(
            'admin/usuarios.html',
            users=[],
            roles=obtener_roles(),
            rol_seleccionado=rol_seleccionado
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()


# activar o desactivar usuarios

@app.route('/admin/users/toggle/<int:id_usuario>')
@admin_required
def toggle_user(id_usuario):

    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()

    if not db:
        flash(
            'No se pudo conectar a la base de datos',
            'danger'
        )
        return redirect(url_for('users'))

    cursor = None

    try:

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT estado
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (id_usuario,)
        )

        usuario = cursor.fetchone()

        if usuario:

            nuevo_estado = (
                'inactivo'
                if usuario['estado'] == 'activo'
                else 'activo'
            )

            cursor.execute(
                """
                UPDATE usuarios
                SET estado = %s
                WHERE id_usuario = %s
                """,
                (
                    nuevo_estado,
                    id_usuario
                )
            )

            db.commit()

        return redirect(url_for('users'))

    except Exception as e:

        db.rollback()

        print(f"Error al cambiar estado del usuario: {e}")

        flash(
            'No fue posible cambiar el estado del usuario',
            'danger'
        )

        return redirect(url_for('users'))

    finally:

        if cursor:
            cursor.close()

        db.close()


# gestion de roles

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


# gestion de grupos y secciones

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
            url_for(
                'admin_grupos',
                success='editado'
            )
        )

    return redirect(
        url_for(
            'admin_grupos',
            error=mensaje
        )
    )


@app.route('/admin/grupos/eliminar/<int:id_grupo>', methods=['POST'])
@permission_required('grupos.eliminar')
def admin_grupos_eliminar(id_grupo):

    exito, mensaje = eliminar_grupo(id_grupo)

    if exito:

        return redirect(
            url_for(
                'admin_grupos',
                success='eliminado'
            )
        )

    return redirect(
        url_for(
            'admin_grupos',
            error=mensaje
        )
    )


# detalle del grupo

@app.route('/admin/grupos/<int:id_grupo>', methods=['GET'])
@permission_required('grupos.ver')
def admin_grupos_detalle(id_grupo):

    grupo, estudiantes, docentes = obtener_detalle_grupo(id_grupo)

    if grupo is None:
        return redirect(
            url_for(
                'admin_grupos',
                error='El grupo no existe.'
            )
        )

    disponibles = obtener_estudiantes_disponibles(id_grupo)

    otros_grupos = [
        g for g in obtener_grupos()
        if g['id_grupo'] != id_grupo
        and g['anio_lectivo'] == grupo['anio_lectivo']
    ]

    return render_template(
        'admin/grupo_detalle.html',
        grupo=grupo,
        estudiantes=estudiantes,
        docentes=docentes,
        disponibles=disponibles,
        otros_grupos=otros_grupos,
        docentes_disponibles=obtener_docentes(),
        materias=obtener_materias(),
        puede_editar=True
    )


# asignar y mover estudiantes entre grupos

@app.route(
    '/admin/grupos/<int:id_grupo>/estudiantes/asignar',
    methods=['POST']
)
@permission_required('grupos.editar')
def admin_grupos_asignar_estudiante(id_grupo):

    id_estudiante = request.form.get('id_estudiante', '').strip()

    if not id_estudiante:

        return redirect(
            url_for(
                'admin_grupos_detalle',
                id_grupo=id_grupo,
                error='Selecciona un estudiante.'
            )
        )

    exito, mensaje = asignar_estudiante_a_grupo(
        id_estudiante,
        id_grupo
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_grupos_detalle',
            id_grupo=id_grupo,
            **{clave: mensaje}
        )
    )


@app.route('/admin/estudiantes/<int:id_estudiante>/mover', methods=['POST'])
@permission_required('grupos.editar')
def admin_estudiante_mover(id_estudiante):

    id_origen = request.form.get('id_grupo_origen', '').strip()
    id_destino = request.form.get('id_grupo_destino', '').strip()

    if not id_destino:

        return redirect(
            url_for(
                'admin_grupos_detalle',
                id_grupo=id_origen,
                error='Selecciona el grupo de destino.'
            )
        )

    exito, mensaje = asignar_estudiante_a_grupo(
        id_estudiante,
        id_destino
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_grupos_detalle',
            id_grupo=id_origen,
            **{clave: mensaje}
        )
    )


# asignar y quitar docentes de grupos

@app.route(
    '/admin/grupos/<int:id_grupo>/docentes/asignar',
    methods=['POST']
)
@permission_required('grupos.editar')
def admin_grupos_asignar_docente(id_grupo):

    id_docente = request.form.get('id_docente', '').strip()
    id_materia = request.form.get('id_materia', '').strip()

    if not id_docente or not id_materia:

        return redirect(
            url_for(
                'admin_grupos_detalle',
                id_grupo=id_grupo,
                error='Selecciona un docente y una materia.'
            )
        )

    exito, mensaje = asignar_docente_a_grupo(
        id_docente,
        id_materia,
        id_grupo
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_grupos_detalle',
            id_grupo=id_grupo,
            **{clave: mensaje}
        )
    )


@app.route(
    '/admin/grupos/<int:id_grupo>/docentes/quitar/<int:id_asignacion>',
    methods=['POST']
)
@permission_required('grupos.editar')
def admin_grupos_quitar_docente(id_grupo, id_asignacion):

    exito, mensaje = quitar_docente_de_grupo(
        id_asignacion,
        id_grupo
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_grupos_detalle',
            id_grupo=id_grupo,
            **{clave: mensaje}
        )
    )


# generar reportes

def _filtros_reporte():

    return {
        "tipo": request.args.get("tipo", "asistencia"),
        "id_grupo": request.args.get("grupo") or None,
        "id_periodo": request.args.get("periodo") or None,
        "desde": request.args.get("desde") or None,
        "hasta": request.args.get("hasta") or None,
    }


@app.route('/admin/reportes', methods=['GET'])
@admin_required
def admin_reportes():

    f = _filtros_reporte()

    titulo, columnas, filas = generar_reporte(
        f["tipo"],
        f["id_grupo"],
        f["id_periodo"],
        f["desde"],
        f["hasta"]
    )

    return render_template(
        'admin/reportes.html',
        tipos=TIPOS,
        filtros=f,
        grupos=obtener_grupos(),
        periodos=obtener_periodos(),
        titulo=titulo,
        columnas=columnas,
        filas=filas
    )


# exportar reportes

@app.route('/admin/reportes/exportar/<formato>', methods=['GET'])
@admin_required
def admin_reportes_exportar(formato):

    f = _filtros_reporte()

    titulo, columnas, filas = generar_reporte(
        f["tipo"],
        f["id_grupo"],
        f["id_periodo"],
        f["desde"],
        f["hasta"]
    )

    if not filas:

        return redirect(
            url_for(
                'admin_reportes',
                error='No hay datos para exportar.'
            )
        )

    nombre = f"{f['tipo']}_{datetime.now():%Y%m%d_%H%M}"

    if formato == 'csv':

        return send_file(
            exportar_csv(titulo, columnas, filas),
            as_attachment=True,
            download_name=f"{nombre}.csv",
            mimetype="text/csv"
        )

    return redirect(
        url_for(
            'admin_reportes',
            error='Formato de exportación no válido.'
        )
    )


# lista de estudiantes por grupo

@app.route('/admin/estudiantes-grupo', methods=['GET'])
@admin_required
def admin_estudiantes_grupo():

    grupos = obtener_grupos()

    id_grupo = request.args.get('grupo', '').strip()

    grupo_sel = None
    estudiantes = []

    if id_grupo.isdigit():

        grupo_sel = next(
            (
                g for g in grupos
                if g['id_grupo'] == int(id_grupo)
            ),
            None
        )

        if grupo_sel:
            estudiantes = obtener_estudiantes_por_grupo(
                int(id_grupo)
            )

    return render_template(
        'admin/estudiantes_grupo.html',
        grupos=grupos,
        grupo_sel=grupo_sel,
        estudiantes=estudiantes
    )


# consultar y actualizar docentes

@app.route('/admin/docentes', methods=['GET'])
@admin_required
def admin_docentes():

    return render_template(
        'admin/docentes.html',
        docentes=obtener_lista_docentes(),
        materias=obtener_materias(),
        grupos=obtener_grupos()
    )


@app.route('/admin/docentes/nuevo', methods=['POST'])
@admin_required
def admin_docentes_nuevo():

    exito, mensaje = registrar_docente(
        request.form.get('nombre'),
        request.form.get('apellido1'),
        request.form.get('apellido2'),
        request.form.get('correo'),
        request.form.get('telefono'),
        request.form.get('contrasena'),
        request.form.get('especialidad'),
        request.form.get('id_materia'),
        request.form.get('id_grupo')
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_docentes',
            **{clave: mensaje}
        )
    )


@app.route('/admin/docentes/editar/<int:id_docente>', methods=['POST'])
@admin_required
def admin_docentes_editar(id_docente):

    exito, mensaje = actualizar_docente(
        id_docente,
        request.form.get('nombre'),
        request.form.get('apellido1'),
        request.form.get('apellido2'),
        request.form.get('telefono'),
        request.form.get('especialidad')
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_docentes',
            **{clave: mensaje}
        )
    )


# epf-04-01 epf-04-02 registro y consulta de estudiantes

@app.route('/admin/estudiantes/registro', methods=['GET', 'POST'])
@admin_required
def admin_estudiantes_registro():

    if request.method == 'POST':

        exito, mensaje = registrar_estudiante(
            request.form.get('nombre'),
            request.form.get('apellido1'),
            request.form.get('apellido2'),
            request.form.get('correo'),
            request.form.get('telefono'),
            request.form.get('contrasena'),
            request.form.get('fecha_nacimiento'),
            request.form.get('id_grupo')
        )

        flash(
            mensaje,
            'success' if exito else 'danger'
        )

        return redirect(
            url_for('admin_estudiantes_registro')
        )

    return render_template(
        'admin/estudiantes.html',
        estudiantes=obtener_estudiantes_registrados(),
        grupos=obtener_grupos_para_estudiantes(),
        hoy=datetime.now().date().isoformat()
    )


@app.route(
    '/admin/estudiantes/<int:id_estudiante>/actualizar',
    methods=['POST']
)
@admin_required
def admin_estudiante_actualizar(id_estudiante):

    exito, mensaje = actualizar_estudiante(
        id_estudiante,
        request.form.get('nombre'),
        request.form.get('apellido1'),
        request.form.get('apellido2'),
        request.form.get('correo'),
        request.form.get('telefono'),
        request.form.get('fecha_nacimiento')
    )

    flash(
        mensaje,
        'success' if exito else 'danger'
    )

    return redirect(
        url_for('admin_estudiantes_registro')
    )


# vincular padres con estudiantes

@app.route('/admin/vinculos', methods=['GET'])
@admin_required
def admin_vinculos():

    return render_template(
        'admin/vinculos.html',
        padres=obtener_padres(),
        estudiantes=obtener_estudiantes_activos(),
        vinculos=obtener_vinculos(),
        parentescos=PARENTESCOS
    )


@app.route('/admin/padres/nuevo', methods=['POST'])
@admin_required
def admin_padres_nuevo():

    exito, mensaje = registrar_padre_familia(
        request.form.get('nombre'),
        request.form.get('apellido1'),
        request.form.get('apellido2'),
        request.form.get('correo'),
        request.form.get('telefono'),
        request.form.get('contrasena')
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_vinculos',
            **{clave: mensaje}
        )
    )


@app.route('/admin/vinculos/nuevo', methods=['POST'])
@admin_required
def admin_vinculos_nuevo():

    exito, mensaje = crear_vinculo(
        request.form.get('id_padre'),
        request.form.get('id_estudiante'),
        request.form.get('parentesco')
    )

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_vinculos',
            **{clave: mensaje}
        )
    )


@app.route('/admin/vinculos/eliminar/<int:id_vinculo>', methods=['POST'])
@admin_required
def admin_vinculos_eliminar(id_vinculo):

    exito, mensaje = eliminar_vinculo(id_vinculo)

    clave = 'success' if exito else 'error'

    return redirect(
        url_for(
            'admin_vinculos',
            **{clave: mensaje}
        )
    )


if __name__ == '__main__':
    app.run(debug=True)
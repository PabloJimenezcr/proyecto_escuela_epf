from functools import wraps
from flask import session, redirect, url_for

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. VERIFICAR SESIÓN ACTIVA
        if 'id_usuario' not in session:
            return redirect(url_for('login'))
            
        # 2. VERIFICAR PERMISOS DE ROLES AUTORIZADOS
        rol = session.get('rol_usuario')
        if rol not in ['Docente', 'Administrador']:
            return (
                """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>403 - Acceso denegado</title>
                    <style>
                        body {
                            margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
                            font-family: Arial, sans-serif; background: #f7f9fc; color: #17202a;
                        }
                        .error-container {
                            width: min(90%, 520px); padding: 40px; text-align: center; background: #ffffff;
                            border-radius: 20px; box-shadow: 0 20px 50px rgba(23, 63, 95, 0.14);
                        }
                        .error-icon {
                            width: 80px; height: 80px; margin: 0 auto 24px; display: flex; align-items: center;
                            justify-content: center; border-radius: 50%; background: #fff0f0; color: #d64545; font-size: 38px;
                        }
                        h1 { margin: 0 0 12px; font-size: 32px; }
                        p { margin: 0 0 28px; color: #667085; line-height: 1.6; }
                        .btn {
                            display: inline-block; padding: 13px 24px; border-radius: 10px; background: #173f5f;
                            color: #ffffff; text-decoration: none; font-weight: 600; transition: 0.3s ease;
                        }
                        .btn:hover { background: #0b253a; }
                    </style>
                </head>
                <body>
                    <div class="error-container">
                        <div class="error-icon">🔒</div>
                        <h1>Acceso denegado</h1>
                        <p>
                            No tienes permisos para acceder a esta sección. 
                            Esta funcionalidad está disponible únicamente para el personal docente autorizado.
                        </p>
                        <a href="/dashboard" class="btn">Volver al dashboard</a>
                    </div>
                </body>
                </html>
                """
            ), 403
            
        # 3. USUARIO AUTORIZADO PASA CON ÉXITO
        return f(*args, **kwargs)
        
    return decorated_function
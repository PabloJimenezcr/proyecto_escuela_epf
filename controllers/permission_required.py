from functools import wraps

from flask import session, redirect, url_for

from controllers.role_controller import usuario_tiene_permiso


def permission_required(codigo_permiso):
    """Protege una ruta según un permiso específico"""

    def decorator(route_function):

        @wraps(route_function)
        def wrapper(*args, **kwargs):

            
            # 1. verifica sesión
            

            if 'id_usuario' not in session:
                return redirect(
                    url_for('login')
                )


            
            # 2. verifica permiso
            

            tiene_permiso = usuario_tiene_permiso(
                session['id_usuario'],
                codigo_permiso
            )

            if not tiene_permiso:

                return (
                    """
                    <!DOCTYPE html>
                    <html lang="es">

                    <head>

                        <meta charset="UTF-8">

                        <meta
                            name="viewport"
                            content="width=device-width, initial-scale=1.0"
                        >

                        <title>403 - Acceso denegado</title>

                        <style>

                            body {
                                margin: 0;
                                min-height: 100vh;

                                display: flex;
                                align-items: center;
                                justify-content: center;

                                background: #f7f9fc;

                                color: #17202a;

                                font-family: Arial, sans-serif;
                            }

                            .permission-error {
                                width: min(90%, 520px);

                                padding: 42px;

                                text-align: center;

                                background: #ffffff;

                                border-radius: 22px;

                                box-shadow:
                                    0 20px 50px
                                    rgba(23, 63, 95, 0.14);
                            }

                            .permission-icon {
                                width: 76px;
                                height: 76px;

                                margin: 0 auto 22px;

                                display: flex;
                                align-items: center;
                                justify-content: center;

                                border-radius: 50%;

                                background: #fff0f0;

                                color: #d64545;

                                font-size: 34px;
                            }

                            h1 {
                                margin: 0 0 12px;

                                font-size: 30px;
                            }

                            p {
                                margin: 0 0 26px;

                                color: #667085;

                                line-height: 1.6;
                            }

                            a {
                                display: inline-flex;

                                padding: 13px 22px;

                                border-radius: 10px;

                                background: #173f5f;

                                color: #ffffff;

                                text-decoration: none;

                                font-weight: 600;
                            }

                        </style>

                    </head>

                    <body>

                        <div class="permission-error">

                            <div class="permission-icon">
                                🔒
                            </div>

                            <h1>
                                Acceso denegado
                            </h1>

                            <p>
                                Tu perfil no tiene el permiso necesario
                                para realizar esta acción.
                            </p>

                            <a href="/dashboard">
                                Volver al dashboard
                            </a>

                        </div>

                    </body>

                    </html>
                    """
                ), 403

            return route_function(*args, **kwargs)

        return wrapper

    return decorator
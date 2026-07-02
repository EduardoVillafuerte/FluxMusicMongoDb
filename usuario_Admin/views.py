from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

# Tu función actual se queda igual
def listar_usuarios(request):
    with connection.cursor() as cursor:
        cursor.execute("EXEC Persona.sp_ConsultarUsuarios")
        columnas = [col[0] for col in cursor.description]
        usuarios = [dict(zip(columnas, row)) for row in cursor.fetchall()]

    return render(request, 'PanelAdmin.html', {'usuarios': usuarios})

# --- AÑADE ESTA NUEVA VISTA AQUÍ ---
def actualizar_rol_usuario(request):
    if request.method == 'POST':
        # Recibimos los datos ocultos que manda el Modal
        usuario_id = request.POST.get('usuario_id')
        nuevo_rol = request.POST.get('nuevo_rol')

        if usuario_id and nuevo_rol:
            try:
                with connection.cursor() as cursor:
                    # Ejecutamos el SP que acabamos de crear en SQL Server
                    cursor.execute(
                        "EXEC Persona.sp_ActualizarRolUsuario @usuarioId=%s, @nuevoRol=%s",
                        [usuario_id, nuevo_rol]
                    )
                # Mensaje de éxito que ya tienes configurado en tu Mainbase.html
                messages.success(request, f"¡Rol actualizado a {nuevo_rol} correctamente!")
            except Exception as e:
                # Si SQL Server rechaza el cambio, le avisamos al admin
                messages.error(request, f"Error en la base de datos: {e}")
        else:
            messages.error(request, "Faltan datos para procesar la solicitud.")

    # Al terminar, recargamos la tabla de usuarios
    return redirect('listar_usuarios')
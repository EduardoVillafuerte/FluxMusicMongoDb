from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.db_connection import get_db 

def listar_usuarios(request):
    db = get_db()
    usuarios = list(db['usuarios'].find())
    
    return render(request, 'PanelAdmin.html', {'usuarios': usuarios})

def actualizar_rol_usuario(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        nuevo_rol = request.POST.get('nuevo_rol')

        if usuario_id and nuevo_rol:
            try:
                db = get_db()
                coleccion_usuarios = db['usuarios']
                
                resultado = coleccion_usuarios.update_one(
                    {'usuarioId': int(usuario_id)}, 
                    {'$set': {'rolPerfil': nuevo_rol}}
                )
                
                    
            except Exception as e:
                messages.error(request, f"Error en la base de datos: {e}")
        else:
            messages.error(request, "Faltan datos para procesar la solicitud.")

    return redirect('listar_usuarios')
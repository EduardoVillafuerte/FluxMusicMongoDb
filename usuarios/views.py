"""
Views para la app 'usuarios' en FluxMusic
Adaptado de SQL Server a MongoDB - Solo funciones necesarias
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Conexión a MongoDB Atlas
client = MongoClient('mongodb+srv://Admin:Udla@clusterudla03.yq570z6.mongodb.net/?retryWrites=true&w=majority&appName=ClusterUdla03&authSource=admin')
db = client['FluxMusicMongoDb']

# ==========================================
# VISTA: MI PERFIL
# ==========================================

def mi_perfil(request):
    """
    Obtiene y muestra el perfil del usuario logueado
    """
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        # Obtener usuario de MongoDB usando usuarioId (numérico)
        usuario = db.usuarios.find_one(
            {'usuarioId': usuario_id},
            {'password': 0}  # No retornar contraseña
        )
        
        if not usuario:
            messages.error(request, 'Usuario no encontrado')
            return redirect('login')
        
        return render(request, 'usuario/perfil.html', {'usuario': usuario})
    
    except PyMongoError as e:
        messages.error(request, f'Error al obtener perfil: {str(e)}')
        return redirect('/Main/')


# ==========================================
# VISTA: EDITAR PERFIL
# ==========================================

def editar_perfil(request):
    """
    Permite editar el nickname del usuario
    """
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    if request.method == 'POST':
        nuevo_nickname = request.POST.get('nickname', '').strip()
        
        # Validar que no esté vacío
        if not nuevo_nickname:
            messages.error(request, 'El nickname no puede estar vacío')
            return render(request, 'usuario/editar_perfil.html')
        
        # Validar que no sea muy corto
        if len(nuevo_nickname) < 3:
            messages.error(request, 'El nickname debe tener al menos 3 caracteres')
            return render(request, 'usuario/editar_perfil.html')
        
        try:
            # Verificar que el nickname no esté en uso por otro usuario
            nickname_existente = db.usuarios.find_one({
                'nickname': nuevo_nickname,
                'usuarioId': {'$ne': usuario_id}
            })
            
            if nickname_existente:
                messages.error(request, 'Este nickname ya está en uso')
                return render(request, 'usuario/editar_perfil.html')
            
            # Actualizar nickname en MongoDB
            resultado = db.usuarios.update_one(
                {'usuarioId': usuario_id},
                {'$set': {'nickname': nuevo_nickname}}
            )
            
            if resultado.modified_count > 0:
                # Actualizar sesión
                request.session['nickname'] = nuevo_nickname
                messages.success(request, 'Perfil actualizado correctamente')
                return redirect('usuarios:mi_perfil')
            else:
                messages.error(request, 'No se pudo actualizar el perfil')
                return render(request, 'usuario/editar_perfil.html')
        
        except PyMongoError as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
            return render(request, 'usuario/editar_perfil.html')
    
    # GET: Mostrar formulario
    try:
        usuario = db.usuarios.find_one(
            {'usuarioId': usuario_id},
            {'password': 0}
        )
        return render(request, 'usuario/editar_perfil.html', {'usuario': usuario})
    
    except PyMongoError as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('/Main/')


# ==========================================
# VISTA: CAMBIAR CONTRASEÑA
# ==========================================

def cambiar_password(request):
    """
    Permite cambiar la contraseña del usuario
    """
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual', '').strip()
        password_nueva = request.POST.get('password_nueva', '').strip()
        password_confirmar = request.POST.get('password_confirmar', '').strip()
        
        # Validar que no estén vacíos
        if not password_actual or not password_nueva or not password_confirmar:
            messages.error(request, 'Por favor completa todos los campos')
            return render(request, 'usuario/cambiar_password.html')
        
        # Validar que las nuevas contraseñas coincidan
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return render(request, 'usuario/cambiar_password.html')
        
        # Validar que la nueva contraseña sea diferente
        if password_nueva == password_actual:
            messages.error(request, 'La nueva contraseña debe ser diferente a la actual')
            return render(request, 'usuario/cambiar_password.html')
        
        # Validar que la nueva contraseña tenga al menos 6 caracteres
        if len(password_nueva) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return render(request, 'usuario/cambiar_password.html')
        
        try:
            # Obtener usuario actual
            usuario = db.usuarios.find_one({'usuarioId': usuario_id})
            
            if not usuario:
                messages.error(request, 'Usuario no encontrado')
                return render(request, 'usuario/cambiar_password.html')
            
            # Verificar que la contraseña actual sea correcta
            if usuario.get('password') != password_actual:
                messages.error(request, 'La contraseña actual es incorrecta')
                return render(request, 'usuario/cambiar_password.html')
            
            # Actualizar contraseña en MongoDB
            resultado = db.usuarios.update_one(
                {'usuarioId': usuario_id},
                {'$set': {'password': password_nueva}}
            )
            
            if resultado.modified_count > 0:
                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('usuarios:mi_perfil')
            else:
                messages.error(request, 'No se pudo actualizar la contraseña')
                return render(request, 'usuario/cambiar_password.html')
        
        except PyMongoError as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'usuario/cambiar_password.html')
    
    # GET: Mostrar formulario
    return render(request, 'usuario/cambiar_password.html')


# ==========================================
# VISTA: ELIMINAR CUENTA
# ==========================================

def eliminar_cuenta(request):
    """
    Elimina la cuenta del usuario
    """
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Eliminar usuario de MongoDB usando usuarioId
            resultado = db.usuarios.delete_one({'usuarioId': usuario_id})
            
            if resultado.deleted_count > 0:
                # Limpiar sesión
                request.session.flush()
                messages.success(request, 'Tu cuenta ha sido eliminada correctamente')
                return redirect('login')
            else:
                messages.error(request, 'No se pudo eliminar la cuenta')
                return redirect('usuarios:editar_perfil')
        
        except PyMongoError as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
            return redirect('usuarios:editar_perfil')
    
    # GET: Redirigir a editar perfil (donde está el botón)
    return redirect('usuarios:editar_perfil')


# ==========================================
# VISTA: LOGOUT
# ==========================================

def logout_view(request):
    """
    Cierra la sesión del usuario
    """
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')
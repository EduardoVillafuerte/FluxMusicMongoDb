import hashlib
from django.shortcuts import render, redirect
from django.contrib import messages
from pymongo import MongoClient
from usuarios.db_connection import get_db

def login_custom(request):
    if request.method == 'POST':
        # Limpieza de espacios y forzar minúsculas en email
        email_input = request.POST.get('email', '').strip().lower()
        password_input = request.POST.get('password', '')
        
        # Encriptamos la contraseña entrante para que coincida con la BD
        hashed_password = hashlib.sha256(password_input.encode('utf-8')).hexdigest().upper()
        
        try:
            db = get_db()
            coleccion_usuarios = db['usuarios']
            
            # Buscamos que coincida el email Y la contraseña ya hasheada
            usuario_valido = coleccion_usuarios.find_one({
                'email': email_input,
                'password': hashed_password
            })
            
            # En login_custom
            if usuario_valido:
                # Limpiamos cualquier dato de sesión de un login anterior
                # (evita que queden mezclados nickname/rol/plan de otra cuenta)
                request.session.flush()

                request.session['usuario_id'] = usuario_valido.get('usuarioId')
                request.session['nickname'] = usuario_valido.get('nickname', 'Usuario')
                request.session['rol'] = usuario_valido.get('rolPerfil', 'Oyente') # Permisos
                request.session['plan_tipo'] = usuario_valido.get('planActivo', 'Free') # Beneficios
                return redirect('/Main/')
            else:
                messages.error(request, "El correo electrónico o la contraseña son incorrectos.")
                
        except Exception as e:
            messages.error(request, f"Error interno de conexión: {str(e)}")
            
    return render(request, 'login.html')


def registro_view(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip()
        email = request.POST.get('email', '').strip().lower()
        pais = request.POST.get('pais', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden. Inténtalo de nuevo.')
            return render(request, 'registrarse.html')

        rol_perfil = 'Oyente'

        # Encriptamos la contraseña del nuevo usuario ANTES de guardarla
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest().upper()

        try:
            db = get_db()
            coleccion_usuarios = db['usuarios']
            
            # Verificar si el correo ya existe
            if coleccion_usuarios.find_one({'email': email}):
                messages.error(request, 'Este correo ya está registrado.')
                return render(request, 'registrarse.html')

            # Obtener el siguiente usuarioId
            ultimo_usuario = coleccion_usuarios.find_one(sort=[('usuarioId', -1)])
            nuevo_usuario_id = (ultimo_usuario['usuarioId'] + 1) if ultimo_usuario else 1001

            # Estructurar el nuevo documento guardando el HASH, no el texto plano
            nuevo_usuario = {
                'usuarioId': nuevo_usuario_id,
                'nickname': nickname,
                'email': email,
                'pais': pais,
                'password': hashed_password,
                'rolPerfil': rol_perfil
            }
            
            coleccion_usuarios.insert_one(nuevo_usuario)
            
            messages.success(request, '¡Cuenta creada con éxito! Ya puedes iniciar sesión.')
            return redirect('login') 

        except Exception as e:
            messages.error(request, f'Ocurrió un error al crear la cuenta: {str(e)}')
            return render(request, 'registrarse.html')

    return render(request, 'registrarse.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')
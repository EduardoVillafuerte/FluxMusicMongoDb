from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.db_connection import get_db 

def listar_usuarios(request):
    db = get_db()
    usuarios = list(db['usuarios'].find())

    # ── Canciones del catálogo (con álbum y artista) ──────
    canciones = []
    try:
        canciones = list(db['canciones'].aggregate([
            {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                         'foreignField': 'albumID', 'as': 'albumData'}},
            {'$unwind': {'path': '$albumData', 'preserveNullAndEmptyArrays': True}},
            {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': {'path': '$artistaData', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'CancionId': '$cancionId',
                'Cancion': '$tituloCancion',
                'Album': {'$ifNull': ['$albumData.tituloAlbum', 'Sin álbum']},
                'Artista': {'$ifNull': ['$artistaData.perfilArtista.nombreProfesional', 'Desconocido']},
                'Duracion': '$duracionTotal'
            }},
            {'$sort': {'Cancion': 1}}
        ]))
    except Exception as e:
        print(f"Error cargando canciones: {e}")

    # ── Álbumes del catálogo (con artista y total de canciones) ──
    albumes = []
    try:
        albumes = list(db['catalogo'].aggregate([
            {'$lookup': {'from': 'usuarios', 'localField': 'artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': {'path': '$artistaData', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'AlbumId': '$albumID',
                'Album': '$tituloAlbum',
                'Artista': {'$ifNull': ['$artistaData.perfilArtista.nombreProfesional', 'Desconocido']},
                'Fecha': '$fechaLanzamiento'
            }},
            {'$sort': {'Album': 1}}
        ]))

        canciones_por_album = {}
        for c in db['canciones'].find({}, {'albumId': 1}):
            canciones_por_album[c['albumId']] = canciones_por_album.get(c['albumId'], 0) + 1
        for a in albumes:
            a['TotalCanciones'] = canciones_por_album.get(a['AlbumId'], 0)
    except Exception as e:
        print(f"Error cargando álbumes: {e}")

    # ── Suma total histórica de regalías pagadas ──────────
    regalias_totales = 0
    try:
        resultado = list(db['liquidaciones'].aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$montoPagarUSD'}}}
        ]))
        if resultado:
            regalias_totales = round(resultado[0].get('total', 0), 2)
    except Exception as e:
        print(f"Error calculando regalías totales: {e}")

    context = {
        'usuarios': usuarios,
        'canciones': canciones,
        'albumes': albumes,
        'regalias_totales': regalias_totales,
    }
    return render(request, 'PanelAdmin.html', context)

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



# ============================================================
# NUEVO: Panel Admin — eliminar canción del catálogo
# ============================================================
def eliminar_cancion_admin(request):
    if request.method != 'POST':
        return redirect('listar_usuarios')

    if request.session.get('rol') != 'Administrador':
        messages.error(request, "No autorizado.")
        return redirect('listar_usuarios')

    cancion_id = request.POST.get('cancion_id')
    if not cancion_id:
        messages.error(request, "Falta indicar la canción a eliminar.")
        return redirect('listar_usuarios')

    db = get_db()
    try:
        cancion_id = int(cancion_id)
        cancion = db['canciones'].find_one({'cancionId': cancion_id})

        if not cancion:
            messages.error(request, "La canción no existe.")
            return redirect('listar_usuarios')

        db['canciones'].delete_one({'cancionId': cancion_id})

        # Limpieza de referencias en otras colecciones
        db['playlists'].update_many({}, {'$pull': {'cancionesIds': cancion_id}})
        db['interacciones'].delete_many({'cancionId': cancion_id})
        db['reproducciones'].delete_many({'cancionId': cancion_id})

        messages.success(request, f'"{cancion.get("tituloCancion", "La canción")}" fue eliminada correctamente.')
    except Exception as e:
        messages.error(request, f"Error al eliminar la canción: {e}")

    return redirect('listar_usuarios')


# ============================================================
# NUEVO: Panel Admin — eliminar álbum (y sus canciones) del catálogo
# ============================================================
def eliminar_album_admin(request):
    if request.method != 'POST':
        return redirect('listar_usuarios')

    if request.session.get('rol') != 'Administrador':
        messages.error(request, "No autorizado.")
        return redirect('listar_usuarios')

    album_id = request.POST.get('album_id')
    if not album_id:
        messages.error(request, "Falta indicar el álbum a eliminar.")
        return redirect('listar_usuarios')

    db = get_db()
    try:
        album_id = int(album_id)
        album = db['catalogo'].find_one({'albumID': album_id})

        if not album:
            messages.error(request, "El álbum no existe.")
            return redirect('listar_usuarios')

        canciones_del_album = [
            c['cancionId'] for c in db['canciones'].find({'albumId': album_id}, {'cancionId': 1})
        ]

        # Elimina las canciones del álbum y sus referencias
        if canciones_del_album:
            db['canciones'].delete_many({'albumId': album_id})
            db['playlists'].update_many({}, {'$pull': {'cancionesIds': {'$in': canciones_del_album}}})
            db['interacciones'].delete_many({'cancionId': {'$in': canciones_del_album}})
            db['reproducciones'].delete_many({'cancionId': {'$in': canciones_del_album}})

        db['catalogo'].delete_one({'albumID': album_id})

        messages.success(
            request,
            f'El álbum "{album.get("tituloAlbum", "")}" y sus {len(canciones_del_album)} canción(es) fueron eliminados.'
        )
    except Exception as e:
        messages.error(request, f"Error al eliminar el álbum: {e}")

    return redirect('listar_usuarios')
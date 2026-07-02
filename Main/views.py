import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from usuarios.db_connection import get_db
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_protect


@ensure_csrf_cookie

@ensure_csrf_cookie
def dashboard_negocio(request):
    oyente_id = request.session.get('usuario_id')
    rol = request.session.get('rol')    
    db = get_db()

    # ========= HISTORIAL RECIENTE =========
    historial_reciente = []
    if oyente_id:
        try:
            historial_reciente = list(db['reproducciones'].aggregate([
                {'$match': {'oyenteId': oyente_id}},
                {'$sort': {'fechaHora': -1}},
                {'$limit': 9},
                {'$lookup': {'from': 'canciones', 'localField': 'cancionId',
                             'foreignField': 'cancionId', 'as': 'cancionData'}},
                {'$unwind': '$cancionData'},
                {'$lookup': {'from': 'catalogo', 'localField': 'cancionData.albumId',
                             'foreignField': 'albumID', 'as': 'albumData'}},
                {'$unwind': '$albumData'},
                {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                             'foreignField': 'usuarioId', 'as': 'artistaData'}},
                {'$unwind': '$artistaData'},
                {'$project': {
                    'CancionId': '$cancionData.cancionId',
                    'Cancion': '$cancionData.tituloCancion',
                    'Duracion': '$cancionData.duracionTotal',
                    'Artista': '$artistaData.perfilArtista.nombreProfesional',
                    'ArtistaId': '$artistaData.usuarioId'
                }}
            ]))
        except Exception as e:
            print(f"Error historial_reciente: {e}")

    # ========= TOP CONSUMO =========
    reporte_consumo = []
    if oyente_id:
        try:
            reporte_consumo = list(db['reproducciones'].aggregate([
                {'$match': {'oyenteId': oyente_id}},
                {'$group': {'_id': '$cancionId', 'Frecuencia': {'$sum': 1}}},
                {'$sort': {'Frecuencia': -1}},
                {'$limit': 5},
                {'$lookup': {'from': 'canciones', 'localField': '_id',
                             'foreignField': 'cancionId', 'as': 'cancionData'}},
                {'$unwind': '$cancionData'},
                {'$lookup': {'from': 'catalogo', 'localField': 'cancionData.albumId',
                             'foreignField': 'albumID', 'as': 'albumData'}},
                {'$unwind': '$albumData'},
                {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                             'foreignField': 'usuarioId', 'as': 'artistaData'}},
                {'$unwind': '$artistaData'},
                {'$project': {
                    'CancionId': '$cancionData.cancionId',
                    'Cancion': '$cancionData.tituloCancion',
                    'Duracion': '$cancionData.duracionTotal',
                    'Artista': '$artistaData.perfilArtista.nombreProfesional',
                    'ArtistaId': '$artistaData.usuarioId',
                    'Frecuencia': 1
                }}
            ]))
        except Exception as e:
            print(f"Error reporte_consumo: {e}")

    # ========= RECOMENDACIONES =========
    recomendaciones = []
    if oyente_id:
        try:
            escuchadas_ids = [
                r['cancionId'] for r in db['reproducciones'].find(
                    {'oyenteId': oyente_id}, {'cancionId': 1}
                )
            ]
            recomendaciones = list(db['canciones'].aggregate([
                {'$match': {'cancionId': {'$nin': escuchadas_ids}}},
                {'$sample': {'size': 6}},
                {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                             'foreignField': 'albumID', 'as': 'albumData'}},
                {'$unwind': '$albumData'},
                {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                             'foreignField': 'usuarioId', 'as': 'artistaData'}},
                {'$unwind': '$artistaData'},
                {'$project': {
                    'CancionId': '$cancionId',
                    'Recomendacion': '$tituloCancion',
                    'Duracion': '$duracionTotal',
                    'Artista': '$artistaData.perfilArtista.nombreProfesional',
                    'ArtistaId': '$artistaData.usuarioId',
                    'Genero_Musical': {
                        '$ifNull': [{'$arrayElemAt': ['$generos.genero', 0]}, 'Varios']
                    }
                }}
            ]))
        except Exception as e:
            print(f"Error recomendaciones: {e}")

    # ========= REGALÍAS =========
    reporte_regalias = []
    if rol in ('Administrador', 'Artista', 'Discografica'):
        try:
            match_stage = {'artistaId': oyente_id} if rol == 'Artista' else {}
            reporte_regalias = list(db['liquidaciones'].aggregate([
                {'$match': match_stage},
                {'$lookup': {'from': 'usuarios', 'localField': 'artistaId',
                             'foreignField': 'usuarioId', 'as': 'artistaData'}},
                {'$unwind': '$artistaData'},
                {'$project': {
                    'Artista': '$artistaData.perfilArtista.nombreProfesional',
                    'PagoTotalUSD': '$montoPagarUSD'
                }}
            ]))
        except Exception as e:
            print(f"Error reporte_regalias: {e}")

    # ========= ADN MUSICAL =========
    adn_musical = {
        'actividad_pct': 0,
        'genero_favorito': 'Sin datos',
        'genero_pct': 0,
        'artista_favorito': 'Sin datos',
        'artista_pct': 0,
        'mood': 'Sin datos',
        'mood_pct': 0,
    }
    if oyente_id:
        try:
            total_plays = db['reproducciones'].count_documents({'oyenteId': oyente_id})

            if total_plays > 0:
                adn_musical['actividad_pct'] = min(100, round((total_plays / 20) * 100))

                genero_stats = list(db['reproducciones'].aggregate([
                    {'$match': {'oyenteId': oyente_id}},
                    {'$lookup': {'from': 'canciones', 'localField': 'cancionId',
                                 'foreignField': 'cancionId', 'as': 'cancionData'}},
                    {'$unwind': '$cancionData'},
                    {'$project': {
                        'genero': {'$ifNull': [{'$arrayElemAt': ['$cancionData.generos.genero', 0]}, 'Variado']}
                    }},
                    {'$group': {'_id': '$genero', 'count': {'$sum': 1}}},
                    {'$sort': {'count': -1}}
                ]))
                if genero_stats:
                    top_genero = genero_stats[0]
                    adn_musical['genero_favorito'] = top_genero['_id']
                    adn_musical['genero_pct'] = round((top_genero['count'] / total_plays) * 100)
                    if len(genero_stats) > 1:
                        segundo = genero_stats[1]
                        adn_musical['mood'] = segundo['_id']
                        adn_musical['mood_pct'] = round((segundo['count'] / total_plays) * 100)
                    else:
                        adn_musical['mood'] = top_genero['_id']
                        adn_musical['mood_pct'] = adn_musical['genero_pct']

                artista_stats = list(db['reproducciones'].aggregate([
                    {'$match': {'oyenteId': oyente_id}},
                    {'$lookup': {'from': 'canciones', 'localField': 'cancionId',
                                 'foreignField': 'cancionId', 'as': 'cancionData'}},
                    {'$unwind': '$cancionData'},
                    {'$lookup': {'from': 'catalogo', 'localField': 'cancionData.albumId',
                                 'foreignField': 'albumID', 'as': 'albumData'}},
                    {'$unwind': '$albumData'},
                    {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                                 'foreignField': 'usuarioId', 'as': 'artistaData'}},
                    {'$unwind': '$artistaData'},
                    {'$group': {
                        '_id': '$artistaData.usuarioId',
                        'nombre': {'$first': '$artistaData.perfilArtista.nombreProfesional'},
                        'count': {'$sum': 1}
                    }},
                    {'$sort': {'count': -1}}
                ]))
                if artista_stats:
                    top_artista = artista_stats[0]
                    adn_musical['artista_favorito'] = top_artista['nombre']
                    adn_musical['artista_pct'] = round((top_artista['count'] / total_plays) * 100)
        except Exception as e:
            print(f"Error calculando ADN musical: {e}")

    context = {
        'nickname': request.session.get('nickname'),
        'role': rol,
        'reporte_regalias': reporte_regalias,
        'reporte_consumo': reporte_consumo,
        'recomendaciones': recomendaciones,
        'historial_reciente': historial_reciente,
        'adn_musical': adn_musical,
    }
    return render(request, 'Main.html', context)


def mi_biblioteca(request):
    if 'usuario_id' not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tu biblioteca.")
        return redirect('login')

    oyente_id = request.session['usuario_id']
    db = get_db()

    playlists, albumes, artistas, mis_gustas = [], [], [], []

    try:

        albumes = list(db['interacciones'].aggregate([
            {'$match': {'oyenteId': oyente_id, 'tipoInteraccion': 'Guardar'}},
            {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                         'foreignField': 'albumID', 'as': 'albumData'}},
            {'$unwind': '$albumData'},
            {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': '$artistaData'},
            {'$project': {
                'Album_Guardado': '$albumData.tituloAlbum',
                'Artista': '$artistaData.perfilArtista.nombreProfesional'
            }}
        ]))

        artistas = list(db['interacciones'].aggregate([
            {'$match': {'oyenteId': oyente_id, 'tipoInteraccion': 'Seguir'}},
            {'$lookup': {'from': 'usuarios', 'localField': 'artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': '$artistaData'},
            {'$lookup': {'from': 'usuarios', 'localField': 'artistaData.perfilArtista.discograficaId',
                         'foreignField': 'usuarioId', 'as': 'discograficaData'}},
            {'$unwind': {'path': '$discograficaData', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'Artista_Seguido': '$artistaData.perfilArtista.nombreProfesional',
                'Discografica': {'$ifNull': ['$discograficaData.nickname', 'Independiente']}
            }}
        ]))

        # ========= NUEVO: TUS ME GUSTAS =========
        mis_gustas = list(db['interacciones'].aggregate([
            {'$match': {'oyenteId': oyente_id, 'tipoInteraccion': 'Like'}},
            {'$lookup': {'from': 'canciones', 'localField': 'cancionId',
                         'foreignField': 'cancionId', 'as': 'cancionData'}},
            {'$unwind': '$cancionData'},
            {'$lookup': {'from': 'catalogo', 'localField': 'cancionData.albumId',
                         'foreignField': 'albumID', 'as': 'albumData'}},
            {'$unwind': '$albumData'},
            {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': '$artistaData'},
            {'$project': {
                'CancionId': '$cancionData.cancionId',
                'Cancion': '$cancionData.tituloCancion',
                'Artista': '$artistaData.perfilArtista.nombreProfesional'
            }}
        ]))

    except Exception as e:
        print(f"Error al cargar la biblioteca desde MongoDB: {e}")
        messages.error(request, "Hubo un error al cargar tu biblioteca. Inténtalo de nuevo más tarde.")

    context = {
        'albumes': albumes,
        'artistas': artistas,
        'mis_gustas': mis_gustas,
    }
    return render(request, 'Biblioteca.html', context)


# ============================================================
# Registra una reproducción en Mongo (historial en vivo)
# ============================================================
def registrar_reproduccion(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        cancion_id = int(data.get('cancionId'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'cancionId inválido'}, status=400)

    db = get_db()

    ultimo_log = db['reproducciones'].find_one(sort=[('logId', -1)])
    nuevo_log_id = (ultimo_log['logId'] + 1) if ultimo_log else 1

    db['reproducciones'].insert_one({
        'logId': nuevo_log_id,
        'oyenteId': oyente_id,
        'cancionId': cancion_id,
        'fechaHora': datetime.now().isoformat(),
        'segundosEscuchado': 30,
        'aplicarRegalia': True
    })

    return JsonResponse({'ok': True})


# ============================================================
# Agrega una canción a "Tus Me Gustas" (Like)
# ============================================================
def agregar_a_biblioteca(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        cancion_id = int(data.get('cancionId'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'cancionId inválido'}, status=400)

    db = get_db()

    ya_existe = db['interacciones'].find_one({
        'oyenteId': oyente_id, 'cancionId': cancion_id, 'tipoInteraccion': 'Like'
    })
    if ya_existe:
        return JsonResponse({'ok': True, 'mensaje': 'Ya estaba en tu biblioteca'})

    ultimo = db['interacciones'].find_one(sort=[('interaccionID', -1)])
    nuevo_id = (ultimo['interaccionID'] + 1) if ultimo else 1

    db['interacciones'].insert_one({
        'interaccionID': nuevo_id,
        'tipoInteraccion': 'Like',
        'oyenteId': oyente_id,
        'cancionId': cancion_id
    })

    return JsonResponse({'ok': True, 'mensaje': 'Agregado a tu biblioteca'})


# ============================================================
# NUEVO: Seguir a un artista desde el reproductor
# ============================================================
def seguir_artista(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        artista_id = int(data.get('artistaId'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'artistaId inválido'}, status=400)

    db = get_db()

    ya_existe = db['interacciones'].find_one({
        'oyenteId': oyente_id, 'artistaId': artista_id, 'tipoInteraccion': 'Seguir'
    })
    if ya_existe:
        return JsonResponse({'ok': True, 'mensaje': 'Ya sigues a este artista'})

    ultimo = db['interacciones'].find_one(sort=[('interaccionID', -1)])
    nuevo_id = (ultimo['interaccionID'] + 1) if ultimo else 1

    db['interacciones'].insert_one({
        'interaccionID': nuevo_id,
        'tipoInteraccion': 'Seguir',
        'oyenteId': oyente_id,
        'artistaId': artista_id
    })

    return JsonResponse({'ok': True, 'mensaje': 'Ahora sigues a este artista'})

# ============================================================
# NUEVO: Crear una playlist nueva
# ============================================================
def crear_playlist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    if not nombre:
        return JsonResponse({'error': 'El nombre no puede estar vacío'}, status=400)

    db = get_db()

    ultimo = db['playlists'].find_one(sort=[('playlistID', -1)])
    nuevo_id = (ultimo['playlistID'] + 1) if ultimo else 1

    db['playlists'].insert_one({
        'playlistID': nuevo_id,
        'nombrePlaylist': nombre,
        'oyenteId': oyente_id,
        'cancionesIds': []
    })

    return JsonResponse({'ok': True, 'playlistID': nuevo_id, 'nombre': nombre})


# ============================================================
# NUEVO: Buscador global (topbar)
# ============================================================
def buscar_canciones(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'resultados': []})

    db = get_db()
    try:
        resultados = list(db['canciones'].aggregate([
            {'$match': {'tituloCancion': {'$regex': query, '$options': 'i'}}},
            {'$limit': 10},
            {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                         'foreignField': 'albumID', 'as': 'albumData'}},
            {'$unwind': '$albumData'},
            {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': '$artistaData'},
            {'$project': {
                '_id': 0,
                'cancionId': '$cancionId',
                'titulo': '$tituloCancion',
                'duracion': '$duracionTotal',
                'artista': '$artistaData.perfilArtista.nombreProfesional',
                'artistaId': '$artistaData.usuarioId'
            }}
        ]))
    except Exception as e:
        print(f"Error buscando canciones: {e}")
        resultados = []

    return JsonResponse({'resultados': resultados})

def playlist_detail(request, playlist_id):
    if 'usuario_id' not in request.session:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('login')

    oyente_id = request.session['usuario_id']
    db = get_db()

    playlist = db['playlists'].find_one({'playlistID': playlist_id, 'oyenteId': oyente_id})
    if not playlist:
        messages.error(request, "Playlist no encontrada.")
        return redirect('Main:mi_biblioteca')

    canciones_ids = playlist.get('cancionesIds', [])

    canciones_en_playlist = []
    if canciones_ids:
        canciones_en_playlist = list(db['canciones'].aggregate([
            {'$match': {'cancionId': {'$in': canciones_ids}}},
            {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                         'foreignField': 'albumID', 'as': 'albumData'}},
            {'$unwind': '$albumData'},
            {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                         'foreignField': 'usuarioId', 'as': 'artistaData'}},
            {'$unwind': '$artistaData'},
            {'$project': {
                'CancionId': '$cancionId',
                'Cancion': '$tituloCancion',
                'Duracion': '$duracionTotal',
                'Artista': '$artistaData.perfilArtista.nombreProfesional',
                'ArtistaId': '$artistaData.usuarioId'
            }}
        ]))

    catalogo_completo = list(db['canciones'].aggregate([
        {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                     'foreignField': 'albumID', 'as': 'albumData'}},
        {'$unwind': '$albumData'},
        {'$lookup': {'from': 'usuarios', 'localField': 'albumData.artistaId',
                     'foreignField': 'usuarioId', 'as': 'artistaData'}},
        {'$unwind': '$artistaData'},
        {'$project': {
            'CancionId': '$cancionId',
            'Cancion': '$tituloCancion',
            'Artista': '$artistaData.perfilArtista.nombreProfesional'
        }},
        {'$sort': {'Cancion': 1}}
    ]))

    context = {
        'playlist': playlist,
        'canciones_en_playlist': canciones_en_playlist,
        'canciones_en_playlist_ids': canciones_ids,
        'catalogo_completo': catalogo_completo,
    }
    return render(request, 'PlaylistDetail.html', context)


def agregar_cancion_a_playlist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    try:
        data = json.loads(request.body)
        playlist_id = int(data.get('playlistId'))
        cancion_id = int(data.get('cancionId'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    db = get_db()
    result = db['playlists'].update_one(
        {'playlistID': playlist_id, 'oyenteId': oyente_id},
        {'$addToSet': {'cancionesIds': cancion_id}}   # evita duplicados automáticamente
    )
    if result.matched_count == 0:
        return JsonResponse({'error': 'Playlist no encontrada'}, status=404)
    return JsonResponse({'ok': True})


def quitar_cancion_de_playlist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    try:
        data = json.loads(request.body)
        playlist_id = int(data.get('playlistId'))
        cancion_id = int(data.get('cancionId'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    db = get_db()
    db['playlists'].update_one(
        {'playlistID': playlist_id, 'oyenteId': oyente_id},
        {'$pull': {'cancionesIds': cancion_id}}
    )
    return JsonResponse({'ok': True})


# ============================================================
# NUEVO: Panel del artista para subir canciones
# ============================================================
def subir_cancion(request):
    if 'usuario_id' not in request.session or request.session.get('rol') != 'Artista':
        messages.error(request, "Solo los artistas pueden subir canciones.")
        return redirect('Main:dashboard_negocio')

    artista_id = request.session['usuario_id']
    db = get_db()

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        duracion = request.POST.get('duracion', '').strip()  # formato mm:ss
        genero = request.POST.get('genero', '').strip()
        album_opcion = request.POST.get('album_opcion')  # 'existente' o 'nuevo'

        if not titulo or not duracion:
            messages.error(request, "El título y la duración son obligatorios.")
            return redirect('Main:subir_cancion')

        # Normalizar duración a HH:MM:SS
        partes = duracion.split(':')
        if len(partes) == 2:
            duracion = f"00:{partes[0].zfill(2)}:{partes[1].zfill(2)}"

        # ── Álbum: existente o nuevo ──
        if album_opcion == 'nuevo':
            nombre_album = request.POST.get('nombre_album_nuevo', '').strip()
            if not nombre_album:
                messages.error(request, "Debes indicar el nombre del nuevo álbum.")
                return redirect('Main:subir_cancion')

            ultimo_album = db['catalogo'].find_one(sort=[('albumID', -1)])
            nuevo_album_id = (ultimo_album['albumID'] + 1) if ultimo_album else 1

            db['catalogo'].insert_one({
                'albumID': nuevo_album_id,
                'tituloAlbum': nombre_album,
                'fechaLanzamiento': datetime.now().strftime('%Y-%m-%d'),
                'artistaId': artista_id
            })
            album_id = nuevo_album_id
        else:
            try:
                album_id = int(request.POST.get('album_existente'))
            except (TypeError, ValueError):
                messages.error(request, "Selecciona un álbum válido.")
                return redirect('Main:subir_cancion')

        # ── Insertar la canción ──
        ultimo_cancion = db['canciones'].find_one(sort=[('cancionId', -1)])
        nuevo_cancion_id = (ultimo_cancion['cancionId'] + 1) if ultimo_cancion else 1

        nueva_cancion = {
            'cancionId': nuevo_cancion_id,
            'tituloCancion': titulo,
            'duracionTotal': duracion,
            'albumId': album_id,
        }
        if genero:
            nueva_cancion['generos'] = [{'genero': genero}]

        db['canciones'].insert_one(nueva_cancion)

        messages.success(request, f'"{titulo}" fue publicada correctamente.')
        return redirect('Main:subir_cancion')

    # GET: mostrar formulario
    mis_albumes = list(db['catalogo'].find({'artistaId': artista_id}))
    mis_canciones = list(db['canciones'].aggregate([
        {'$lookup': {'from': 'catalogo', 'localField': 'albumId',
                     'foreignField': 'albumID', 'as': 'albumData'}},
        {'$unwind': '$albumData'},
        {'$match': {'albumData.artistaId': artista_id}},
        {'$project': {
            'Cancion': '$tituloCancion',
            'Album': '$albumData.tituloAlbum',
            'Duracion': '$duracionTotal'
        }},
        {'$sort': {'Cancion': 1}}
    ]))

    context = {
        'mis_albumes': mis_albumes,
        'mis_canciones': mis_canciones,
    }
    return render(request, 'SubirCancion.html', context)

def ver_planes(request):
    try:
        db = get_db() # Usamos tu conexión ya configurada
        coleccion_planes = db['planes']
        
        # Obtenemos todos los planes de la base de datos
        planes_bd = list(coleccion_planes.find())
        
        context = {
            'planes': planes_bd
        }
        return render(request, 'Planes.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar los planes: {str(e)}")
        return render(request, 'Planes.html', {'planes': []})

@csrf_protect
def cambiar_plan(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            tipo_plan = data.get('tipoPlan') # 'Free' o 'Premium'
            usuario_id = request.session.get('usuario_id')

            if not usuario_id:
                return JsonResponse({'ok': False, 'error': 'Sesión no válida'}, status=401)

            db = get_db()
            
            # Buscamos el ID del plan elegido
            plan = db['planes'].find_one({'tipoPlan': tipo_plan})
            if not plan:
                return JsonResponse({'ok': False, 'error': 'Plan no encontrado'}, status=404)

            from bson.objectid import ObjectId
            # Actualizamos el usuario en MongoDB convirtiendo su rolPerfil o actualizando su suscripción activa
            # Para que la corona aparezca, guardamos el estado del plan en su rol o dentro de un campo específico.
            # En este caso, modificaremos 'rolPerfil' a 'Premium' si era un Oyente normal, o actualizaremos su suscripción
                # Buscamos directamente por tu campo numérico (usuarioId) migrado de SQL
            db['usuarios'].update_one(
                {'usuarioId': int(usuario_id)},
                {'$set': {
                    'suscripcionActiva.planId': plan.get('planID'),
                    'suscripcionActiva.estado': 'Activo',
                    'rolPerfil': tipo_plan if request.session.get('rol') != 'Administrador' else 'Administrador'
                }}
            )

            # 🔥 Crucial: Actualizamos la sesión de Django al instante
            if request.session.get('rol') != 'Administrador':
                request.session['rol'] = tipo_plan
            
            # Guardamos una variable extra en sesión por si es Administrador pero quiere ver su corona de prueba
            request.session['plan_tipo'] = tipo_plan

            return JsonResponse({'ok': True})

        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=455)
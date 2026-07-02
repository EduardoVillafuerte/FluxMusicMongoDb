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
            gustadas_ids = [
                i['cancionId'] for i in db['interacciones'].find(
                    {'oyenteId': oyente_id, 'tipoInteraccion': 'Like'}, {'cancionId': 1}
                )
            ]
            excluidas_ids = list(set(escuchadas_ids) | set(gustadas_ids))
            recomendaciones = list(db['canciones'].aggregate([
                {'$match': {'cancionId': {'$nin': excluidas_ids}}},
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

# ============================================================
# NUEVO: Panel de estadísticas del artista
# ============================================================
def estadisticas_artista(request):
    if 'usuario_id' not in request.session or request.session.get('rol') != 'Artista':
        messages.error(request, "Solo los artistas pueden ver sus estadísticas.")
        return redirect('Main:dashboard_negocio')

    artista_id = request.session['usuario_id']
    db = get_db()

    # ── Datos del artista y su discográfica ───────────────
    usuario_artista = db['usuarios'].find_one({'usuarioId': artista_id}) or {}
    perfil = usuario_artista.get('perfilArtista', {})
    discografica_id = perfil.get('discograficaId')
    discografica_nombre = None
    if discografica_id:
        disc = db['usuarios'].find_one({'usuarioId': discografica_id})
        if disc:
            discografica_nombre = disc.get('nickname', 'Discográfica')

    # ── IDs de álbumes y canciones del artista ────────────
    mis_albumes_ids = [a['albumID'] for a in db['catalogo'].find({'artistaId': artista_id}, {'albumID': 1})]
    mis_canciones_ids = [
        c['cancionId'] for c in db['canciones'].find(
            {'albumId': {'$in': mis_albumes_ids}}, {'cancionId': 1}
        )
    ] if mis_albumes_ids else []

    # ── Totales generales ──────────────────────────────────
    total_reproducciones = 0
    total_likes = 0
    if mis_canciones_ids:
        total_reproducciones = db['reproducciones'].count_documents({'cancionId': {'$in': mis_canciones_ids}})
        total_likes = db['interacciones'].count_documents({'cancionId': {'$in': mis_canciones_ids}, 'tipoInteraccion': 'Like'})

    total_seguidores = db['interacciones'].count_documents({'artistaId': artista_id, 'tipoInteraccion': 'Seguir'})

    # ── Reproducciones por mes (histórico agrupado) ───────
    reproducciones_por_mes = []
    if mis_canciones_ids:
        try:
            pipeline_mes = list(db['reproducciones'].aggregate([
                {'$match': {'cancionId': {'$in': mis_canciones_ids}}},
                {'$addFields': {
                    'fechaConvertida': {'$dateFromString': {'dateString': '$fechaHora', 'onError': None}}
                }},
                {'$match': {'fechaConvertida': {'$ne': None}}},
                {'$group': {
                    '_id': {'anio': {'$year': '$fechaConvertida'}, 'mes': {'$month': '$fechaConvertida'}},
                    'total': {'$sum': 1}
                }},
                {'$sort': {'_id.anio': 1, '_id.mes': 1}},
                {'$limit': 12}
            ]))
            meses_es = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            for item in pipeline_mes:
                reproducciones_por_mes.append({
                    'mes': f"{meses_es[item['_id']['mes']]} {item['_id']['anio']}",
                    'total': item['total']
                })
        except Exception as e:
            print(f"Error calculando reproducciones por mes: {e}")

    max_reproducciones_mes = max([m['total'] for m in reproducciones_por_mes], default=0)
    for m in reproducciones_por_mes:
        m['porcentaje'] = round((m['total'] / max_reproducciones_mes) * 100) if max_reproducciones_mes else 0

    # ── Top 5 canciones más escuchadas ────────────────────
    top_canciones = []
    if mis_canciones_ids:
        try:
            top_canciones = list(db['reproducciones'].aggregate([
                {'$match': {'cancionId': {'$in': mis_canciones_ids}}},
                {'$group': {'_id': '$cancionId', 'total': {'$sum': 1}}},
                {'$sort': {'total': -1}},
                {'$limit': 5},
                {'$lookup': {'from': 'canciones', 'localField': '_id',
                             'foreignField': 'cancionId', 'as': 'cancionData'}},
                {'$unwind': '$cancionData'},
                {'$project': {
                    'Cancion': '$cancionData.tituloCancion',
                    'Reproducciones': '$total'
                }}
            ]))
        except Exception as e:
            print(f"Error calculando top canciones: {e}")

    # ── Regalías del periodo más reciente ─────────────────
    regalias_mes_actual = 0
    try:
        liquidacion_actual = db['liquidaciones'].find_one(
            {'artistaId': artista_id}, sort=[('periodo', -1)]
        )
        if liquidacion_actual:
            regalias_mes_actual = liquidacion_actual.get('montoPagarUSD', 0)
    except Exception as e:
        print(f"Error obteniendo regalías del artista: {e}")

    context = {
        'total_reproducciones': total_reproducciones,
        'total_seguidores': total_seguidores,
        'total_likes': total_likes,
        'total_canciones': len(mis_canciones_ids),
        'reproducciones_por_mes': reproducciones_por_mes,
        'top_canciones': top_canciones,
        'regalias_mes_actual': regalias_mes_actual,
        'discografica_nombre': discografica_nombre,
        'tiene_discografica': discografica_id is not None,
    }
    return render(request, 'Estadisticas.html', context)


# ============================================================
# NUEVO: Salir de la discográfica (con advertencia de regalías)
# ============================================================
def salir_discografica(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    if 'usuario_id' not in request.session or request.session.get('rol') != 'Artista':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    artista_id = request.session['usuario_id']
    db = get_db()

    usuario = db['usuarios'].find_one({'usuarioId': artista_id})
    if not usuario or not usuario.get('perfilArtista', {}).get('discograficaId'):
        return JsonResponse({'error': 'No perteneces a ninguna discográfica actualmente.'}, status=400)

    try:
        db['usuarios'].update_one(
            {'usuarioId': artista_id},
            {'$set': {'perfilArtista.discograficaId': None}}
        )
        return JsonResponse({'ok': True, 'mensaje': 'Has salido de la discográfica correctamente.'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


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

# Main/views.py

@csrf_protect
def cambiar_plan(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            nuevo_plan = data.get('tipoPlan') # Ej: 'Free' o 'Premium'
            usuario_id = request.session.get('usuario_id')

            db = get_db()
            
            # Actualizamos SOLO el campo del plan
            db['usuarios'].update_one(
                {'usuarioId': int(usuario_id)},
                {'$set': {'planActivo': nuevo_plan}} # Campo separado del rol
            )

            # Sincronizamos la sesión
            request.session['plan_tipo'] = nuevo_plan
            request.session.modified = True

            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)
        
def panel_discografica(request):
    if request.session.get('rol') != 'Discografica':
        messages.error(request, "Solo las discográficas pueden acceder a este panel.")
        return redirect('Main:dashboard_negocio')

    discografica_id = request.session.get('usuario_id')
    db = get_db()

    try:
        # Artistas que NO tienen ninguna discográfica asignada
        artistas_libres = list(db['usuarios'].find({
            'rolPerfil': 'Artista',
            '$or': [
                {'perfilArtista.discograficaId': None},
                {'perfilArtista.discograficaId': {'$exists': False}},
                {'perfilArtista.discograficaId': "Null"}
            ]
        }))

        # Artistas ya vinculados a ESTA discográfica (para referencia)
        artistas_vinculados = list(db['usuarios'].find({
            'rolPerfil': 'Artista',
            'perfilArtista.discograficaId': int(discografica_id)
        }))
    except Exception as e:
        artistas_libres, artistas_vinculados = [], []
        messages.error(request, f"Error al cargar artistas: {e}")

    context = {
        'artistas_libres': artistas_libres,
        'artistas_vinculados': artistas_vinculados,
    }
    return render(request, 'PanelDiscografica.html', context)


def vincular_artista(request):
    if request.method != 'POST':
        return redirect('Main:panel_discografica')

    if request.session.get('rol') != 'Discografica':
        messages.error(request, "No autorizado.")
        return redirect('Main:dashboard_negocio')

    discografica_id = request.session.get('usuario_id')
    artista_id = request.POST.get('artista_id')

    if not artista_id:
        messages.error(request, "Falta indicar el artista a vincular.")
        return redirect('Main:panel_discografica')

    db = get_db()

    try:
        artista = db['usuarios'].find_one({'usuarioId': int(artista_id), 'rolPerfil': 'Artista'})

        if not artista:
            messages.error(request, "El artista indicado no existe.")
            return redirect('Main:panel_discografica')

        # Evita pisar el vínculo si otra discográfica ya lo tomó entre tanto
        if artista.get('perfilArtista', {}).get('discograficaId'):
            messages.error(request, f"{artista.get('nickname', 'Ese artista')} ya pertenece a otra discográfica.")
            return redirect('Main:panel_discografica')

        db['usuarios'].update_one(
            {'usuarioId': int(artista_id)},
            {'$set': {'perfilArtista.discograficaId': int(discografica_id)}}
        )
        messages.success(request, f"Vinculaste a {artista.get('nickname', 'el artista')} con tu discográfica.")
    except Exception as e:
        messages.error(request, f"Error al vincular artista: {e}")

    return redirect('Main:panel_discografica')
from pymongo import MongoClient

# Aquí va tu conexión a la nube:
client = MongoClient('mongodb+srv://Admin:UDLA@clusterudla03.yq570z6.mongodb.net/')
db = client['FluxMusicMongoDb']

print("✓ Conectado a FluxMusicMongoDb")


# ==========================================
# 1. INSERCIÓN DE DATOS (INSERT)
# ==========================================

# Colección: Planes (Catálogo maestro)
print("\n▶ Insertando planes...")
planes_data = [
    {
        "planID": 1,
        "tipoPlan": "Free",
        "precio": 0.00
    },
    {
        "planID": 2,
        "tipoPlan": "Premium",
        "precio": 9.99
    }
]
db.planes.insert_many(planes_data)

# Colección: Usuarios (Perfiles incrustados, Plan referenciado)
print("▶ Insertando usuarios...")
usuarios_data = [
    {
        "usuarioId": 1000,
        "rolPerfil": "Administrador",
        "nickname": "SysAdmin",
        "email": "admin@fluxmusic.com",
        "pais": "Ecuador"
    },
    {
        "usuarioId": 1001,
        "rolPerfil": "Discografica",
        "nickname": "SonyMusic",
        "email": "contacto@sonymusic.com",
        "pais": "USA"
    },
    {
        "usuarioId": 1002,
        "rolPerfil": "Discografica",
        "nickname": "Universal",
        "email": "info@universalmusic.com",
        "pais": "UK"
    },
    {
        "usuarioId": 1003,
        "rolPerfil": "Discografica",
        "nickname": "Warner",
        "email": "latam@warner.com",
        "pais": "USA"
    },
    {
        "usuarioId": 1004,
        "rolPerfil": "Artista",
        "nickname": "TheWeeknd",
        "email": "abel@xo.com",
        "pais": "Canada",
        "perfilArtista": {
            "biografia": "Cantante y productor canadiense.",
            "genero": "R&B/Pop",
            "nombreProfesional": "The Weeknd",
            "discograficaId": 1002
        }
    },
    {
        "usuarioId": 1005,
        "rolPerfil": "Artista",
        "nickname": "DuaLipa",
        "email": "management@dualipa.com",
        "pais": "UK",
        "perfilArtista": {
            "biografia": "Cantante y compositora británica.",
            "genero": "Pop",
            "nombreProfesional": "Dua Lipa",
            "discograficaId": 1003
        }
    },
    {
        "usuarioId": 1006,
        "rolPerfil": "Artista",
        "nickname": "BadBunny",
        "email": "benito@rimas.com",
        "pais": "Puerto Rico",
        "perfilArtista": {
            "biografia": "Cantante de reguetón y trap latino.",
            "genero": "Urbano",
            "nombreProfesional": "Bad Bunny",
            "discograficaId": 1001
        }
    },
    {
        "usuarioId": 1007,
        "rolPerfil": "Artista",
        "nickname": "TaylorSwift",
        "email": "taylor@republic.com",
        "pais": "USA",
        "perfilArtista": {
            "biografia": "Cantautora estadounidense.",
            "genero": "Pop/Country",
            "nombreProfesional": "Taylor Swift",
            "discograficaId": 1002
        }
    },
    {
        "usuarioId": 1008,
        "rolPerfil": "Artista",
        "nickname": "DaftPunk",
        "email": "contact@daftpunk.com",
        "pais": "France",
        "perfilArtista": {
            "biografia": "Dúo francés de música electrónica.",
            "genero": "Electrónica",
            "nombreProfesional": "Daft Punk",
            "discograficaId": 1001
        }
    },
    {
        "usuarioId": 1009,
        "rolPerfil": "Oyente",
        "nickname": "edison_v",
        "email": "edison@mail.com",
        "pais": "Ecuador",
        "perfilOyente": {
            "preferenciaAudio": "Alta Calidad",
            "fechaNacimiento": "2001-05-14",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 2,
            "fechaInicio": "2026-01-10T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1010,
        "rolPerfil": "Oyente",
        "nickname": "camila_n",
        "email": "camila@mail.com",
        "pais": "Ecuador",
        "perfilOyente": {
            "preferenciaAudio": "Estándar",
            "fechaNacimiento": "2002-08-20",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 1,
            "fechaInicio": "2026-02-15T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1012,
        "rolPerfil": "Oyente",
        "nickname": "musicfan99",
        "email": "fan99@mail.com",
        "pais": "Mexico",
        "perfilOyente": {
            "preferenciaAudio": "Estándar",
            "fechaNacimiento": "1998-02-15",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 1,
            "fechaInicio": "2025-12-20T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1013,
        "rolPerfil": "Oyente",
        "nickname": "rocker_dude",
        "email": "rocker@mail.com",
        "pais": "Argentina",
        "perfilOyente": {
            "preferenciaAudio": "Alta Calidad",
            "fechaNacimiento": "1995-07-22",
            "aceptaNotificaciones": False
        },
        "suscripcionActiva": {
            "planId": 2,
            "fechaInicio": "2026-04-05T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1014,
        "rolPerfil": "Oyente",
        "nickname": "pop_queen",
        "email": "popqueen@mail.com",
        "pais": "Colombia",
        "perfilOyente": {
            "preferenciaAudio": "Estándar",
            "fechaNacimiento": "2005-12-10",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 1,
            "fechaInicio": "2026-04-10T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1015,
        "rolPerfil": "Oyente",
        "nickname": "carlos_dj",
        "email": "carlos.dj@mail.com",
        "pais": "Chile",
        "perfilOyente": {
            "preferenciaAudio": "Alta Calidad",
            "fechaNacimiento": "1999-04-12",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 2,
            "fechaInicio": "2026-03-15T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1016,
        "rolPerfil": "Oyente",
        "nickname": "ana_music",
        "email": "ana.m@mail.com",
        "pais": "Peru",
        "perfilOyente": {
            "preferenciaAudio": "Estándar",
            "fechaNacimiento": "2004-09-30",
            "aceptaNotificaciones": False
        },
        "suscripcionActiva": {
            "planId": 1,
            "fechaInicio": "2026-04-01T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1017,
        "rolPerfil": "Oyente",
        "nickname": "luis_beats",
        "email": "luis.b@mail.com",
        "pais": "Mexico",
        "perfilOyente": {
            "preferenciaAudio": "Alta Calidad",
            "fechaNacimiento": "1992-12-05",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 2,
            "fechaInicio": "2026-01-20T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1018,
        "rolPerfil": "Oyente",
        "nickname": "maria_pop",
        "email": "maria.p@mail.com",
        "pais": "Colombia",
        "perfilOyente": {
            "preferenciaAudio": "Estándar",
            "fechaNacimiento": "2001-01-25",
            "aceptaNotificaciones": True
        },
        "suscripcionActiva": {
            "planId": 1,
            "fechaInicio": "2026-04-12T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1019,
        "rolPerfil": "Oyente",
        "nickname": "pedro_rock",
        "email": "pedro.r@mail.com",
        "pais": "Argentina",
        "perfilOyente": {
            "preferenciaAudio": "Alta Calidad",
            "fechaNacimiento": "1988-06-18",
            "aceptaNotificaciones": False
        },
        "suscripcionActiva": {
            "planId": 2,
            "fechaInicio": "2025-11-10T00:00:00",
            "estado": "Activo"
        }
    },
    {
        "usuarioId": 1020,
        "rolPerfil": "Artista",
        "nickname": "Rosalia",
        "email": "contacto@motomami.com",
        "pais": "Espana",
        "perfilArtista": {
            "biografia": "Cantante, compositora y productora española.",
            "genero": "Urbano/Flamenco",
            "nombreProfesional": "Rosalía",
            "discograficaId": 1001
        }
    },
    {
        "usuarioId": 1021,
        "rolPerfil": "Artista",
        "nickname": "KendrickLamar",
        "email": "kendrick@pglang.com",
        "pais": "USA",
        "perfilArtista": {
            "biografia": "Rapero y compositor estadounidense.",
            "genero": "Hip-Hop",
            "nombreProfesional": "Kendrick Lamar",
            "discograficaId": 1002
        }
    },
    {
        "usuarioId": 1022,
        "rolPerfil": "Artista",
        "nickname": "BillieEilish",
        "email": "billie@darkroom.com",
        "pais": "USA",
        "perfilArtista": {
            "biografia": "Cantautora estadounidense.",
            "genero": "Pop Alternativo",
            "nombreProfesional": "Billie Eilish",
            "discograficaId": 1002
        }
    }
]
db.usuarios.insert_many(usuarios_data)

# Colección: Álbumes (Catálogo principal, referenciando al Artista)
print("▶ Insertando catálogo de álbumes...")
catalogo_data = [
    {
        "albumID": 1,
        "tituloAlbum": "After Hours",
        "artistaId": 1004,
        "fechaLanzamiento": "2020-03-20",
        "genero": "R&B/Pop",
        "totalCanciones": 14
    },
    {
        "albumID": 2,
        "tituloAlbum": "Future Nostalgia",
        "artistaId": 1005,
        "fechaLanzamiento": "2020-11-27",
        "genero": "Pop",
        "totalCanciones": 11
    },
    {
        "albumID": 3,
        "tituloAlbum": "Un x100to",
        "artistaId": 1006,
        "fechaLanzamiento": "2018-02-02",
        "genero": "Urbano",
        "totalCanciones": 16
    },
    {
        "albumID": 4,
        "tituloAlbum": "Discovery",
        "artistaId": 1008,
        "fechaLanzamiento": "2001-03-12",
        "genero": "Electrónica",
        "totalCanciones": 14
    },
    {
        "albumID": 5,
        "tituloAlbum": "Motomami",
        "artistaId": 1020,
        "fechaLanzamiento": "2022-03-18",
        "genero": "Urbano/Flamenco",
        "totalCanciones": 16
    }
]
db.catalogo.insert_many(catalogo_data)

# Colección: Canciones (Referenciando al Álbum)
print("▶ Insertando canciones...")
canciones_data = [
    {"cancionId": 1, "titulo": "Blinding Lights", "artistaId": 1004, "albumId": 1, "duracion": 200},
    {"cancionId": 2, "titulo": "Save Your Tears", "artistaId": 1004, "albumId": 1, "duracion": 215},
    {"cancionId": 3, "titulo": "Break My Heart", "artistaId": 1005, "albumId": 2, "duracion": 204},
    {"cancionId": 4, "titulo": "Physical", "artistaId": 1005, "albumId": 2, "duracion": 191},
    {"cancionId": 5, "titulo": "Tití Me Preguntó", "artistaId": 1006, "albumId": 3, "duracion": 243},
    {"cancionId": 6, "titulo": "La Jumpa", "artistaId": 1006, "albumId": 3, "duracion": 238},
    {"cancionId": 7, "titulo": "One More Time", "artistaId": 1008, "albumId": 4, "duracion": 320},
    {"cancionId": 8, "titulo": "Digital Love", "artistaId": 1008, "albumId": 4, "duracion": 302},
    {"cancionId": 9, "titulo": "Beso", "artistaId": 1020, "albumId": 5, "duracion": 227},
    {"cancionId": 10, "titulo": "Despecha", "artistaId": 1020, "albumId": 5, "duracion": 201}
]
db.canciones.insert_many(canciones_data)

# Colección: Playlists (Nido de IDs de canciones)
print("▶ Insertando playlists...")
playlists_data = [
    {
        "playlistID": 1,
        "nombrePlaylist": "Top Hits 2026",
        "oyenteId": 1010,
        "cancionesIds": [1, 3, 5, 7, 9]
    },
    {
        "playlistID": 2,
        "nombrePlaylist": "Urbano Fuerte",
        "oyenteId": 1014,
        "cancionesIds": [5, 6]
    }
]
db.playlists.insert_many(playlists_data)

# Colección: Reproducciones (Cada streaming individual)
print("▶ Insertando reproducciones...")
reproducciones_data = [
    {
        "reproduccionId": 1,
        "oyenteId": 1009,
        "cancionId": 1,
        "fechaReproduccion": "2026-04-15T10:30:00",
        "segundosEscuchado": 200,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 2,
        "oyenteId": 1010,
        "cancionId": 1,
        "fechaReproduccion": "2026-04-14T15:45:00",
        "segundosEscuchado": 200,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 3,
        "oyenteId": 1012,
        "cancionId": 3,
        "fechaReproduccion": "2026-04-13T08:20:00",
        "segundosEscuchado": 45,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 4,
        "oyenteId": 1013,
        "cancionId": 5,
        "fechaReproduccion": "2026-04-15T19:00:00",
        "segundosEscuchado": 243,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 5,
        "oyenteId": 1014,
        "cancionId": 5,
        "fechaReproduccion": "2026-04-12T22:10:00",
        "segundosEscuchado": 243,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 6,
        "oyenteId": 1015,
        "cancionId": 7,
        "fechaReproduccion": "2026-04-11T14:30:00",
        "segundosEscuchado": 320,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 7,
        "oyenteId": 1016,
        "cancionId": 9,
        "fechaReproduccion": "2026-04-10T11:00:00",
        "segundosEscuchado": 25,
        "aplicarRegalia": None
    },
    {
        "reproduccionId": 8,
        "oyenteId": 1017,
        "cancionId": 3,
        "fechaReproduccion": "2026-04-15T09:15:00",
        "segundosEscuchado": 204,
        "aplicarRegalia": None
    }
]
db.reproducciones.insert_many(reproducciones_data)

# Colección: Notificaciones
print("▶ Insertando notificaciones...")
notificaciones_data = []
for usuario_id in range(1000, 1023):
    notificaciones_data.append({
        "notificacionId": usuario_id - 1000 + 1000,
        "usuarioId": usuario_id,
        "tipo": "Bienvenida",
        "mensaje": "Bienvenido a FluxMusic",
        "leida": False
    })
db.notificaciones.insert_many(notificaciones_data)

# Colección: Liquidaciones (Cierre de Regalías por artista)
print("▶ Insertando liquidaciones...")
liquidaciones_data = [
    {
        "liquidacionId": 1,
        "artistaId": 1004,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 2,
        "montoPagarUSD": 0.008
    },
    {
        "liquidacionId": 2,
        "artistaId": 1005,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 2,
        "montoPagarUSD": 0.008
    },
    {
        "liquidacionId": 3,
        "artistaId": 1006,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 4,
        "montoPagarUSD": 0.016
    },
    {
        "liquidacionId": 4,
        "artistaId": 1008,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 3,
        "montoPagarUSD": 0.012
    },
    {
        "liquidacionId": 5,
        "artistaId": 1020,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 2,
        "montoPagarUSD": 0.008
    },
    {
        "liquidacionId": 6,
        "artistaId": 1021,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 1,
        "montoPagarUSD": 0.004
    },
    {
        "liquidacionId": 7,
        "artistaId": 1022,
        "mes": 4,
        "anio": 2026,
        "totalStreamsValidos": 1,
        "montoPagarUSD": 0.004
    }
]
db.liquidaciones.insert_many(liquidaciones_data)

# ==========================================
# ACTUALIZACIÓN DE DATOS (UPDATE)
# ==========================================

# Actualización en colección de reproducciones para determinar si aplica regalía
print("\n▶ Actualizando reproducciones (aplicarRegalia)...")

# Poner aplicarRegalia en TRUE a los que tienen 30 segundos o más
db.reproducciones.update_many(
    {"segundosEscuchado": {"$gte": 30}},
    {"$set": {"aplicarRegalia": True}}
)

# Poner aplicarRegalia en FALSE a los que tienen menos de 30 segundos
db.reproducciones.update_many(
    {"segundosEscuchado": {"$lt": 30}},
    {"$set": {"aplicarRegalia": False}}
)

# ==========================================
# 2. CONSULTAS DE LECTURA
# ==========================================

print("\n" + "="*50)
print("CONSULTAS DE LECTURA")
print("="*50)

# FINDONE: Buscar el perfil completo de un usuario específico
print("\n▶ FINDONE: Buscar usuario 'edison_v'")
usuario_edison = db.usuarios.find_one({"nickname": "edison_v"})
if usuario_edison:
    print(f"  Usuario encontrado: {usuario_edison['nickname']} - {usuario_edison['email']}")

# FIND: Buscar todo el catálogo de un artista usando su ID de referencia
print("\n▶ FIND: Catálogo del artista 1004 (The Weeknd)")
catalogo_artista = list(db.catalogo.find({"artistaId": 1004}))
for album in catalogo_artista:
    print(f"  Álbum: {album['tituloAlbum']} ({album['fechaLanzamiento']})")

# ==========================================
# 3. CONSULTAS AVANZADAS Y AGREGACIONES
# ==========================================

print("\n" + "="*50)
print("CONSULTAS AVANZADAS Y AGREGACIONES")
print("="*50)

# AGGREGATE + $lookup: Ver el detalle de las canciones dentro de una Playlist
print("\n▶ Agregación: Detalles de canciones en Playlist 1")
pipeline_playlist = [
    {"$match": {"playlistID": 1}},
    {
        "$lookup": {
            "from": "canciones",
            "localField": "cancionesIds",
            "foreignField": "cancionId",
            "as": "detalleCanciones"
        }
    }
]
resultado_playlist = list(db.playlists.aggregate(pipeline_playlist))
if resultado_playlist:
    playlist = resultado_playlist[0]
    print(f"  Playlist: {playlist['nombrePlaylist']}")
    for cancion in playlist['detalleCanciones']:
        print(f"    - {cancion['titulo']} ({cancion['duracion']}s)")

# AGGREGATE + Múltiples $lookups: Cálculo automático de Regalías Mensuales
print("\n▶ Agregación: Cálculo de Regalías Mensuales")
pipeline_regalias = [
    {"$match": {"aplicarRegalia": True}},
    {
        "$lookup": {
            "from": "canciones",
            "localField": "cancionId",
            "foreignField": "cancionId",
            "as": "cancionData"
        }
    },
    {"$unwind": "$cancionData"},
    {
        "$lookup": {
            "from": "catalogo",
            "localField": "cancionData.albumId",
            "foreignField": "albumID",
            "as": "catalogoData"
        }
    },
    {"$unwind": "$catalogoData"},
    {
        "$group": {
            "_id": "$catalogoData.artistaId",
            "totalStreams": {"$sum": 1}
        }
    },
    {
        "$project": {
            "artistaId": "$_id",
            "totalStreams": 1,
            "montoGeneradoUSD": {"$multiply": ["$totalStreams", 0.004]},
            "_id": 0
        }
    }
]
resultados_regalias = list(db.reproducciones.aggregate(pipeline_regalias))
for resultado in resultados_regalias:
    print(f"  Artista {resultado['artistaId']}: {resultado['totalStreams']} streams = ${resultado['montoGeneradoUSD']:.3f}")

# ==========================================
# 4. CONSULTAS DE ACTUALIZACIÓN
# ==========================================

print("\n" + "="*50)
print("CONSULTAS DE ACTUALIZACIÓN")
print("="*50)

# UPDATEONE ($set): Marcar una notificación como leída
print("\n▶ UPDATEONE: Marcar notificación 1010 como leída")
db.notificaciones.update_one(
    {"notificacionId": 1010},
    {"$set": {"leida": True}}
)
print("  ✓ Notificación marcada como leída")

# UPDATEMANY ($set): Promoción masiva - Mejorar calidad de audio
print("\n▶ UPDATEMANY: Promoción - Mejorar calidad de audio de 'Estándar' a 'Alta Calidad'")
resultado_update = db.usuarios.update_many(
    {"perfilOyente.preferenciaAudio": "Estándar"},
    {"$set": {"perfilOyente.preferenciaAudio": "Alta Calidad"}}
)
print(f"  ✓ {resultado_update.modified_count} usuarios actualizados")

# UPDATEONE ($push): Agregar una nueva referencia de canción a una playlist
print("\n▶ UPDATEONE ($push): Agregar canción 25 a Playlist 1")
db.playlists.update_one(
    {"playlistID": 1},
    {"$push": {"cancionesIds": 25}}
)
print("  ✓ Canción agregada a la playlist")

# UPSERT: Actualizar nombre de una playlist o crearla si no existe
print("\n▶ UPSERT: Actualizar/crear Playlist 3")
resultado_upsert = db.playlists.update_one(
    {"playlistID": 3},
    {
        "$set": {
            "nombrePlaylist": "Favoritas 2026",
            "oyenteId": 1011
        }
    },
    upsert=True
)
print(f"  ✓ Upsert completado (upserted_id: {resultado_upsert.upserted_id})")

# ==========================================
# 5. CONSULTAS DE ELIMINACIÓN
# ==========================================

print("\n" + "="*50)
print("CONSULTAS DE ELIMINACIÓN")
print("="*50)

# DELETEONE: Eliminar una playlist específica
print("\n▶ DELETEONE: Eliminar Playlist 2")
resultado_delete_one = db.playlists.delete_one({"playlistID": 2})
print(f"  ✓ {resultado_delete_one.deleted_count} documento eliminado")

# DELETEMANY: Limpieza de base de datos (Borrar reproducciones inválidas)
print("\n▶ DELETEMANY: Eliminar reproducciones con aplicarRegalia = False")
resultado_delete_many = db.reproducciones.delete_many({"aplicarRegalia": False})
print(f"  ✓ {resultado_delete_many.deleted_count} reproducciones eliminadas")

# ==========================================
# RESUMEN FINAL
# ==========================================

print("\n" + "="*50)
print("RESUMEN DE OPERACIONES")
print("="*50)

# Contar documentos en cada colección
colecciones = ['planes', 'usuarios', 'catalogo', 'canciones', 'playlists', 
               'reproducciones', 'notificaciones', 'liquidaciones']

print("\nTotal de documentos por colección:")
for coleccion in colecciones:
    total = db[coleccion].count_documents({})
    print(f"  {coleccion}: {total} documentos")

print("\n✓ Script completado exitosamente")

# Cerrar la conexión
client.close()
from usuarios.db_connection import get_db

def sidebar_data(request):
    oyente_id = request.session.get('usuario_id')
    if not oyente_id:
        return {'playlists': [], 'artistas_seguidos_ids': []}

    db = get_db()

    playlists = list(db['playlists'].find({'oyenteId': oyente_id}))
    for p in playlists:
        p['Playlist'] = p.get('nombrePlaylist')
        p['PlaylistID'] = p.get('playlistID')

    artistas_seguidos_ids = [
        i['artistaId'] for i in db['interacciones'].find(
            {'oyenteId': oyente_id, 'tipoInteraccion': 'Seguir'}, {'artistaId': 1}
        )
    ]

    return {'playlists': playlists, 'artistas_seguidos_ids': artistas_seguidos_ids}
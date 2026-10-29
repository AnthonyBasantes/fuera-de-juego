import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parents[1]
PUBLICADAS = BASE / 'datos' / 'publicadas.json'
BORRADORES = BASE / 'datos' / 'borradores'
CATEGORIAS = {'mundial', 'ecuador', 'fichajes', 'polemicas'}

def cargar(path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)

def main():
    identificador = os.environ.get('NOTICIA_ID', '').strip()
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}', identificador):
        raise SystemExit('ID no válido. Usa letras minúsculas, números y guiones.')
    ruta = BORRADORES / f'{identificador}.json'
    if not ruta.is_file():
        raise SystemExit(f'No existe el borrador: {ruta.relative_to(BASE)}')
    borrador = cargar(ruta)
    if not isinstance(borrador, dict):
        raise SystemExit('El borrador debe ser un objeto JSON.')
    if borrador.get('revision_editorial') is not True:
        raise SystemExit('Primero revisa y marca revision_editorial: true en el borrador.')
    campos = ('cat', 'label', 'title', 'desc', 'body', 'source_name', 'source_url')
    for campo in campos:
        if not isinstance(borrador.get(campo), str) or not borrador[campo].strip():
            raise SystemExit(f'Falta un campo válido: {campo}')
    if borrador['cat'] not in CATEGORIAS:
        raise SystemExit('Categoría no válida.')
    if len(borrador['body'].strip()) < 100:
        raise SystemExit('El artículo es demasiado corto (mínimo 100 caracteres).')
    url = urlparse(borrador['source_url'])
    if url.scheme != 'https' or not url.netloc:
        raise SystemExit('La fuente debe tener un enlace HTTPS válido.')
    imagen = borrador.get('image', '')
    if imagen and (not isinstance(imagen, str) or not (imagen.startswith('./imagenes/') or imagen.startswith('https://'))):
        raise SystemExit('Ruta de imagen no válida.')
    data = cargar(PUBLICADAS)
    noticias = data.get('noticias')
    if not isinstance(noticias, list):
        raise SystemExit('publicadas.json debe contener una lista noticias.')
    if any(n.get('id') == identificador for n in noticias):
        raise SystemExit('La noticia ya está publicada con ese ID.')
    if any(n.get('source_url', '').rstrip('/') == borrador['source_url'].rstrip('/') for n in noticias):
        raise SystemExit('Ya existe una noticia con esa URL de origen.')
    nueva = {'id': identificador, 'estado': 'aprobada'}
    for campo in campos:
        nueva[campo] = borrador[campo].strip()
    if imagen:
        nueva['image'] = imagen
    noticias.insert(0, nueva)
    PUBLICADAS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Noticia aprobada: {identificador}. Total publicadas: {len(noticias)}')

if __name__ == '__main__':
    main()

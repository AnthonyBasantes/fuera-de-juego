
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import feedparser

BASE = Path(__file__).resolve().parents[1]
ARCHIVO = BASE / "datos" / "noticias_pendientes.json"
MAX_NOTICIAS = 200

FUENTES = {
    "BBC Sport - Futbol": "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "The Guardian - Futbol": "https://www.theguardian.com/football/rss",
}


def normalizar_enlace(enlace):
    partes = urlsplit(enlace.strip())
    ruta = partes.path.rstrip("/") or "/"

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        ruta,
        "",
        "",
    ))


def cargar_noticias():
    if not ARCHIVO.exists():
        return []

    try:
        with ARCHIVO.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)

        noticias = datos.get("noticias", [])

        if isinstance(noticias, list):
            return [
                noticia for noticia in noticias
                if isinstance(noticia, dict)
            ]

    except (OSError, ValueError) as error:
        print(f"Error al leer noticias anteriores: {error}")
        raise

    return []


def buscar_noticias():
    fecha = datetime.now(timezone.utc).isoformat()

    noticias = cargar_noticias()

    enlaces = {
        normalizar_enlace(noticia["enlace_fuente"])
        for noticia in noticias
        if isinstance(noticia.get("enlace_fuente"), str)
        and noticia["enlace_fuente"].strip()
    }

    nuevas = 0

    for nombre, url in FUENTES.items():
        print(f"Consultando: {nombre}")

        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"No se pudo leer: {nombre}")
                continue

            for entrada in feed.entries[:10]:
                titulo = entrada.get("title", "").strip()
                enlace = entrada.get("link", "").strip()

                if not titulo or not enlace:
                    continue

                enlace_normalizado = normalizar_enlace(enlace)

                if enlace_normalizado in enlaces:
                    continue

                noticias.append({
                    "titulo_original": titulo,
                    "fuente": nombre,
                    "enlace_fuente": enlace,
                    "estado": "pendiente",
                    "fecha_detectada": fecha,
                })

                enlaces.add(enlace_normalizado)
                nuevas += 1

        except Exception as error:
            print(f"Error consultando {nombre}: {error}")

    noticias = noticias[-MAX_NOTICIAS:]

    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)

    resultado = {
        "actualizado": fecha,
        "total": len(noticias),
        "nuevas": nuevas,
        "noticias": noticias,
    }

    ARCHIVO.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Noticias nuevas encontradas: {nuevas}")
    print(f"Noticias conservadas: {len(noticias)}")


if __name__ == "__main__":
    buscar_noticias()

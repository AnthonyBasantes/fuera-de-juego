
import json
import re
import unicodedata
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
    "El Universo - Ecuador": "https://www.eluniverso.com/arc/outboundfeeds/rss/category/deportes/?outputType=xml",
}

PALABRAS_ECUADOR = (
    "ligapro", "liga pro", "copa ecuador",
    "liga de quito", "liga deportiva universitaria",
    "independiente del valle", "barcelona sc",
    "barcelona sporting club", "emelec",
    "el nacional", "deportivo cuenca",
    "universidad catolica", "delfin",
    "aucas", "mushuc runa", "macara",
    "orense", "libertad fc",
    "seleccion de ecuador", "la tri",
    "moises caicedo", "piero hincapie",
    "willian pacho", "enner valencia",
)

PALABRAS_FICHAJES = (
    "fichaje", "traspaso", "transferencia",
    "contratacion", "refuerzo", "mercado de pases",
    "transfer", "signing", "joins", "signed",
    "loan deal", "transfer window",
)

PALABRAS_POLEMICAS = (
    "polemica", "sancion", "expulsion",
    "tarjeta roja", "escandalo", "denuncia",
    "investigacion", "suspendido",
    "controversy", "red card", "banned",
    "suspended", "investigation",
)

PALABRAS_FUTBOL = (
    "futbol", "ligapro", "liga pro",
    "copa ecuador", "barcelona sc",
    "emelec", "liga de quito",
    "independiente del valle",
    "seleccion", "mundial", "eliminatorias",
    "champions league", "premier league",
    "moises caicedo", "piero hincapie",
    "willian pacho",
)

EXCLUIR = (
    "sign up", "newsletter", "subscribe",
    "quiz", "who am i", "podcast",
    "suscribete", "suscripcion",
    "boletin informativo",
)


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )


def contiene(texto, palabras):
    return any(palabra in texto for palabra in palabras)


def normalizar_enlace(enlace):
    partes = urlsplit(enlace.strip())

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        partes.path.rstrip("/") or "/",
        "",
        "",
    ))


def clasificar_noticia(titulo, fuente):
    texto = normalizar(titulo)

    if fuente == "El Universo - Ecuador":
        if contiene(texto, PALABRAS_FUTBOL):
            return "ecuador"
        if contiene(texto, PALABRAS_ECUADOR):
            return "ecuador"
        return None

    if contiene(texto, PALABRAS_ECUADOR):
        return "ecuador"

    if contiene(texto, PALABRAS_FICHAJES):
        return "fichajes"

    if contiene(texto, PALABRAS_POLEMICAS):
        return "polemicas"

    return "mundial"


def es_valida(titulo, enlace):
    if not titulo or not enlace:
        return False

    texto = normalizar(titulo)

    if contiene(texto, EXCLUIR):
        return False

    partes = urlsplit(enlace)

    if partes.scheme not in ("http", "https"):
        return False

    if not partes.netloc:
        return False

    return True


def cargar_noticias():
    if not ARCHIVO.exists():
        return []

    with ARCHIVO.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    noticias = datos.get("noticias", [])

    if not isinstance(noticias, list):
        raise ValueError("El historial debe contener una lista.")

    return [
        noticia for noticia in noticias
        if isinstance(noticia, dict)
    ]


def buscar_noticias():
    fecha = datetime.now(timezone.utc).isoformat()
    anteriores = cargar_noticias()

    noticias = []
    enlaces = set()

    descartadas = 0

    for noticia in anteriores:
        enlace = noticia.get("enlace_fuente", "")

        if not isinstance(enlace, str) or not enlace:
            continue

        clave = normalizar_enlace(enlace)

        if clave in enlaces:
            continue

        if "categoria" not in noticia:
            noticia["categoria"] = clasificar_noticia(
                noticia.get("titulo_original", ""),
                noticia.get("fuente", ""),
            ) or "mundial"

        noticias.append(noticia)
        enlaces.add(clave)

    nuevas = 0

    for nombre, url in FUENTES.items():
        print(f"Consultando: {nombre}")

        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"No se pudo leer: {nombre}")
                continue

            encontradas = 0

            for entrada in feed.entries[:30]:
                titulo = entrada.get("title", "").strip()
                enlace = entrada.get("link", "").strip()

                if not es_valida(titulo, enlace):
                    descartadas += 1
                    continue

                categoria = clasificar_noticia(titulo, nombre)

                if categoria is None:
                    descartadas += 1
                    continue

                clave = normalizar_enlace(enlace)

                if clave in enlaces:
                    continue

                noticias.append({
                    "titulo_original": titulo,
                    "fuente": nombre,
                    "enlace_fuente": enlace,
                    "categoria": categoria,
                    "estado": "pendiente",
                    "fecha_detectada": fecha,
                })

                enlaces.add(clave)
                encontradas += 1
                nuevas += 1

            print(f"Nuevas de {nombre}: {encontradas}")

        except Exception as error:
            print(f"Error en {nombre}: {error}")

    noticias = noticias[-MAX_NOTICIAS:]

    resultado = {
        "actualizado": fecha,
        "total": len(noticias),
        "nuevas": nuevas,
        "descartadas": descartadas,
        "noticias": noticias,
    }

    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)

    ARCHIVO.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("------------------------------")
    print(f"Noticias nuevas: {nuevas}")
    print(f"Noticias guardadas: {len(noticias)}")
    print(f"Entradas descartadas: {descartadas}")
    print("Busqueda finalizada correctamente.")


if __name__ == "__main__":
    buscar_noticias()

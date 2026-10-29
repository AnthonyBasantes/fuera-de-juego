
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parents[1]
PENDIENTES = BASE / "datos" / "noticias_pendientes.json"
BORRADORES = BASE / "datos" / "borradores"
PUBLICADAS = BASE / "datos" / "publicadas.json"

CATEGORIAS = {"ecuador", "mundial", "fichajes", "polemicas"}


def cargar(ruta):
    with ruta.open(encoding="utf-8") as archivo:
        return json.load(archivo)


def normalizar_url(url):
    partes = urlsplit(url.strip())

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        partes.path.rstrip("/"),
        "",
        "",
    ))


def crear_id(noticia):
    titulo = noticia["titulo_original"].lower()
    titulo = unicodedata.normalize("NFKD", titulo)

    titulo = "".join(
        letra for letra in titulo
        if not unicodedata.combining(letra)
    )

    titulo = re.sub(r"[^a-z0-9]+", "-", titulo)
    titulo = titulo.strip("-")[:55].rstrip("-")

    url = normalizar_url(noticia["enlace_fuente"])
    codigo = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:10]

    return f"{titulo or 'noticia'}-{codigo}"


def main():
    datos = cargar(PENDIENTES)
    noticias = datos.get("noticias", [])

    if not noticias:
        raise SystemExit("No hay noticias pendientes.")

    print("\nNOTICIAS DISPONIBLES\n")

    for numero, noticia in enumerate(noticias, 1):
        identificador = crear_id(noticia)

        print(
            f"{numero}. [{noticia.get('categoria', 'mundial')}] "
            f"{noticia['titulo_original']}"
        )
        print(f"   ID: {identificador}")

    seleccion = os.environ.get("NOTICIA_ID", "").strip()

    if not seleccion:
        seleccion = input(
            "\nEscribe el ID de la noticia: "
        ).strip()

    noticia = next(
        (
            item for item in noticias
            if crear_id(item) == seleccion
        ),
        None,
    )

    if noticia is None:
        raise SystemExit(
            "No existe una noticia con ese ID."
        )

    categoria = noticia.get("categoria", "mundial")

    if categoria not in CATEGORIAS:
        raise SystemExit("Categoría no válida.")

    BORRADORES.mkdir(
        parents=True,
        exist_ok=True
    )

    destino = BORRADORES / f"{seleccion}.json"

    if destino.exists():
        raise SystemExit(
            "Ya existe un borrador para esta noticia."
        )

    url = normalizar_url(
        noticia["enlace_fuente"]
    )

    for archivo in BORRADORES.glob("*.json"):
        try:
            anterior = cargar(archivo)

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            print(
                f"AVISO: JSON inválido en {archivo.name}"
            )
            continue

        if not isinstance(anterior, dict):
            print(
                f"AVISO: Formato incorrecto en {archivo.name}"
            )
            continue

        url_anterior = anterior.get(
            "source_url", ""
        )

        if not isinstance(url_anterior, str):
            print(
                f"AVISO: URL incorrecta en {archivo.name}"
            )
            continue

        if normalizar_url(url_anterior) == url:
            raise SystemExit(
                f"Esta noticia ya tiene borrador: "
                f"{archivo.name}"
            )

    publicadas = cargar(PUBLICADAS)

    for publicada in publicadas.get("noticias", []):
        url_publicada = publicada.get(
            "source_url", ""
        )

        if not isinstance(url_publicada, str):
            continue

        if normalizar_url(url_publicada) == url:
            raise SystemExit(
                "Esta noticia ya fue publicada."
            )

    etiquetas = {
        "ecuador": "FÚTBOL ECUATORIANO",
        "mundial": "FÚTBOL MUNDIAL",
        "fichajes": "FICHAJES",
        "polemicas": "POLÉMICAS",
    }

    borrador = {
        "revision_editorial": False,
        "cat": categoria,
        "label": etiquetas[categoria],
        "title": "REDACTAR TÍTULO EN ESPAÑOL",
        "desc": "REDACTAR RESUMEN ORIGINAL",
        "body": "REDACTAR ARTÍCULO ORIGINAL Y VERIFICADO",
        "source_name": noticia["fuente"],
        "source_url": noticia["enlace_fuente"],
        "image": f"./imagenes/categoria-{categoria}.svg",
    }

    destino.write_text(
        json.dumps(
            borrador,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("\nBORRADOR CREADO CORRECTAMENTE")
    print(
        f"Archivo: {destino.relative_to(BASE)}"
    )
    print(
        "Estado: pendiente de revisión editorial."
    )


if __name__ == "__main__":
    main()

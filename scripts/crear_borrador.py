
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PENDIENTES = BASE / "datos" / "noticias_pendientes.json"
BORRADORES = BASE / "datos" / "borradores"


def crear_id(titulo):
    texto = unicodedata.normalize("NFKD", titulo.lower())
    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")[:70].rstrip("-")


def cargar_pendientes():
    with PENDIENTES.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos["noticias"]


def crear_borrador():
    noticias = cargar_pendientes()

    print("\nNOTICIAS DISPONIBLES\n")

    for numero, noticia in enumerate(noticias, start=1):
        print(
            f"{numero}. [{noticia.get('categoria', 'mundial')}] "
            f"{noticia['titulo_original']}"
        )

    seleccion = int(input("\nNúmero de noticia: "))

    if seleccion < 1 or seleccion > len(noticias):
        print("Número no válido.")
        return

    noticia = noticias[seleccion - 1]

    identificador = crear_id(noticia["titulo_original"])

    BORRADORES.mkdir(parents=True, exist_ok=True)

    destino = BORRADORES / f"{identificador}.json"

    if destino.exists():
        print("Este borrador ya existe.")
        return

    categoria = noticia.get("categoria", "mundial")

    etiquetas = {
        "ecuador": "FÚTBOL ECUATORIANO",
        "mundial": "FÚTBOL MUNDIAL",
        "fichajes": "FICHAJES",
        "polemicas": "POLÉMICAS",
    }

    borrador = {
        "revision_editorial": False,
        "cat": categoria,
        "label": etiquetas.get(categoria, "FÚTBOL MUNDIAL"),
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

    print(f"\nBorrador creado: {destino.relative_to(BASE)}")
    print("Revisa los datos y redacta el artículo.")
    print("Después cambia revision_editorial a true.")


if __name__ == "__main__":
    crear_borrador()

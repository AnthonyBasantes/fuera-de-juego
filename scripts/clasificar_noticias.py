
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parents[1]
PENDIENTES = BASE / "datos" / "noticias_pendientes.json"
BORRADORES = BASE / "datos" / "borradores"
PUBLICADAS = BASE / "datos" / "publicadas.json"
RESULTADO = BASE / "datos" / "estado_noticias.json"


def cargar(ruta):
    try:
        with ruta.open(encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        print(f"AVISO: No se pudo leer {ruta.name}")
        return {}


def normalizar_url(url):
    if not isinstance(url, str):
        return ""

    partes = urlsplit(url.strip())

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        partes.path.rstrip("/"),
        "",
        "",
    ))


def main():
    datos = cargar(PENDIENTES)
    noticias = datos.get("noticias", [])

    borradores = set()
    publicadas = set()

    if BORRADORES.exists():
        for archivo in BORRADORES.glob("*.json"):
            borrador = cargar(archivo)

            if not isinstance(borrador, dict):
                continue

            url = normalizar_url(
                borrador.get("source_url", "")
            )

            if url:
                borradores.add(url)

    datos_publicados = cargar(PUBLICADAS)

    for noticia in datos_publicados.get("noticias", []):
        url = normalizar_url(
            noticia.get("source_url", "")
        )

        if url:
            publicadas.add(url)

    resultado = []
    conteo = {
        "pendiente": 0,
        "en_revision": 0,
        "publicada": 0,
    }

    for noticia in noticias:
        url = normalizar_url(
            noticia.get("enlace_fuente", "")
        )

        if url in publicadas:
            estado = "publicada"
        elif url in borradores:
            estado = "en_revision"
        else:
            estado = "pendiente"

        conteo[estado] += 1

        resultado.append({
            "titulo": noticia.get("titulo_original", ""),
            "categoria": noticia.get("categoria", "mundial"),
            "fuente": noticia.get("fuente", ""),
            "enlace_fuente": noticia.get("enlace_fuente", ""),
            "estado": estado,
        })

    salida = {
        "total": len(resultado),
        "resumen": conteo,
        "noticias": resultado,
    }

    RESULTADO.write_text(
        json.dumps(
            salida,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print("\nESTADO EDITORIAL - FUERA DE JUEGO")
    print("=" * 45)
    print(f"Total detectadas: {len(resultado)}")
    print(f"Pendientes: {conteo['pendiente']}")
    print(f"En revisión: {conteo['en_revision']}")
    print(f"Publicadas: {conteo['publicada']}")
    print("=" * 45)
    print("Archivo generado: datos/estado_noticias.json")


if __name__ == "__main__":
    main()

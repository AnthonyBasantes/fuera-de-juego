
import json
from datetime import datetime, timezone
from pathlib import Path

import feedparser

FUENTES = {
    "BBC Sport - Futbol": "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "The Guardian - Futbol": "https://www.theguardian.com/football/rss",
}

ARCHIVO = Path("datos/noticias_pendientes.json")


def buscar_noticias():
    noticias = []

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

                noticias.append({
                    "titulo_original": titulo,
                    "fuente": nombre,
                    "enlace_fuente": enlace,
                    "estado": "pendiente",
                })

        except Exception as error:
            print(f"Error en {nombre}: {error}")

    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)

    resultado = {
        "actualizado": datetime.now(timezone.utc).isoformat(),
        "noticias": noticias,
    }

    ARCHIVO.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Se encontraron {len(noticias)} noticias candidatas.")


if __name__ == "__main__":
    buscar_noticias()

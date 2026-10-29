# FUERA DE JUEGO — Actualización integral

## Cambios
- Cuatro artículos con URLs propias en `noticias/`, HTML legible sin JavaScript, etiquetas SEO, Open Graph y datos estructurados NewsArticle.
- `sitemap.xml` con las 4 noticias y las 4 páginas principales.
- Enlaces desde las tarjetas de inicio a páginas individuales.
- Generación automática de páginas al aprobar una noticia y cuando cambie `datos/publicadas.json`.
- Se conserva el panel editorial, los scripts de RSS, las imágenes y las páginas legales.
- Se corrigió el artículo de Bruno Fernandes que no tenía `id`.
- Se normalizó la presentación del título de Rulli (sin alterar el cuerpo).

## Instalación
1. En GitHub, realiza una copia de seguridad del repositorio actual.
2. Sube los archivos y carpetas de este paquete a la rama `main`, conservando la estructura.
3. Comprueba en GitHub Actions que `Generar paginas y sitemap` no tenga errores.
4. Comprueba `index.html`, las cuatro URLs en `noticias/`, y `sitemap.xml`.
5. Si algo falla, restaura el commit anterior en GitHub.

## Revisión editorial pendiente antes de AdSense
- Contrastar los datos deportivos de las cuatro noticias con las fuentes originales.
- Reescribir o enriquecer cualquier texto que sea una paráfrasis demasiado cercana de la fuente.
- Comprobar derechos comerciales de todas las imágenes y de la fotografía externa de Unsplash del encabezado.
- Revisar dominio y compatibilidad con AdSense; esta actualización NO instala anuncios ni garantiza aprobación.
- Agregar fechas de publicación reales a las noticias y al esquema NewsArticle cuando el sistema las registre.
- Revisar política de privacidad y consentimiento antes de activar publicidad o analítica.

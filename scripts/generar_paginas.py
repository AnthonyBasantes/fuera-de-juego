from pathlib import Path
import json, re, html, xml.etree.ElementTree as ET
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
BASE="https://anthonybasantes.github.io/fuera-de-juego/"
DEST=ROOT/"noticias"
def e(s):return html.escape(str(s or ""),quote=True)
def main():
 data=json.loads((ROOT/"datos/publicadas.json").read_text(encoding="utf-8"))["noticias"]
 DEST.mkdir(exist_ok=True)
 urls=[BASE]+[BASE+x for x in ("contacto.html","privacidad.html","terminos.html") if (ROOT/x).exists()]
 expected=set()
 for a in data:
  if a.get("estado")!="aprobada":continue
  slug=a.get("id","")
  if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}",slug):raise ValueError("ID inválido: "+str(slug))
  if not all(isinstance(a.get(k),str) and a[k].strip() for k in ("title","desc","body","source_name","source_url")):raise ValueError("Noticia incompleta: "+slug)
  if urlparse(a["source_url"]).scheme!="https":raise ValueError("Fuente no HTTPS: "+slug)
  image=a.get("image","")
  if not isinstance(image,str) or not re.fullmatch(r"\./imagenes/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp|svg)",image):image="./imagenes/categoria-mundial.svg"
  image=BASE+image[2:]
  url=BASE+"noticias/"+slug+".html";urls.append(url);expected.add(slug+".html")
  title=e(a["title"]);desc=e(a["desc"][:160]);source=e(a["source_url"])
  paragraphs="\n".join("<p>"+e(t.strip())+"</p>" for t in re.split(r"\n\s*\n",a["body"]) if t.strip())
  credit=e(a.get("image_credit") or "Ilustración editorial de FUERA DE JUEGO. No representa una fotografía del acontecimiento.")
  ld=json.dumps({"@context":"https://schema.org","@type":"NewsArticle","headline":a["title"],"description":a["desc"],"mainEntityOfPage":url,"image":[image],"author":{"@type":"Organization","name":"FUERA DE JUEGO"},"publisher":{"@type":"Organization","name":"FUERA DE JUEGO"}},ensure_ascii=False).replace("<","\u003c")
  page="""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0b0e0c"><meta name="robots" content="index,follow"><title>__TITLE__ | FUERA DE JUEGO</title><meta name="description" content="__DESC__"><link rel="canonical" href="__URL__"><meta property="og:type" content="article"><meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESC__"><meta property="og:url" content="__URL__"><meta property="og:image" content="__IMAGE__"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">__LD__</script><style>:root{--lime:#bcff20}*{box-sizing:border-box}body{margin:0;background:#0b0e0c;color:#f6f8f4;font:16px/1.75 system-ui,Arial,sans-serif}a{color:var(--lime)}header,footer{padding:18px max(20px,calc((100vw - 860px)/2));border-bottom:1px solid #303831}header a{color:#fff;text-decoration:none;font-size:23px;font-weight:900}header strong{color:var(--lime)}main{max-width:820px;margin:auto;padding:25px 20px 65px}h1{font-size:clamp(30px,5vw,52px);line-height:1.13}.kicker{color:var(--lime);font-size:12px;font-weight:800;letter-spacing:2px}.lead{font-size:19px;color:#d5ddd4;font-weight:600}figure{margin:25px 0}figure img{width:100%;height:auto;display:block;border-radius:9px}figcaption{font-size:12px;color:#b7c0b7;margin-top:8px}article p{margin:0 0 20px}.source{background:#151916;border-left:3px solid var(--lime);padding:18px;margin-top:30px;overflow-wrap:anywhere}.back{display:inline-block;margin:20px 0;font-weight:700}footer{border-top:1px solid #303831;border-bottom:0;font-size:13px}footer a{margin-right:12px}</style></head><body><header><a href="../index.html">FUERA DE <strong>JUEGO</strong></a></header><main><a class="back" href="../index.html#noticias">← Volver a noticias</a><article><div class="kicker">__LABEL__</div><h1>__TITLE__</h1><p class="lead">__SUMMARY__</p><figure><img src="__IMAGE__" alt="Ilustración del artículo"><figcaption>__CREDIT__</figcaption></figure>__PARAGRAPHS__<div class="source">Fuente: <a href="__SOURCE__" target="_blank" rel="noopener noreferrer">__SOURCE_NAME__</a>. Información editorial de FUERA DE JUEGO.</div></article><a class="back" href="../index.html#noticias">← Más noticias</a></main><footer>© 2026 FUERA DE JUEGO · <a href="../contacto.html">Contacto</a><a href="../privacidad.html">Privacidad</a><a href="../terminos.html">Términos</a></footer></body></html>"""
  for key,value in {"TITLE":title,"DESC":desc,"URL":e(url),"IMAGE":e(image),"LD":ld,"LABEL":e(a.get("label","FÚTBOL")),"SUMMARY":e(a["desc"]),"CREDIT":credit,"PARAGRAPHS":paragraphs,"SOURCE":source,"SOURCE_NAME":e(a["source_name"])}.items():page=page.replace("__"+key+"__",value)
  (DEST/(slug+".html")).write_text(page,encoding="utf-8")
 for old in DEST.glob("*.html"):
  if old.name not in expected:old.unlink()
 ns="http://www.sitemaps.org/schemas/sitemap/0.9";ET.register_namespace("",ns)
 r=ET.Element("{"+ns+"}urlset")
 for url in urls:ET.SubElement(ET.SubElement(r,"{"+ns+"}url"),"{"+ns+"}loc").text=url
 ET.ElementTree(r).write(ROOT/"sitemap.xml",encoding="utf-8",xml_declaration=True)
 print("Noticias generadas:",len(expected),"URLs:",len(urls))
if __name__=="__main__":main()

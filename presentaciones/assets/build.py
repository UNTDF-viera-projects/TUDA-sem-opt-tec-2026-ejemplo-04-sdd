from pathlib import Path
import html,json,re
P=Path(__file__).resolve().parent.parent
def e(s):return html.escape(str(s))
def render(name,title,slides):
 sections=''.join(f'<section class="slide" id="{s["id"]}" data-title="{e(s["title"])}"><div class="brandline"><span><b>UNTDF</b>Introducción al Desarrollo Asistido por Agentes</span><span>{e(s["section"])} · 2026</span></div><header class="heading"><h1>{e(s["title"])}</h1><p class="subtitle">{e(s["sub"])}</p></header><div class="content">{s["body"]}</div></section>' for s in slides)
 index=''.join(f'<a href="#{s["id"]}/0" data-slide="{s["id"]}">{s["id"]} · {e(s["title"])}</a>' for s in slides)
 out=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · UNTDF</title><link rel="stylesheet" href="assets/theme.css"><script defer src="assets/deck.js"></script></head><body data-deck="{name}"><main class="stage"><div class="slides">{sections}</div><nav class="navigation" aria-label="Navegación de diapositivas"><button id="previous" aria-label="Diapositiva o fragmento anterior">←</button><button id="next" aria-label="Diapositiva o fragmento siguiente">→</button><button id="index-open">Secciones</button><a href="index.html">Materiales</a><a id="notes" class="notes-link" target="_blank">Notas</a><button id="fullscreen">Pantalla completa</button><span id="position" class="position" aria-live="polite"></span></nav></main><div id="index-overlay" class="index-overlay" hidden><section class="index-card" role="dialog" aria-modal="true" aria-labelledby="index-title"><button id="index-close" class="index-close">Cerrar</button><h2 id="index-title">{title} · Índice</h2><div class="index-grid">{index}</div></section></div></body></html>'''
 (P/f'{name}.html').write_text(out)
 notes=['# '+title+' · Guion docente','Cada ID enlaza a la diapositiva. Los estados base, F1 y F2 se distinguen en cada nota.']
 nh=[]
 for s in slides:
  text=f'## {s["id"]} · {s["title"]}\n\n- Propósito: {s["sub"]}\n- Explicación: {s["note"]}\n- Conclusión: {s.get("conclusion",s["sub"])}\n- Pregunta: {s["question"]}\n- Estado del ejemplo: {s["state"]}\n- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `{s["id"]}`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.\n'
  notes.append(text)
  nh.append(f'<section id="{s["id"]}"><h2><a href="../{name}.html#{s["id"]}/0">{s["id"]} · {e(s["title"])}</a></h2><p><b>Propósito:</b> {e(s["sub"])}</p><p><b>Explicación:</b> {e(s["note"])}</p><p><b>Conclusión:</b> {e(s.get("conclusion",s["sub"]))}</p><p><b>Pregunta:</b> {e(s["question"])}</p><p><b>Estado:</b> {e(s["state"])}</p><p><b>Recuperación:</b> usar documento, checkpoint y resultados guardados; volver a {s["id"]}.</p></section>')
 (P/'notas'/f'{name}.md').write_text('\n\n'.join(notes))
 (P/'notas'/f'{name}.html').write_text(f'<!doctype html><html lang="es"><meta charset="utf-8"><title>Notas · {title}</title><style>body{{max-width:1000px;margin:40px auto;background:#f4f1ec;color:#22242a;font:20px/1.5 system-ui;padding:20px}}section{{padding:24px 0;border-bottom:1px solid #ddd}}a{{color:#9f3329}}p{{margin:12px 0}}</style><h1>{title} · Notas docentes</h1>'+''.join(nh)+'</html>')

if __name__=='__main__':
 data=json.loads((P/'assets/content.json').read_text())
 titles={'fundamentos':'Fundamentos de SDD','openspec':'OpenSpec paso a paso','spec-kit':'Spec Kit paso a paso'}
 for name,slides in data.items():render(name,titles[name],slides)
 print('Regenerados HTML y notas desde content.json')

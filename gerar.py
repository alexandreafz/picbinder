"""Gera as páginas da política de privacidade (privacy/<idioma>.html) a partir
de fonte/<idioma>.md. Rodar: python3 gerar.py"""
import html, re, pathlib

IDIOMAS = [('pt','Português'),('en','English'),('es','Español'),('fr','Français'),
           ('de','Deutsch'),('hi','हिन्दी'),('zh','中文')]
CSS = """
:root{--fundo:#f7f9ff;--texto:#1a1c20;--suave:#44474f;--azul:#1a63e0;--cartao:#fff;--linha:#dfe3eb}
@media (prefers-color-scheme:dark){:root{--fundo:#111318;--texto:#e2e2e9;--suave:#c4c6d0;--azul:#a9c7ff;--cartao:#1d2024;--linha:#33363d}}
*{box-sizing:border-box}
body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 64px}
nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}
nav a{padding:4px 12px;border:1px solid var(--linha);border-radius:999px;color:var(--suave);text-decoration:none;font-size:14px}
nav a[aria-current]{background:var(--azul);border-color:var(--azul);color:var(--fundo)}
h1{font-size:28px;line-height:1.25;margin:0 0 4px}
.data{color:var(--suave);margin:0 0 24px}
h2{font-size:19px;margin:32px 0 8px}
a{color:var(--azul);overflow-wrap:anywhere}
ul{padding-left:22px}li{margin:6px 0}
.resumo{background:var(--cartao);border:1px solid var(--linha);border-radius:16px;padding:4px 20px}
"""

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', t)
    t = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', t)
    return t

def converter(md):
    saida, lista, titulo, no_resumo = [], False, '', False
    for linha in md.strip().splitlines():
        if linha.startswith('- '):
            if not lista: saida.append('<ul>'); lista = True
            saida.append(f'<li>{inline(linha[2:])}</li>'); continue
        if lista: saida.append('</ul>'); lista = False
        if not linha.strip(): continue
        if linha.startswith('# '):
            titulo = linha[2:]; saida.append(f'<h1>{html.escape(titulo)}</h1>')
        elif linha.startswith('_') and linha.endswith('_'):
            saida.append(f'<p class="data">{html.escape(linha[1:-1])}</p>')
        elif linha.startswith('## '):
            if no_resumo: saida.append('</div>'); no_resumo = False
            saida.append(f'<h2>{html.escape(linha[3:])}</h2>')
            if len([s for s in saida if s.startswith('<h2>')]) == 1:
                saida.append('<div class="resumo">'); no_resumo = True
        else:
            saida.append(f'<p>{inline(linha)}</p>')
    if lista: saida.append('</ul>')
    if no_resumo: saida.append('</div>')
    return titulo, '\n'.join(saida)

def pagina(codigo, titulo, corpo):
    nav = ''.join(f'<a href="{c}.html" lang="{c}"' + (' aria-current="page"' if c == codigo else '') + f'>{n}</a>'
                  for c, n in IDIOMAS)
    return f"""<!DOCTYPE html>
<html lang="{codigo}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>{CSS}</style>
</head>
<body><main>
<nav>{nav}</nav>
{corpo}
</main></body>
</html>
"""

pasta = pathlib.Path('privacy'); pasta.mkdir(exist_ok=True)
for c, _ in IDIOMAS:
    titulo, corpo = converter((pathlib.Path('fonte') / f'{c}.md').read_text())
    (pasta / f'{c}.html').write_text(pagina(c, titulo, corpo))

# privacy/ sem idioma: abre no idioma do navegador (inglês se não houver).
codigos = [c for c, _ in IDIOMAS]
lista = ''.join(f'<li><a href="{c}.html">{n}</a></li>' for c, n in IDIOMAS)
(pasta / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PicBinder Privacy Policy</title>
<script>
var c={codigos!r};var l=(navigator.language||'en').slice(0,2).toLowerCase();
location.replace((c.indexOf(l)>=0?l:'en')+'.html');
</script>
<style>{CSS}</style></head>
<body><main><h1>PicBinder Privacy Policy</h1><ul>{lista}</ul></main></body></html>
""")
pathlib.Path('index.html').write_text("""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PicBinder</title><meta http-equiv="refresh" content="0; url=privacy/">
</head><body><a href="privacy/">PicBinder Privacy Policy</a></body></html>
""")
print('ok')

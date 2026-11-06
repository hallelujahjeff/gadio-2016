"""Package the committed full JSON for GitHub Pages; no metadata API requests."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'data/radios-all.json'
    snapshot = json.loads(source.read_text(encoding='utf8'))
    items = snapshot['items']
    assert snapshot['count'] == len(items) == len({i['id'] for i in items})
    assert all(isinstance(i['publishedTimestamp'], int) for i in items)
    items.sort(key=lambda i:i['publishedTimestamp'],reverse=True)
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'public',out,dirs_exist_ok=True)
    (out/'data').mkdir(exist_ok=True)
    # Reuse previously bundled covers if present; other covers use their source URLs.
    for item in items:
        name = item.get('image','').rsplit('/',1)[-1]
        if name and (out/'images'/name).is_file():
            item['image'] = 'images/' + name
    (out/'data/radios-all.json').write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf8')
    html = (out/'index.html').read_text(encoding='utf8')
    html = html.replace('href="/"','href="./"').replace('href="/favicon.svg"','href="favicon.svg"').replace('href="/style.css','href="style.css').replace('src="/app.js','src="app.js').replace('src="/analytics.js','src="analytics.js').replace('src="/assets/','src="assets/')
    (out/'index.html').write_text(html,encoding='utf8')
    css = (out/'style.css').read_text(encoding='utf8').replace("url('/assets/", "url('assets/")
    (out/'style.css').write_text(css,encoding='utf8')
    js = (out/'app.js').read_text(encoding='utf8')
    (out/'app.js').write_text('window.GADIO_STATIC = true;\n'+js,encoding='utf8')
    (out/'.nojekyll').touch()
    print(f'Packaged {len(items)} programs from committed JSON; no metadata API requests')

if __name__ == '__main__': main()


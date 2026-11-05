"""Build a self-contained GitHub Pages site from live Gcores data."""
import argparse
import concurrent.futures
import datetime as dt
import json
import re
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TZ = dt.timezone(dt.timedelta(hours=8))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--direct', action='store_true')
    args = parser.parse_args()
    opener = urllib.request.build_opener(*([urllib.request.ProxyHandler({})] if args.direct else []))
    def get(url):
        for attempt in range(3):
            try:
                with opener.open(urllib.request.Request(url, headers={'User-Agent':'Gadio2016/1.0'}), timeout=30) as response:
                    return response.read()
            except Exception:
                if attempt == 2: raise
                time.sleep(attempt + 1)
    today = dt.datetime.now(TZ).date()
    try: historical = today.replace(year=today.year - 10)
    except ValueError: historical = today.replace(year=today.year - 10, day=28)
    # A small forward buffer lets the browser advance during delayed scheduled builds.
    through = historical + dt.timedelta(days=14)
    cutoff = int(dt.datetime.combine(through + dt.timedelta(days=1), dt.time(), TZ).timestamp()) - 1
    rows, categories = [], {}
    for offset in range(0, 5000, 100):
        params = {'filter[to]':cutoff, 'sort':'-published-at', 'page[limit]':100, 'page[offset]':offset,
                  'include':'category', 'fields[categories]':'name',
                  'fields[radios]':'title,published-at,desc,thumb,cover,vol,category,duration'}
        payload = json.loads(get('https://www.gcores.com/gapi/v1/radios?' + urllib.parse.urlencode(params)))
        categories.update({x['id']:x['attributes']['name'] for x in payload.get('included',[]) if x['type']=='categories'})
        rows.extend(payload['data'])
        if len(payload['data']) < 100: break
    else: raise RuntimeError('Unexpected catalog size; refusing incomplete publication')
    if not rows: raise RuntimeError('No programs returned; retaining previous deployment')
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'public', out, dirs_exist_ok=True)
    (out/'data').mkdir(exist_ok=True)
    (out/'images').mkdir(exist_ok=True)
    items = []
    for row in rows:
        a = row['attributes']
        if dt.datetime.fromisoformat(a['published-at']).timestamp() > cutoff: continue
        cat = (row.get('relationships',{}).get('category',{}).get('data') or {}).get('id')
        image = a.get('cover') or a.get('thumb')
        if image and not re.fullmatch(r'[A-Za-z0-9_-]+\.(?:jpg|jpeg|png|gif|webp)',image,re.I): image = None
        items.append({'id':row['id'],'title':a['title'],'description':a.get('desc') or '',
                      'date':a['published-at'][:10],'categoryId':cat,'category':categories.get(cat,'电台节目'),
                      'vol':a.get('vol'),'duration':a.get('duration'),
                      'image':'images/'+image if image else '', 'url':'https://www.gcores.com/radios/'+row['id']})
    def download(name):
        target = out/name
        if not target.exists(): target.write_bytes(get('https://image.gcores.com/'+target.name))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(download, sorted({i['image'] for i in items if i['image']})))
    items.sort(key=lambda x:x['date'],reverse=True)
    (out/'data/episodes.json').write_text(json.dumps({'items':items,'through':through.isoformat()},ensure_ascii=False),encoding='utf8')
    html = (out/'index.html').read_text(encoding='utf8')
    html = html.replace('href="/"','href="./"').replace('href="/favicon.svg"','href="favicon.svg"').replace('href="/style.css"','href="style.css"').replace('src="/app.js"','src="app.js"').replace('src="/assets/','src="assets/')
    (out/'index.html').write_text(html,encoding='utf8')
    css = (out/'style.css').read_text(encoding='utf8').replace("url('/assets/", "url('assets/")
    (out/'style.css').write_text(css,encoding='utf8')
    js = (out/'app.js').read_text(encoding='utf8')
    (out/'app.js').write_text('window.GADIO_STATIC = true;\n'+js,encoding='utf8')
    (out/'.nojekyll').touch()
    print(f'Built {len(items)} programs; browser cutoff {historical}; data buffer through {through}')

if __name__ == '__main__': main()

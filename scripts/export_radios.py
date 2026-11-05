"""Export all currently public Gcores radio metadata; no media downloads.

python scripts/export_radios.py --direct
"""
import argparse
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TZ = dt.timezone(dt.timedelta(hours=8))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--direct', action='store_true')
    args = parser.parse_args()
    opener = urllib.request.build_opener(*([urllib.request.ProxyHandler({})] if args.direct else []))
    out = ROOT / 'data' / 'radios-all.json'
    out.parent.mkdir(exist_ok=True)
    partial = out.with_suffix('.partial.json')
    started = dt.datetime.now(TZ)
    cutoff = int(started.timestamp())
    items, categories, seen = [], {}, set()
    offset, pages, duplicates = 0, 0, 0
    cursor = cutoff
    while True:
        params = {'filter[to]':cursor, 'sort':'-published-at', 'page[limit]':100,
                  'page[offset]':offset, 'include':'category', 'fields[categories]':'name',
                  'fields[radios]':'title,published-at,desc,thumb,cover,vol,category,duration,owner-type,is-require-privilege,is-free'}
        url = 'https://www.gcores.com/gapi/v1/radios?' + urllib.parse.urlencode(params)
        for attempt in range(4):
            try:
                with opener.open(urllib.request.Request(url, headers={'User-Agent':'Gadio2016/1.0'}),timeout=30) as response:
                    payload = json.load(response)
                break
            except Exception:
                if attempt == 3: raise
                time.sleep(2 ** attempt)
        rows = payload['data']
        categories.update({c['id']:c['attributes']['name'] for c in payload.get('included',[]) if c['type']=='categories'})
        for row in rows:
            if row['id'] in seen:
                duplicates += 1
                continue
            seen.add(row['id'])
            a = row['attributes']
            published = dt.datetime.fromisoformat(a['published-at'])
            assert published.tzinfo is not None and published.timestamp() <= cutoff
            cat = (row.get('relationships',{}).get('category',{}).get('data') or {}).get('id')
            items.append({'id':row['id'], 'title':a['title'], 'description':a.get('desc') or '',
                          'publishedAt':a['published-at'], 'publishedTimestamp':int(published.timestamp()),
                          'date':published.astimezone(TZ).date().isoformat(),
                          'categoryId':cat, 'category':categories.get(cat,'电台节目'),
                          'vol':a.get('vol'), 'duration':a.get('duration'),
                          'image':'https://image.gcores.com/'+(a.get('cover') or a.get('thumb')) if a.get('cover') or a.get('thumb') else '',
                          'thumbnail':'https://image.gcores.com/'+a['thumb'] if a.get('thumb') else '',
                          'url':'https://www.gcores.com/radios/'+row['id'],
                          'ownerType':a.get('owner-type'), 'requiresPrivilege':a.get('is-require-privilege'), 'isFree':a.get('is-free')})
        pages += 1
        if rows:
            last_stamp = int(dt.datetime.fromisoformat(rows[-1]['attributes']['published-at']).timestamp())
            trailing = sum(int(dt.datetime.fromisoformat(r['attributes']['published-at']).timestamp()) == last_stamp for r in rows)
            offset = offset + trailing if last_stamp == cursor else trailing
            cursor = last_stamp
        partial.write_text(json.dumps({'cutoff':cutoff,'offset':offset,'items':items},ensure_ascii=False),encoding='utf8')
        if pages % 10 == 0 or len(rows) < 100:
            print(f'Pages {pages}; unique programs {len(items)}; last date {items[-1]["date"] if items else "none"}',flush=True)
        if not rows: break
        # Follow actual returned page sizes; confirm end with an empty page.
        if pages > 1000: raise RuntimeError('Unexpected pagination; incomplete export retained as partial')
        time.sleep(.1)
    if duplicates: raise RuntimeError(f'{duplicates} duplicate records across pages; rerun to verify stable pagination')
    items.sort(key=lambda i:i['publishedTimestamp'],reverse=True)
    result = {'schemaVersion':1,'source':'https://www.gcores.com/gapi/v1/radios',
              'scope':'Public radio records returned by the current API, including official and resident podcasts; excludes unpublished/deleted/inaccessible records.',
              'exportedAt':dt.datetime.now(TZ).isoformat(),'cutoffTimestamp':cutoff,
              'timestampUnit':'seconds','displayTimezone':'Asia/Shanghai',
              'count':len(items),'pagesFetched':pages,'categories':categories,'items':items}
    partial.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    partial.replace(out)
    print(f'Complete: {out} ({out.stat().st_size:,} bytes)',flush=True)

if __name__ == '__main__': main()


"""Repeatable Play review monitor. Keyword tags are provisional, not verified labels.
Run: python tracker.py --offline --as-of 2026-10-29
Live: python tracker.py (requires the revised fetch_reviews.py alongside this file).
"""
import argparse
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from themes import THEMES, tag

ROOT = Path(__file__).resolve().parent
DATA, OUT = ROOT / 'data', ROOT / 'out'
MAIN = 'com.moveinsync.ets'
APPS = {
    MAIN: 'MoveInSync employee',
    'com.moveinsync.driver.lite': 'MoveInSync Partner Lite',
    'com.moveinsync.driver.dco': 'MoveInSync Driver Partner',
    'field.moveinsync.ets': 'MoveInSync Field',
    'in.mtap.iincube.safetrax.commuter': 'Safetrax Commuter',
    'com.routematic.employee': 'Routematic',
}
FILES = {MAIN: 'ets_en.jsonl', 'in.mtap.iincube.safetrax.commuter': 'safetrax_en.jsonl',
         'com.routematic.employee': 'routematic_en.jsonl'}


def write_json(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    tmp.replace(path)


def summary(rows):
    low = [r for r in rows if r['score'] <= 2]
    replied = [r for r in low if (r.get('replyContent') or '').strip()]
    return dict(reviews=len(rows), avg=round(sum(r['score'] for r in rows)/len(rows), 3) if rows else None,
                low_rated=len(low), one_star=sum(r['score']==1 for r in rows),
                low_rated_percent=round(100*len(low)/len(rows), 2) if rows else None,
                low_with_reply=len(replied), reply_coverage_percent=round(100*len(replied)/len(low), 2) if low else None,
                replies_predating_review=sum(bool(r.get('repliedAt')) and r['repliedAt'] < r['at'] for r in replied))


def refresh():
    from google_play_scraper import app
    fields = ['ts','app_id','score','ratings','reviews','h1','h2','h3','h4','h5','version']
    path = DATA/'snapshots.csv'
    snapshots = []
    for app_id in APPS:
        d = app(app_id, lang='en', country='in')
        snapshots.append([datetime.now(timezone.utc).isoformat(), app_id, d['score'], d['ratings'],
                          d['reviews'], *d['histogram'], d.get('version')])
    new = not path.exists() or path.stat().st_size == 0
    with path.open('a', encoding='utf-8', newline='') as f:
        w=csv.writer(f)
        if new: w.writerow(fields)
        w.writerows(snapshots)
    for app_id, filename in FILES.items():
        subprocess.run([sys.executable, str(ROOT/'fetch_reviews.py'), app_id,
                        str(DATA/filename), 'en', 'in'], check=True)


def compute(as_of):
    end = as_of + timedelta(days=1)
    month_index = as_of.year*12 + as_of.month - 1 - 11
    start = date(month_index//12, month_index%12+1, 1)
    alerts, peers, main = [], {}, []
    collection = {}
    for app_id, filename in FILES.items():
        path = DATA/filename
        with path.open(encoding='utf-8-sig') as f:
            rows = [json.loads(line) for line in f if line.strip()]
        ids = [r.get('reviewId') for r in rows]
        if not rows or not all(ids) or len(ids)!=len(set(ids)):
            raise ValueError(f'{filename}: empty data, missing IDs or duplicate IDs')
        for r in rows:
            if r.get('score') not in [1,2,3,4,5]: raise ValueError(f'{filename}: invalid score')
            r['_date'] = date.fromisoformat(r['at'][:10])
        selected = [r for r in rows if start <= r['_date'] < end]
        peers[app_id] = summary(selected)
        meta_path = path.with_suffix('.meta.json')
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding='utf-8-sig'))
            collected = datetime.fromisoformat(meta['finished_at_utc']).date()
            age = (as_of-collected).days
            collection[app_id] = dict(status=meta.get('status'), finished_at_utc=meta['finished_at_utc'], age_days=age)
            if meta.get('status')!='exhausted' or age>7:
                alerts.append(f'{APPS[app_id]}: incomplete or stale collection; refresh before acting on alerts.')
        else:
            alerts.append(f'{APPS[app_id]}: collection metadata missing; freshness unknown.')
        if app_id==MAIN: main=rows
    main = [r for r in main if r['_date'] < end]
    recent = [r for r in main if r['_date'] >= start]
    low = [r for r in recent if r['score']<=2]
    for r in low: r['_tags'] = tag(r.get('content'))
    counts = Counter(t for r in low for t in r['_tags'])
    themes = [dict(key=k,label=THEMES[k]['label'],suggested_owner=THEMES[k]['owner'],
                   reviews=v,percent_of_low=round(100*v/len(low),2)) for k,v in counts.most_common()]
    for k in THEMES:
        this = sum(k in r['_tags'] and r['_date'] >= end-timedelta(days=7) for r in low)
        previous = sum(k in r['_tags'] and end-timedelta(days=63)<=r['_date']<end-timedelta(days=7) for r in low)
        if this>=5 and (previous==0 or this>=2*(previous/8)):
            alerts.append(f'Keyword signal {k}: {this} in last 7 days; prior 8-week average {previous/8:.2f}. Review matching text.')
    safety = sum('safety' in r['_tags'] and r['_date']>=end-timedelta(days=7) for r in low)
    if safety: alerts.append(f'Safety keyword triage: inspect {safety} recent low-rated reviews; tags may be false positives.')
    last30 = summary([r for r in main if r['_date']>=end-timedelta(days=30)])
    if last30['reply_coverage_percent'] is not None and last30['reply_coverage_percent']<90:
        alerts.append(f"Last 30 days: {last30['reply_coverage_percent']}% of low-rated reviews have a reply; proposed target 90%. Replies do not establish resolution.")
    months, versions = defaultdict(list), defaultdict(list)
    for r in recent:
        months[r['at'][:7]].append(r)
        if r.get('reviewCreatedVersion'): versions[str(r['reviewCreatedVersion'])].append(r)
    releases = [dict(version=k,**summary(v),small_sample=len(v)<30) for k,v in sorted(versions.items())]
    for r in releases:
        if r['reviews']>=30 and r['one_star']/r['reviews']>0.30:
            alerts.append(f"Version investigation: {r['version']} has {r['one_star']}/{r['reviews']} one-star reviews in the reporting window. Association, not proof of regression.")
    store, changes = {}, None
    snap_path = DATA/'snapshots.csv'
    if snap_path.exists():
        with snap_path.open(encoding='utf-8-sig',newline='') as f:
            snaps=[s for s in csv.DictReader(f) if s['ts'][:10]<end.isoformat()]
        for s in sorted(snaps,key=lambda x:x['ts']):
            store[s['app_id']]=dict(name=APPS.get(s['app_id'],s['app_id']),score=float(s['score']),
                ratings=int(s['ratings']),as_of=s['ts'])
        ss=sorted([s for s in snaps if s['app_id']==MAIN],key=lambda x:x['ts'])
        if len(ss)>=2:
            a,b=ss[-2:]
            changes=dict(since=a['ts'],until=b['ts'],net_rating_count=int(b['ratings'])-int(a['ratings']),
                         net_histogram=[int(b[f'h{i}'])-int(a[f'h{i}']) for i in range(1,6)],
                         note='Net changes include additions, edits, removals and source corrections; not a new-rating distribution.')
        for k,s in store.items():
            if (as_of-date.fromisoformat(s['as_of'][:10])).days>7: alerts.append(f'{s["name"]}: store snapshot is older than 7 days.')
    metrics=dict(generated_utc=datetime.now(timezone.utc).isoformat(),as_of=as_of.isoformat(),
        period_start=start.isoformat(),period_end_exclusive=end.isoformat(),collection=collection,store=store,
        latest_review=max((r['at'] for r in main),default=None),last12=peers[MAIN],peers=peers,last30=last30,
        net_rating_changes=changes,theme_method='Provisional keyword matches; separate from original LLM labels and AI-assisted sample check.',
        themes=themes,monthly=[dict(month=k,**summary(v),partial_month=k==as_of.strftime('%Y-%m') and end.day!=1) for k,v in sorted(months.items())],
        releases=releases,missing_version=sum(not r.get('reviewCreatedVersion') for r in recent),alerts=alerts,
        limitations=['Review timestamps used as supplied; timezone unspecified. As-of filters current records, not historical versions of edited reviews.',
                      'English/India request does not prove reviewer residence or complete coverage.',
                      'Reply coverage counts any nonempty reply; an older reply may predate edited review text.',
                      'Keyword tagging is multi-label and can misinterpret praise, negation and vague complaints.'])
    write_json(OUT/'metrics.json',metrics)
    with (OUT/'reviews_tagged.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['review_id','date','stars','text','provisional_keyword_themes'])
        for r in low: w.writerow([r['reviewId'],r['at'],r['score'],r.get('content',''),';'.join(r['_tags'])])
    return metrics


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--as-of',type=date.fromisoformat,help='Reporting date YYYY-MM-DD; defaults to current India date')
    args=parser.parse_args()
    if args.as_of and not args.offline: parser.error('--as-of requires --offline')
    DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    try:
        if not args.offline: refresh()
        today=(datetime.now(timezone.utc)+timedelta(hours=5,minutes=30)).date()
        result=compute(args.as_of or today)
        print(json.dumps(result['last12'],indent=2))
        print('\nAlerts (investigation signals):')
        for alert in result['alerts']: print('-',alert)
        print('\nSaved out/metrics.json and out/reviews_tagged.csv')
    except Exception as exc:
        print(f'Tracker failed: {exc}. Existing outputs may be from an earlier run.',file=sys.stderr)
        sys.exit(1)

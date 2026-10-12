import json, sys, collections
for d in sys.argv[1:]:
    r = json.load(open(d + '/results.json'))['blockrate']['default']
    for h, v in r['holes'].items():
        rows = v['rows']
        oc = collections.Counter(x['outcome'] for x in rows)
        print(d, h, 'n', len(rows), 'blocked', sum(x['blocked'] for x in rows), '%.1f%%' % (100 * sum(x['blocked'] for x in rows) / len(rows)),
              'touched', sum(x['touched'] for x in rows), 'flags', sum(x['flags'] for x in rows), dict(oc), {k: v[k] for k in v if k != 'rows'})
    print(' issues', r['issues'])

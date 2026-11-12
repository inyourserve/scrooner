import json, re, sys
def load(fn):
    if fn.endswith('.json'): return json.load(open(fn))
    t = open(fn).read()
    i = t.find('[{'); 
    # the payload may be a JSON string with escaped quotes
    if '\\"' in t[:2000]:
        s = json.loads(t)['result'] if t.lstrip().startswith('{') else t
        i = s.find('[{'); j = s.rfind('}]') + 2
        return json.loads(s[i:j])
    j = t.rfind('}]') + 2
    return json.loads(t[i:j])
if __name__ == '__main__':
    d = load(sys.argv[1]); print(len(d), d[0].keys(), [(x['company_id'], x['accession'], x['fy'], x['rn'], len(x['reps'] or []), len(x['lines'] or [])) for x in d][:40])

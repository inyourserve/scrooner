"""Read the latest 10-K face statements for a list of CIKs (argv[1] = file with one cik per line, argv[2] = out dir)."""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readfiling as rf, sec
ciks = [l.strip() for l in open(sys.argv[1]) if l.strip()]
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
t0 = time.time()
for i, c in enumerate(ciks):
    p = f"{out}/{c}.json"
    if os.path.exists(p):
        continue
    try:
        r = rf.read_company(c)
    except Exception as e:  # keep going; record the failure
        r = {"cik": c, "err": "exception:" + repr(e)[:200]}
    json.dump(r, open(p, "w"))
    if i % 20 == 0:
        print(i, len(ciks), round(time.time() - t0), sec.COUNT, flush=True)
print("done", sec.COUNT, flush=True)

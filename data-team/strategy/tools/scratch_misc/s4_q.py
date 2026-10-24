import sys
from scrooner_pipeline.db.connection import get_connection
sql=open(sys.argv[1]).read()
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("set default_transaction_read_only = on")
        cur.execute("set statement_timeout='60s'")
        cur.execute("select count(*) from pg_stat_activity"); n=cur.fetchone()[0]
        print('# pg_stat_activity',n, file=sys.stderr)
        if n>40: sys.exit('gate')
        for stmt in [s for s in sql.split(';\n') if s.strip()]:
            cur.execute(stmt)
            if cur.description:
                print('\t'.join(d.name for d in cur.description))
                for r in cur.fetchall(): print('\t'.join(str(x) for x in r))

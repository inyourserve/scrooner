import os,sys,psycopg
from dotenv import dotenv_values
u=dotenv_values('/Users/vikash/scrooner/pipeline/.env')['DATABASE_URL']
with psycopg.connect(u,connect_timeout=15) as c:
    cur=c.cursor()
    cur.execute("set statement_timeout=20000")
    cur.execute("select count(*) from pg_stat_activity")
    print(cur.fetchone())
    cur.execute("show default_transaction_read_only"); print(cur.fetchone())

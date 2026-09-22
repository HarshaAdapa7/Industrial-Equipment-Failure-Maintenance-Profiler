import psycopg2

regions = [
    "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ap-northeast-2",
    "us-east-1", "us-west-1", "eu-central-1", "eu-west-1", "eu-west-2",
    "sa-east-1", "ca-central-1", "me-central-1"
]

ref = "frfkburreisufcdkqpji"
pwd = "Harsha%409515445632"

for r in regions:
    host = f"aws-0-{r}.pooler.supabase.com"
    conn_str = f"postgresql://postgres.{ref}:{pwd}@{host}:6543/postgres?sslmode=require"
    try:
        conn = psycopg2.connect(conn_str)
        print(f"SUCCESS MATCH! Region: {r} Host: {host}")
        conn.close()
        break
    except Exception as e:
        err_msg = str(e)
        if "tenant/user" not in err_msg and "ENOTFOUND" not in err_msg:
            print(f"REGION MATCH FOR {r}! Error: {err_msg}")
        else:
            pass

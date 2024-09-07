import psycopg2
from dotenv import load_dotenv

load_dotenv()
import uuid

null_uuid_raw = uuid.uuid4()

from os import getenv

if not getenv("HASDB"):
    raise Exception("No PostGres found")
db = psycopg2.connect(
    host=getenv("DBHOST"),
    user=getenv("DBUSER"),
    port=getenv("DBPORT"),
    password=getenv("DBPASSWORD"),
    dbname=getenv("DBNAME"),
)
# null_uuid = psycopg2.extensions.adapt(null_uuid_raw).getquoted()
with db.cursor() as cur:
    # cur.execute("USE tags")
    # create table
    cur.execute(
        "CREATE TABLE taginfo (id VARCHAR(200), name VARCHAR(60), title VARCHAR(60), content VARCHAR(4000), owner VARCHAR(19))"
    )
    # insert default tag
    cur.execute(
        f"INSERT INTO taginfo VALUES('{null_uuid_raw.hex}', 'null', 'null', 'tag not found', '716306888492318790', '961063229168164864')"
    )
    db.commit()

print("Database setup completed")

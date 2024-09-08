#Copyright (c) 2024 - present, MaskDuck

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

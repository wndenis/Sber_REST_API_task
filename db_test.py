import psycopg2
import time

db_boilerplate = """DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "name" character varying(80) NOT NULL,
    "age" smallint NOT NULL
) WITH (oids = false);

INSERT INTO "users" ("id", "name", "age") VALUES
(0,	'Peter Jackson',	42),
(1,	'John Dow',	252),
(2,	'Baba Dusya',	89),
(3,	'Thomas the Train',	251),
(4,	'Виктор Зубов',	22),
(5,	'Дарья Игонина',	35),
(6,	'Евгений Автобусов',	4);"""


class db:
    def __init__(self):
        self.conn = None
        self.establish_connection()

    def establish_connection(self):
        while not self.conn:
            time.sleep(1)
            try:
                self.conn = psycopg2.connect(host="db_docker",
                                        dbname="api_db",
                                        user="postgres",
                                        password="test")
            except psycopg2.OperationalError as e:
                pass

    def recreate(self):
        cur = self.conn.cursor()
        cur.execute(db_boilerplate)
        self.conn.commit()
        cur.close()


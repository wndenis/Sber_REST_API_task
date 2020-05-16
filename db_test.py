import psycopg2
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

def test_connection():
    # connection = pg.connect("host='db_docker' dbname=api_db user=postgres password='test'")
    # df = pd.read_sql_query('select * from category', con=connection)
    # print(df)

    # conn = psycopg2.connect(host="db_docker",
    #                         # port=5432,
    #                         dbname="api_db",
    #                         user="postgres",
    #                         password="test")
    conn = psycopg2.connect("host=db_docker dbname=api_db user=postgres password=test")



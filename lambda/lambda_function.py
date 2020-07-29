import json
import os
import psycopg2
import psycopg2.extras
import sys


def lambda_handler(event, context):
  REDSHIFT_DATABASE = os.environ['REDSHIFT_DATABASE']
  REDSHIFT_USER = os.environ['REDSHIFT_USER']
  REDSHIFT_PASSWD = os.environ['REDSHIFT_PASSWD']
  REDSHIFT_PORT = os.environ['REDSHIFT_PORT']
  REDSHIFT_ENDPOINT = os.environ['REDSHIFT_ENDPOINT']
  REDSHIFT_QUERY =  str(os.environ['REDSHIFT_QUERY'])
  print (REDSHIFT_QUERY)
  try:
    conn = psycopg2.connect(
      dbname=REDSHIFT_DATABASE,
      user=REDSHIFT_USER,
      password=REDSHIFT_PASSWD,
      port=REDSHIFT_PORT,
      host=REDSHIFT_ENDPOINT)
    print ("connected to db...")
  except Exception as ERROR:
    print("Connection Issue: " + str(ERROR))
    sys.exit(1)

  try:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print(cursor.execute(REDSHIFT_QUERY))
    cursor.close()
    conn.commit()
    conn.close()
  except Exception as ERROR:
    print("Execution Issue: " + str(ERROR))
    sys.exit(1)
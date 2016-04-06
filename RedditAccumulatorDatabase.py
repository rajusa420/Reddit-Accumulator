import os
import pprint
import psycopg2
import sys

class RedditAccumulatorDatabase:
    connection = None

    def connect(self):
        try:
            password = os.getenv("REDDIT_DB_PASS")
            self.connection = psycopg2.connect(database='RedditTest', user='reddituser', password=password)
            cur = self.connection.cursor()
            cur.execute('SELECT version()')
            ver = cur.fetchone()
            print(ver)
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            sys.exit(1)
        finally:
            if self.connection:
                self.connection.close()
        return
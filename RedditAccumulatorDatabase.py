import os
import pprint
import psycopg2
import sys

class RedditAccumulatorDatabase:
    connection = None
    cursor = None

    def __del__(self):
        if self.connection:
            self.connection.close()

    def connect(self):
        try:
            password = os.getenv("REDDIT_DB_PASS")
            self.connection = psycopg2.connect(database='RedditTest', user='reddituser', password=password)
            self.cursor = self.connection.cursor()
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            sys.exit(1)
        return

    def printTablesAvailable(self):
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            self.cursor.execute(query)
            test = self.cursor.fetchall()
            for tableName in test:
                pprint.pprint(tableName)
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)

    def deleteAllArticles(self):
        try:
            self.cursor.execute("DELETE FROM \"RedditTopPosts\"")
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)

    def getArticleCount(self):
        try:
            self.cursor.execute("SELECT COUNT(id) FROM \"RedditTopPosts\"")
            countRecord = self.cursor.fetchone()
            return countRecord[0]
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)

    def saveArticle(self, name, title, url, score, subreddit):
        try:
            query = "INSERT INTO \"RedditTopPosts\" (name, title, url, score, date, subreddit) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, (name, title, url, score, "now", subreddit))
            self.connection.commit()
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)
            self.connection.rollback()

    def getArticlesForSubreddit(self, subreddit):
        try:
            self.cursor.execute("SELECT * FROM \"RedditTopPosts\" where subreddit=%s", (subreddit))
            return self.cursor.fetchall
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)

    def getArticleCountForSubreddit(self, subreddit):
        try:
            self.cursor.execute("SELECT COUNT(id) FROM \"RedditTopPosts\" where subreddit=%s", (subreddit))
            countRecord = self.cursor.fetchone()
            return countRecord[0]
        except psycopg2.DatabaseError as e:
            print('Error %s' % e)


class oracleDB:
    def __conn(self):
        try:
            import cx_Oracle
            from auth import oracle

            user = oracle.user
            pw = oracle.pw
            host = oracle.host
            port = oracle.port
            sid = oracle.sid

            conn = cx_Oracle.connect(user, pw, host + port + sid)
            c = conn.cursor()

            return c, conn
        except Exception as e:
            return str(e)

    def fetch(self, sql):
        try:
            c, conn = self.__conn()

            c.execute(sql)
            return c.fetchall()
        except Exception as e:
            return str(e)

    def update(self, sql):
        try:
            c, conn = self.__conn()

            c.execute(sql)
            conn.commit()
            c.close()
            conn.close()
            return 'success'
        except Exception as e:
            return str(e)


class mysqlDB:
    def conn(this):
        try:
            import MySQLdb
            from auth import mysql

            user = mysql.user
            pw = mysql.pw
            host = mysql.host
            db = mysql.db

            conn = MySQLdb.connect(host=host, user=user, passwd=pw, db=db)
            c = conn.cursor()

            return c, conn
        except Exception as e:
            return str(e)

    def fetch(this, sql):
        try:
            c, conn = this.conn()
            c.execute(sql)

            return c.fetchall()
        except Exception as e:
            return str(e)

    def update(self, sql):
        try:
            c, conn = self.conn()

            c.execute(sql)
            conn.commit()
            c.close()
            conn.close()
            return 'success'
        except Exception as e:
            return str(e)

class cassandraDB:
    def conn(self):
        from cassandra.cluster import Cluster
        import datetime
        import uuid

        try:
            # port is changed for docker access port
            session = Cluster(port=32774).connect(keyspace='demo')

            ''' create keyspace '''
            # session.execute(
            #     "CREATE KEYSPACE IF NOT EXISTS demo WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")

            ''' create table '''
            # session.execute(
            #     "CREATE TABLE IF NOT EXISTS userbase (user_id timeuuid PRIMARY KEY, added_date timestamp, first_name text, last_name text, email text);")

            ''' insert some data '''
            # session.execute(
            #     """
            #     INSERT INTO userbase (user_id, added_date, first_name, last_name, email)
            #     VALUES (%(user_id)s, %(added_date)s, %(first_name)s, %(last_name)s, %(email)s)
            #     """,
            #     {'user_id': uuid.uuid1(), 'added_date': datetime.datetime.utcfromtimestamp(0), 'first_name': 'ervin', 'last_name': 'pora',
            #      'email': 'smtg'}
            # )

            result = session.execute("SELECT * FROM userbase")

            for r in result:
                print(r.user_id, r.first_name, r.last_name, r.email, r.added_date)

            return "done"
        except Exception as e:
            return str(e)


class mongoDB:
    def conn(self):
        from pymongo import MongoClient
        import datetime
        import pprint

        client = MongoClient('localhost', 27017)
        db = client['flaskapp']

        ''' create a collection '''
        # collection = db.userbase

        ''' route for db/schema/table '''
        posts = db.userbase.posts

        ''' insert data '''
        # post = {"added_date": datetime.datetime.utcnow(), "first_name": "ervin", "last_name": "pora",
        #         "email": ["mongodb", "python", "pymongo"]}
        #
        # post_id = posts.insert_one(post).inserted_id

        pprint.pprint(posts.find_one())

        return 'ok'

# for tweet in oracleConn('SELECT * FROM tweets'):
#     print(tweet)

# print(mysqlConn())

# print(cassandraConn())

# print(mongoConn())

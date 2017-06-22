def oracleConn(sql):
    import cx_Oracle
    import auth

    user = auth.user
    pw = auth.pw
    host = auth.host
    port = auth.port
    sid = auth.sid

    conn = cx_Oracle.connect(user, pw, host + port + sid)

    cursor = conn.cursor()
    cursor.execute(sql)

    return cursor.fetchall()


for tweet in oracleConn('SELECT * FROM tweets'):
    print(tweet)

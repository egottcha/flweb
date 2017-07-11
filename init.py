from flask import Flask, render_template, flash, request, url_for, redirect, session, send_file, send_from_directory, \
    jsonify
from auth import email, general
from flask_mail import Mail, Message
from content_management import Content
from dbconns import mysqlDB
from MySQLdb import escape_string as esc_str
from registration import RegistrationForm
from passlib.hash import sha256_crypt
from werkzeug.datastructures import ImmutableOrderedMultiDict
from functools import wraps
import time
import requests
import pygal
import os
import gc

TOPIC_DICT = Content()

app = Flask(__name__, instance_path=general.protectedFolderPath)

# Get email credentials
mailserver = email.server
mailuser = email.user
mailpw = email.pw

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER=mailserver,
    MAIL_PORT=25,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=mailuser,
    MAIL_PASSWORD=mailpw
)
mail = Mail(app)


# path handling
# @app.route('/<path:urlpath>')
@app.route('/')
def homepage(urlpath='/'):
    return render_template("main.html")


@app.route('/dashboard')
def dashboard():
    # flash(error)
    # flash("fladfasdfsaassh test!!!!")
    return render_template("dashboard.html", TOPIC_DICT=TOPIC_DICT)


@app.route('/signup', methods=['POST'])
def signup_page():
    try:
        form = RegistrationForm(request.form)

        if form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = mysqlDB.conn()

            x = c.execute("SELECT * FROM userbase WHERE name = '%s'" % username)

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('signup.html', form=form)

            else:
                c.execute("INSERT INTO userbase (name, pw, email, role) VALUES ('%s', '%s', '%s', 'reader')" %
                          (username, password, email))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("signup.html", form=form)
    except Exception as e:
        return str(e)


def login_required(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return function(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST'])
def login_page():
    error = ''
    try:
        c, conn = mysqlDB.conn()

        c.execute("SELECT * FROM userbase WHERE name = '%s'" % request.form['username'])

        userpw = c.fetchone()[2]

        if sha256_crypt.verify(request.form['password'], userpw):
            session['logged_in'] = True
            session['username'] = request.form['username']

            flash("You are now logged in")
            return redirect(url_for("dashboard"))

        else:
            error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        # flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)


@app.route('/purchase')
def purchase():
    try:
        return render_template("subscribe.html")
    except Exception as e:
        return str(e)


@app.route('/success')
def success():
    try:
        return render_template("success.html")
    except Exception as e:
        return str(e)

# TODO: work in progress
@app.route('/ipn', methods=['POST'])
def ipn():
    try:
        arg = ''
        request.parameter_storage_class = ImmutableOrderedMultiDict
        values = request.form
        for x, y in values.iteritems():
            arg += "&{x}={y}".format(x=x, y=y)

        validate_url = 'https://www.sandbox.paypal.com' \
                       '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
            .format(arg=arg)
        r = requests.get(validate_url)
        if r.text == 'VERIFIED':
            try:
                payer_email = request.form.get('payer_email')
                unix = int(time.time())
                payment_date = request.form.get('payment_date')
                username = request.form.get('custom')
                last_name = request.form.get('last_name')
                payment_gross = request.form.get('payment_gross')
                payment_fee = request.form.get('payment_fee')
                payment_net = float(payment_gross) - float(payment_fee)
                payment_status = request.form.get('payment_status')
                txn_id = request.form.get('txn_id')
            except Exception as e:
                with open('/tmp/ipnout.txt', 'a') as f:
                    data = 'ERROR WITH IPN DATA\n' + str(values) + '\n'
                    f.write(data)

            with open('/tmp/ipnout.txt', 'a') as f:
                data = 'SUCCESS\n' + str(values) + '\n'
                f.write(data)

            c, conn = mysqlDB.conn()
            c.execute(
                "INSERT INTO ipn (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id))
            conn.commit()
            c.close()
            conn.close()
            gc.collect()

        else:
            with open('/tmp/ipnout.txt', 'a') as f:
                data = 'FAILURE\n' + str(values) + '\n'
                f.write(data)

        return r.text

    except Exception as e:
        return str(e)


@app.errorhandler(404)
def page_not_found(e):
    try:
        gc.collect()
        rule = request.path
        if "feed" in rule or "favicon" in rule or "wp-content" in rule or "wp-login" in rule or "wp-login" in rule or "wp-admin" in rule or "xmlrpc" in rule or "tag" in rule or "wp-include" in rule or "style" in rule or "apple-touch" in rule or "genericons" in rule or "topics" in rule or "category" in rule or "index" in rule or "include" in rule or "trackback" in rule or "download" in rule or "viewtopic" in rule or "browserconfig" in rule:
            pass
        else:
            errorlogging = open("static/log/404log.txt", "a")
            errorlogging.write((str(rule) + '\n'))

        return render_template('404.html'), 404
    except Exception as e:
        return str(e)


@app.route('/email')
def sendmail():
    try:
        msg = Message("Testing - python app mail sending function",
                      sender="",
                      recipients=[""])
        msg.body = 'Hello ' + 'user' + ',\nThis is a test message '
        msg.html = render_template('/mails/testmsg.html')

        mail.send(msg)
        return 'Mail sent!'
    except Exception as e:
        return str(e)


@app.route('/downloads')
def downloads():
    try:
        return render_template('downloads.html')
    except Exception as e:
        return str(e)


def special_requirement(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session['username'] == general.protectedUser:
                return f(*args, **kwargs)
        except:
            flash("You are not allowed to view this file")
            return redirect(url_for('dashboard'))

    return wrap


@app.route('/protected/<path:file>')
@special_requirement
def protected(file):
    try:
        # send_from_directory param = 'as_attachment=True' to force download
        return send_from_directory(os.path.join(app.instance_path, ''), file)
    except Exception as e:
        # flash(e)
        return redirect(url_for('dashboard'))


@app.route('/files/<file>')
def files(file):
    try:
        # send_file param = 'as_attachment=True' to force download
        return send_file('/static/files/pdf/' + file,
                         attachment_filename=file)
    except Exception as e:
        return str(e)


@app.route('/include_example')
def include_example():
    gc.collect()
    replies = {'Jack': 'Cool post',
               'Jane': '+1',
               'Erika': 'Most definitely',
               'Bob': 'wow',
               'Carl': 'amazing!', }
    return render_template("include_example.html", replies=replies)


@app.route('/jinjaman')
def jinjaman():
    try:
        gc.collect()
        data = [15, '15', 'Python is good', 'Python, Java, php, SQL, C++', '<p><strong>Hey there!</strong></p>']
        return render_template("jinjatemplating.html", data=data)
    except Exception as e:
        return str(e)


@app.route('/interactive')
def interactive():
    try:
        gc.collect()
        return render_template("interactive.html")
    except Exception as e:
        return str(e)


@app.route('/background_process')
def background_process():
    try:
        gc.collect()
        text = request.args.get('jqresp', 0, type=str)
        if text.lower() == 'fine':
            return jsonify(result='It will be better')
        else:
            return jsonify(result='Do better')
    except Exception as e:
        return str(e)


@app.route('/pygalgraph')
def pygalgraph():
    try:
        gc.collect()
        graph = pygal.Line()
        graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = ['2011', '2012', '2013', '2014', '2015', '2016']
        graph.add('Python', [15, 31, 89, 200, 356, 900])
        graph.add('Java', [15, 45, 76, 80, 91, 95])
        graph.add('C++', [5, 51, 54, 102, 150, 201])
        graph.add('All others combined!', [5, 15, 21, 55, 92, 105])
        graph_data = graph.render_data_uri()
        return render_template("graphing.html", graph_data=graph_data)
    except Exception as e:
        return str(e)


@app.route('/converters')
# filter to int, can be float, string etc.
# @app.route('/converters/<int:page>')
@app.route('/converters/<path:urlpath>')
def converters(urlpath=1):
    try:
        gc.collect()
        return render_template("converters.html", urlpath=urlpath)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.secret_key = '12345'

    app.run()

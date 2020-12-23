import re
import requests
from email.headerregistry import Address
import smtplib
from email.mime.base import MIMEBase
from email import encoders
from os import environ, mkdir
from shutil import rmtree
from threading import Thread
import json
from flask.helpers import make_response
import redis
# importing unit 4's functions
from sentiport.utils.utilities.crawling import *
from sentiport.pdf_generator import create_pdf
from sentiport.mail import create_email_message, get_user_mail
from sentiport.forms import AppForm
from sentiport import app, thread_lock, threads, store
from flask import render_template, url_for, flash, redirect, request, abort, session, jsonify
from uuid import uuid1


# Error handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route("/", methods=['GET', 'POST'])
def index():
    form = AppForm()
    return render_template('index.html', form=form)


@app.route("/status/<thread_id>", methods=['GET'])
def status(thread_id):
    # Common mistakes: passing byte got from redis into JSON response
    try:
        statuses = store.hmget(
            thread_id,
            "is_running",
            "is_error",
            "error_message",
            "runtime_message"
            )
        is_running, is_error, error_message, runtime_message = [status.decode("utf-8") for status in statuses]
        is_running = int(is_running); is_error = int(is_error)
        return jsonify({
            "status": 200,
            "thread_id": thread_id,
            "task_status": {
                "isRunning": is_running,
                "isError": is_error,
                "errorMessage": error_message,
                "runtimeMessage": runtime_message
            }
        })
    except Exception as e:
        return {
            "status": 500,
            "error": str(e)
        }        


@app.route("/status/delete", methods=['POST'])
def delete_thread_status():
    # Assumption: Most of the time, this method is called naturally by JavaScript,
    # when thread has stopped running. Not called manually by user
    try:
        thread_id = request.json["thread_id"]
        store.delete(thread_id)
        return {"status": 200, "message": "thread status deleted"}
    except Exception as e:
        return {"status": 200, "error_message": str(e)}


@app.route("/scrape", methods=['POST'])
def scrape():
    form = AppForm()
    if form.validate_on_submit():
        # get form data
        APP_URL = form.app_id.data
        COUNTRY = request.form['country_code']
        targetmail = form.email.data
        try:
            url_res = requests.get(APP_URL)
            PLAYSTORE_ID = get_id(APP_URL)
        except:
            abort(404)

        # start thread
        if url_res.status_code == 200:
            thread_id = str(uuid1())
            thread = Thread(
                target=pipeline,
                args=(
                    PLAYSTORE_ID,
                    COUNTRY,
                    targetmail,
                    thread_id
                )
            )
            thread.start()
            
            # store status to redis
            store.hmset(thread_id, {
                "is_running": int(True),
                "is_error": int(False),
                "error_message": "",
                "runtime_message": "Scraping data",
            })

            status_url = url_for("status", thread_id=thread_id)
            response = make_response(render_template(
                'status.html',
                status_url=status_url,
                thread_id=thread_id,
                playstore_id=PLAYSTORE_ID,
                country_code=COUNTRY,
                user_email=targetmail,
                form=form
            ))

            return response

        flash("""Wrong url or the application doesnt exist""", 'danger')
        return redirect(url_for('hello'))

    flash("""Wrong Playstore URL or the app doesnt exist""", 'danger')
    return redirect(url_for('hello'))


def get_id(toParse):
    regex = r'\?id=([a-zA-Z\.]+)'
    app_id = re.findall(regex, toParse)[0]
    return app_id


def pipeline(playstore_id, country, targetmail, thread_id):
    temp_path = f'sentiport/artifacts/{thread_id}'
    mkdir(temp_path)
    try:
        """PREPARING PLOTS AND VALUE"""
        # store status to redis
        store.hmset(thread_id, {
            "is_running": int(True),
            "is_error": int(False),
            "runtime_message": "Scraping data"
        })

        # crawling
        DATAFRAME = get_crawl_google(playstore_id, country)

        store.hmset(thread_id, {
            "is_running": int(True),
            "is_error": int(False),
            "runtime_message": "Creating PDF"
        })

        with thread_lock:
            filename = create_pdf(DATAFRAME, playstore_id, country, thread_id)

        """SEND THE REPORT THROUGH EMAIL"""
        store.hmset(thread_id, {
            "is_running": int(True),
            "is_error": int(False),
            "runtime_message": "Sending email"
        })

        uname_targetmail, domain_targetmail = get_user_mail(targetmail)

        # Get the account used to send report
        email_address = environ.get('ST_EMAIL')
        print("my email: " + email_address)
        email_password = environ.get('ST_PASSWORD')

        # targeted email
        to_address = (
            Address(
                username=uname_targetmail,
                domain=domain_targetmail
            ),
        )

        # body message
        with open("sentiport/templates/mail.html", "r", encoding='utf-8') as f:
            HTML_MESSAGE = f.read()

        msg = create_email_message(
            from_address=email_address,
            to_address=to_address,
            subject=f'{playstore_id} Review Analysis Report',
            plaintext="Plain text version.",
            html=HTML_MESSAGE
        )

        p = MIMEBase('application', 'octet-stream')

        # attaching the report into email
        with open(f"{temp_path}/{filename}", "rb") as attachment:
            p.set_payload(attachment.read())

        encoders.encode_base64(p)

        p.add_header('Content-Disposition',
                     "attachment; filename= %s" % filename)

        msg.attach(p)

        with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(email_address, email_password)
            smtp_server.send_message(msg)

        print('Email sent successfully')

        # store status to redis
        store.hmset(thread_id, {
            "is_running": int(False),
            "is_error": int(False)
        })

    except Exception as e:
        # store status to redis
        store.hmset(thread_id, {
            "is_running": int(False),
            "is_error": int(True),
            "error_message": str(e)
        })

    finally:
        rmtree(temp_path)

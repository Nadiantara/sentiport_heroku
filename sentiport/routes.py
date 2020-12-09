from email.headerregistry import Address
import smtplib
from email.mime.base import MIMEBase
from email import encoders
from os import environ, mkdir
from shutil import rmtree
from threading import Thread
import json
from flask.helpers import make_response
# importing unit 4's functions
from sentiport.utils.utilities.crawling import *
from sentiport.pdf_generator import create_pdf
from sentiport.mail import create_email_message, get_user_mail
from sentiport import app, thread_lock, threads
from flask import render_template, url_for, redirect, request, make_response
from uuid import uuid1


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/status/<thread_id>", methods=['GET'])
def status(thread_id):
    return {
        "status": 200, 
        "thread_id": thread_id, 
        "task_status": {
            "isRunning": threads[thread_id]["is_running"], 
            "isError": threads[thread_id]["is_error"]
            }
        }
    # return json.dumps({"status": 200, "thread_id": 1, "task_status": "baik-baik saja"})


@app.route("/scrape", methods=['GET', 'POST'])
def scrape():
    if request.method == 'POST':
        # get some data
        playstore_id = request.form['playstore_id']
        country = request.form['country_code']
        targetmail = request.form['user_email']

        thread_id = str(uuid1())
        thread = Thread(
            target=pipeline,
            args=(
                playstore_id,
                country,
                targetmail,
                thread_id
            )
        )
        thread.start()
        threads[thread_id] = {
            "thread": thread,
            "is_running": True,
            "is_error": False,
            "error_message": ""
        }

        # return something
        # DEBUG
        status_url = url_for("status", thread_id=thread_id)
        response = make_response(redirect(url_for('index')))
        response.set_cookie("status_url", status_url)

        return response


def pipeline(playstore_id, country, targetmail, thread_id):
    temp_path = f'sentiport/artifacts/{thread_id}'
    try:
        print("Start!")

        """PREPARING PLOTS AND VALUE"""
        # crawling
        DATAFRAME = get_crawl_google(playstore_id, country)

        mkdir(temp_path)

        with thread_lock:
            filename = create_pdf(DATAFRAME, playstore_id, country, thread_id)

        uname_targetmail, domain_targetmail = get_user_mail(targetmail)

        # DEBUG
        # """SEND THE REPORT THROUGH EMAIL"""
        # # Account used to send report
        # email_address = environ.get('ST_EMAIL')
        # print("my email: " + email_address)
        # email_password = environ.get('ST_PASSWORD')

        # # targeted email
        # to_address = (
        #     Address(
        #         username=uname_targetmail,
        #         domain=domain_targetmail
        #     ),
        # )

        # # body message
        # with open("sentiport/templates/mail.html", "r", encoding='utf-8') as f:
        #     HTML_MESSAGE = f.read()

        # msg = create_email_message(
        #     from_address=email_address,
        #     to_address=to_address,
        #     subject=f'{playstore_id} Review Analysis Report',
        #     plaintext="Plain text version.",
        #     html=HTML_MESSAGE
        # )

        # p = MIMEBase('application', 'octet-stream')

        # # attaching the report into email
        # with open(f"{temp_path}/{filename}", "rb") as attachment:
        #     p.set_payload(attachment.read())

        # encoders.encode_base64(p)

        # p.add_header('Content-Disposition',
        #              "attachment; filename= %s" % filename)

        # msg.attach(p)

        # with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
        #     smtp_server.ehlo()
        #     smtp_server.starttls()
        #     smtp_server.login(email_address, email_password)
        #     smtp_server.send_message(msg)

        # print('Email sent successfully')
        threads[thread_id]["is_running"] = False
        threads[thread_id]["is_error"] = False

    except Exception as e:
        threads[thread_id]["is_running"] = False
        threads[thread_id]["is_error"] = True
        threads[thread_id]["error_message"] = str(e)
    
    finally:
        rmtree(temp_path)


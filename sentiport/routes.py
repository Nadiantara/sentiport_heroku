import re
import requests
from email.headerregistry import Address
import smtplib
from email.mime.base import MIMEBase
from email import encoders
from os import environ, mkdir
from shutil import rmtree
from threading import Thread
# importing unit 4's functions
from sentiport.utils.utilities.crawling import *
from sentiport.utils.utilities.helper import *
from sentiport.pdf_generator import create_pdf
from sentiport.mail import create_email_message, get_user_mail
from sentiport.forms import AppForm
from sentiport import app, thread_lock
from flask import render_template, url_for, flash, redirect, request, abort, session
from uuid import uuid1


#Error handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route("/", methods=['GET', 'POST'])
def index():
    form = AppForm()
    return render_template('index.html', form=form)


@app.route("/scrape", methods=['GET', 'POST'])
def scrape():
    form = AppForm()
    if form.validate_on_submit():
        # get some data
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
            Thread(
                target=pipeline,
                args=(
                    PLAYSTORE_ID,
                    COUNTRY,
                    targetmail
                )
            ).start()

            flash("""An message with pdf attachment will be sent to your email in 5 to 10 minutes,
                please contact us if you receive none""", 'success')
            return redirect(url_for('index'))
        flash("""Wrong url or the app doesnt exist""", 'danger')
        return redirect(url_for('index'))
    else:
        flash("""Wrong Playstore URL or the app doesnt exist""", 'danger')
        return redirect(url_for('index'))


def get_id(toParse):
    regex = r'\?id=([a-zA-Z\.]+)'
    app_id = re.findall(regex, toParse)[0]
    return app_id

def pipeline(PLAYSTORE_ID, COUNTRY, targetmail):
    print("Start!")

    """PREPARING PLOTS AND VALUE"""
    # crawling
    DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)

    temp_dir = uuid1()
    temp_path = f'sentiport/artifacts/{temp_dir}'

    mkdir(temp_path)

    with thread_lock:
        filename = create_pdf(DATAFRAME, PLAYSTORE_ID, COUNTRY, temp_dir)

    uname_targetmail, domain_targetmail = get_user_mail(targetmail)

    """SEND THE REPORT THROUGH EMAIL"""
    # Account used to send report
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
        subject=f'{PLAYSTORE_ID} Review Analysis Report',
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
    rmtree(temp_path)


from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from datetime import date
from email.headerregistry import Address
from email.message import EmailMessage
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
from sentiport import app, thread_lock
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort, session
from uuid import uuid1


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/scrape", methods=['GET', 'POST'])
def scrape():
    if request.method == 'POST':
        # get some data
        PLAYSTORE_ID = request.form['playstore_id']
        COUNTRY = request.form['country_code']
        targetmail = request.form['user_email']

        # start thread
        Thread(
            target=pipeline,
            args=(
                PLAYSTORE_ID,
                COUNTRY,
                targetmail
            )
        ).start()

        # return something
        return redirect(url_for('index'))


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
    email_address = environ.get('ST_EMAIL') or 'tb.adam.co.id@gmail.com'
    print("my email: " + email_address)
    email_password = environ.get('ST_PASSWORD') or 'lspwiljpkbgvpzni'

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


def OLDscrape():
    if request.method == 'POST':
        PLAYSTORE_ID = request.form['playstore_id']
        COUNTRY = request.form['country_code']
        targetmail = request.form['user_email']
        session['context'] = {'PLAYSTORE_ID': PLAYSTORE_ID,
                              'COUNTRY': COUNTRY, 'targetmail': targetmail}
        print("Start!")

        """PREPARING PLOTS AND VALUE"""
        start = time.time()
        # crawling
        DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)
        session['fileName'] = create_pdf(DATAFRAME, PLAYSTORE_ID, COUNTRY)

        return redirect(url_for('success'))


def OLDsuccess():
    context = session.get('context', None)
    PLAYSTORE_ID = context["PLAYSTORE_ID"]
    COUNTRY = context["COUNTRY"]
    targetmail = context["targetmail"]
    print("TARGET MAIL : " + targetmail)
    uname_targetmail, domain_targetmail = get_user_mail(targetmail)
    fileName = session.get('fileName', None)

    """PREPARING PLOTS AND VALUE"""
    start = time.time()
    # crawling

    """SEND THE REPORT THROUGH EMAIL"""
    # Account used to send report
    email_address = environ.get('ST_EMAIL')
    print("my email: " + email_address)
    email_password = environ.get('ST_PASSWORD')

    # targeted email
    to_address = (
        Address(username=uname_targetmail, domain=domain_targetmail),
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

    # attaching the report into email
    filename = fileName
    attachment = open(f"sentiport/artifacts/{fileName}", "rb")

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(p)

    with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(email_address, email_password)
        smtp_server.send_message(msg)

    print('Email sent successfully')

    return render_template('success.html', context=context)

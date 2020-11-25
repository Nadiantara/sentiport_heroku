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

# importing unit 4's functions
from sentiport.utils.utilities.crawling import *
from sentiport.utils.utilities.helper import *
from sentiport.pdf_generator import create_pdf
from sentiport.mail import create_email_message
from sentiport import app
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort


@app.route("/", methods=['GET', 'POST'])
def index():
        return render_template('index.html')

        

@app.route("/report", methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        PLAYSTORE_ID = request.form['playstore_id']
        COUNTRY = request.form['country_code']
        targetmail = request.form['user_email']
        context = {'form_1': PLAYSTORE_ID, 'form_2': COUNTRY, 'form_3': targetmail}
        
        # PLAYSTORE_ID = input('Enter Playstore ID: ')


        # COUNTRY = input('Enter COUNTRY ID: ')

        # # targeted email input
        # targetmail = input('Enter recipient email: ')

        # dividing the email into uname and domain (for email function)
        for i in range(len(targetmail)):
            if targetmail[i] == '@':
                uname_targetmail = (targetmail[0:i])
                domain_targetmail = (targetmail[-(len(targetmail)-i-1):])

        print("Start!")

        """PREPARING PLOTS AND VALUE"""

        start = time.time()
        # crawling
        DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)
        fileName = create_pdf(DATAFRAME, PLAYSTORE_ID, COUNTRY)



        """SEND THE REPORT THROUGH EMAIL"""

        # Account used to send report
        email_address = '*****'
        email_password = '******'

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





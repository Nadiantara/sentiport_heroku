def drawMyRuler(pdf):
    pdf.setFont("Courier-Bold", 20)
    pdf.drawString(100, 755, 'x100')
    pdf.drawString(200, 755, 'x200')
    pdf.drawString(300, 755, 'x300')
    pdf.drawString(400, 755, 'x400')
    pdf.drawString(500, 755, 'x500')
    pdf.drawString(600, 755, 'x600')
    pdf.drawString(700, 755, 'x700')
    pdf.drawString(800, 755, 'x800')
    pdf.drawString(900, 755, 'x900')
    pdf.drawString(1000, 755, 'x1000')
    pdf.drawString(1100, 755, 'x1100')
    pdf.drawString(1200, 755, 'x1200')
    pdf.drawString(1300, 755, 'x1300')
    pdf.drawString(50, 755, 'x')
    pdf.drawString(150, 755, 'x')
    pdf.drawString(250, 755, 'x')
    pdf.drawString(350, 755, 'x')
    pdf.drawString(450, 755, 'x')
    pdf.drawString(550, 755, 'x')
    pdf.drawString(650, 755, 'x')
    pdf.drawString(750, 755, 'x')
    pdf.drawString(850, 755, 'x')
    pdf.drawString(950, 755, 'x')
    pdf.drawString(1050, 755, 'x')
    pdf.drawString(1150, 755, 'x')
    pdf.drawString(1250, 755, 'x')
    pdf.drawString(1350, 755, 'x')

    pdf.drawString(5, 100, 'y100')
    pdf.drawString(5, 200, 'y200')
    pdf.drawString(5, 300, 'y300')
    pdf.drawString(5, 400, 'y400')
    pdf.drawString(5, 500, 'y500')
    pdf.drawString(5, 600, 'y600')
    pdf.drawString(5, 700, 'y700')
    pdf.drawString(5, 50, 'y')
    pdf.drawString(5, 150, 'y')
    pdf.drawString(5, 250, 'y')
    pdf.drawString(5, 350, 'y')
    pdf.drawString(5, 450, 'y')
    pdf.drawString(5, 550, 'y')
    pdf.drawString(5, 650, 'y')
    pdf.drawString(5, 750, 'y')


# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request', sender='noreply@wayannadiantara.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
#     {url_for('reset_token', token=token, _external=True)}

#     If you did not make this request then simply ignore this email and no change will be made.
#     '''
#     mail.send(msg)

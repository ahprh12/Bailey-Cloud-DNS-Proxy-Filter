import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_message():
    msg = MIMEMultipart('alternative')
    s = smtplib.SMTP('smtp.sendgrid.net', 587)
    s.login(USERNAME, PASSWORD)

    msg['Subject'] = 'Granville Report'
    msg['From'] = 'mailer@gville.com'
    body = 'This is the message'

    content = MIMEText(body, 'plain')
    msg.attach(content)
    s.sendmail(fromEmail, toEmail, msg.as_string())

# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create the container (outer) email message.
msg = MIMEMultipart()
msg['Subject'] = ''

me = 'mailer@gville.com'
to = 'ahprh12@gmail.com'
msg['From'] = me
msg['To'] = to
msg.preamble = 'Your report from Granville.'

filename = './logs/alert.log'
msg.attach(MIMEText(open(filename).read()))

# Send the email via our own SMTP server.
s = smtplib.SMTP('smtp.gmail.com', '587')
s.sendmail(msg)
s.quit()
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()


def client_accsuccess(uname,upass,uemail,usite):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT"))

    msg_str = "Hello,\n\nGood day! \n\n\tThank you for creating an account with us. For your reference, here are your login details: \n\n\t\tSite: "+ usite +"\n\t\tUsername: " + uname + "\n\t\tPassword: " + upass + "\n\n\tPlease keep this information for your records. If you have any questions or need assistance, feel free to reach out—we’ll be happy to help.\n\n\tWe look forward to doing business with you.\n\nThank you and have a great day!"

    msg = EmailMessage()
    msg["Subject"] = "CCASS - Your Account Login Details"

    to_list = [uemail,"adeguzman@orcacoldchain.com"]
    cc_list = []
    bcc_list = []

    all_recipients = to_list + cc_list + bcc_list
    msg.set_content(msg_str)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        #server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg, from_addr=EMAIL_USER, to_addrs=all_recipients)


def internal_accsuccess(uname,uemail,pnum, usite):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT"))

    msg_str = "Hi Team,\n\nThis is to inform everyone that a new client has successfully registered in the system.\n\n\t\tClient Details\n\t\tSite: " + usite +"\n\t\tUsername:" + uname + "\n\t\tEmail: " + uemail + "\n\t\tPhone Number: " + pnum + "\n\nThis is for your review.\n\nThank you."

    msg = EmailMessage()
    msg["Subject"] = "CCASS New Client Notif - TEST EMAIL PLEASE DISREGARD"

    to_list = ["orcasupport@orcacoldchain.com","orca-crm@orcacoldchain.com"]
    cc_list = []
    bcc_list = []

    all_recipients = to_list + cc_list + bcc_list
    msg.set_content(msg_str)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        #server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg, from_addr=EMAIL_USER, to_addrs=all_recipients)
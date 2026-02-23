import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import *
# ========== EMAIL ==========
#SENDER_EMAIL = "umer.bsse1500@gmail.com"
SENDER_EMAIL = get_config_val('SENDER_EMAIL')


#APP_PASSWORD = "yxhy inwe gvdf ffht"
APP_PASSWORD = get_config_val('APP_PASSWORD')


#RECEIVER_EMAIL = "umarbsse@gmail.com"
RECEIVER_EMAIL = get_config_val('RECEIVER_EMAIL')


#SMTP_SERVER = "smtp.gmail.com"
SMTP_SERVER = get_config_val('SMTP_SERVER')


#SMTP_PORT = 587
SMTP_PORT = int(get_config_val('SMTP_PORT'))
# ===========================

# ---------- EMAIL FUNCTION ----------
def send_email(subject, body, attachment_path=None):
    # 1. Create a Multipart container
    msg = MIMEMultipart()
    msg['Subject'] = f"{subject}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    # 2. Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # 3. Handle the attachment
    if attachment_path:
        try:
            with open(attachment_path, "rb") as attachment:
                # Create a base part for the file
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)
            
            # Add header with the filename
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_path}",
            )
            
            # Add attachment to the message
            msg.attach(part)
        except Exception as e:
            print(f"Could not attach file: {e}")

    # 4. Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent with attachment:", subject)
        #write_log(subject + " | " + body)
    except Exception as e:
        print("Email failed:", e)
        #write_log("Email failed: " + str(e))
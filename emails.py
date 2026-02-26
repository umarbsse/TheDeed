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
def send_email(subject, body, attachment_paths=None):
    # 1. Create a Multipart container
    msg = MIMEMultipart()
    msg['Subject'] = f"{subject}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    # 2. Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # 3. Handle multiple attachments
    if attachment_paths:
        # Ensure attachment_paths is a list even if a single string is passed
        if isinstance(attachment_paths, str):
            attachment_paths = [attachment_paths]

        for path in attachment_paths:
            try:
                if os.path.exists(path):
                    with open(path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    
                    # Use only the filename, not the full path, for the header
                    filename = os.path.basename(path)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    msg.attach(part)
                else:
                    print(f"File not found: {path}")
            except Exception as e:
                print(f"Could not attach file {path}: {e}")

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
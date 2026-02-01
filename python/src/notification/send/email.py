import smtplib, os, json
from email.message import EmailMessage

def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message.get("mp3_fid")
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")
        receiver_address = message.get("username")

        msg = EmailMessage()
        msg.set_content(f"Your mp3 is ready at {mp3_fid}")
        msg["Subject"] = "Your mp3 is ready"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, receiver_address)
        session.quit()
        print("Email sent successfully")
        
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return "Invalid JSON", 400
    
    
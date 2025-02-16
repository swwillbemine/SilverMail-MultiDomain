import os
import json
import random
import subprocess
import mailbox
import ssl
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, session, jsonify, request

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 Menit/1800 Detik

with open('assets/domains.json', 'r') as f:
    DOMAINS = json.load(f)

if not isinstance(DOMAINS, list):
    raise ValueError("File JSON harus list.")

domain_utama = os.getenv("MAIN_DOMAIN")
use_ssl = os.getenv("USE_SSL")

with open('assets/names.json', 'r') as f:
    NAMES = json.load(f)

if not isinstance(NAMES, list):
    raise ValueError("File JSON harus list.")


POSTFIX_VIRTUAL_MAILBOX = os.getenv("POSTFIX_VIRTUAL_MAILBOX")
POSTFIX_VIRTUAL_ALIAS = os.getenv("POSTFIX_VIRTUAL_ALIAS")\


used_combinations = set()

class EmailManager:
    def __init__(self):
        self.current_email = None
        self.mailbox_path = None

    def generate_username(self):
        while True:
            name = random.choice(NAMES)
            number = random.randint(100, 9999)
            combination = f"{name}{number}"
            if combination not in used_combinations:
                used_combinations.add(combination)
                return combination

    def cleanup_previous_email(self):
        if self.current_email:
            try:
                # Hapus email lama di Postfix
                subprocess.run(f"sudo sed -i '/^{self.current_email}/d' {POSTFIX_VIRTUAL_MAILBOX}", 
                             shell=True, check=True)
                subprocess.run(f"sudo sed -i '/^{self.current_email}/d' {POSTFIX_VIRTUAL_ALIAS}", 
                             shell=True, check=True)
                
                # Update data Postfix
                subprocess.run("sudo postmap " + POSTFIX_VIRTUAL_MAILBOX, shell=True, check=True)
                subprocess.run("sudo postmap " + POSTFIX_VIRTUAL_ALIAS, shell=True, check=True)
                subprocess.run("sudo systemctl reload postfix", shell=True, check=True)
                
            except subprocess.CalledProcessError as e:
                app.logger.error(f"Cleanup error: {str(e)}")

    def create_new_email(self):
        username = self.generate_username()
        domain = random.choice(DOMAINS)
        new_email = f"{username}@{domain}"
        alias_email = f"{username}@{domain_utama}"
        self.mailbox_path = f"/var/mail/vhosts/{domain_utama}/{username}"
        
        try:
            os.makedirs(f"{self.mailbox_path}/new", exist_ok=True)
            os.makedirs(f"{self.mailbox_path}/cur", exist_ok=True)
            subprocess.run(f"sudo chown -R vmail:vmail {self.mailbox_path}", 
                         shell=True, check=True)
            subprocess.run(f"sudo chmod -R 700 {self.mailbox_path}", 
                         shell=True, check=True)
            

            # Update konfigurasi Postfix
            with open(POSTFIX_VIRTUAL_MAILBOX, "a") as f:
                f.write(f"{alias_email}    {domain_utama}/{username}/\n")
            with open(POSTFIX_VIRTUAL_ALIAS, "a") as f:
                f.write(f"{new_email}    {alias_email}\n")
            
            # Update Postfix
            subprocess.run(f"sudo postmap {POSTFIX_VIRTUAL_MAILBOX}", shell=True, check=True)
            subprocess.run(f"sudo postmap {POSTFIX_VIRTUAL_ALIAS}", shell=True, check=True)
            subprocess.run("sudo systemctl reload postfix", shell=True, check=True)
            
            return new_email
            
        except Exception as e:
            app.logger.error(f"Generation error: {str(e)}")
            raise

email_manager = EmailManager()

@app.route('/')
def index():
    domain = request.host 
    if domain not in DOMAINS:
        return "Domain not supported", 404
    
    return render_template("index.html", 
                         email=session.get('current_email'),
                         generated_time=session.get('generated_time'),
                         web_title=os.getenv("WEB_TITLE"),
                         web_slogan=os.getenv("WEB_SLOGAN"),
                         refresh_interval=os.getenv("WEB_REFRESH_INTERVAL"))

@app.route('/generate', methods=['POST'])
def generate_email():
    if 'current_email' in session:
        email_manager.current_email = session['current_email']
        email_manager.cleanup_previous_email()
    
    try:
        new_email = email_manager.create_new_email()
        session['current_email'] = new_email
        session['generated_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session['email_counter'] = 0  # Reset counter
        return jsonify({"email": new_email})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/emails')
def get_emails():
    if 'current_email' not in session:
        return jsonify([])
    
    try:
        username = session['current_email'].split('@')[0]
        domain = session['current_email'].split('@')[1]
        mail_path = f"/var/mail/vhosts/{domain_utama}/{username}"
        
        mbox = mailbox.Maildir(mail_path, factory=lambda f: mailbox.MaildirMessage(f))
        emails = []
        counter = session.get('email_counter', 0)
        
        for key in mbox.keys()[counter:]:
            msg = mbox[key]
            body = extract_body(msg)
            
            emails.append({
                'id': key,
                'from': msg['from'],
                'subject': msg['subject'] or "No Subject",
                'date': msg['date'],
                'body': body
            })
            counter += 1
        
        session['email_counter'] = counter
        return jsonify(emails)
    
    except Exception as e:
        app.logger.error(f"Mailbox error: {str(e)}")
        return jsonify([])

def extract_body(msg): 
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode(errors='replace')
                break
    else:
        body = msg.get_payload(decode=True).decode(errors='replace')
    return body

if __name__ == '__main__':
    if use_ssl == "true":
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain('ssl/cert.pem', 'ssl/key.pem')
        app.run(host='0.0.0.0', port=443, ssl_context=context)
    else:
        app.run(host='0.0.0.0', port=80)
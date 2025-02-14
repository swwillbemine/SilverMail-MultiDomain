import os
import random
import subprocess
import shutil
import mailbox
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, jsonify, request

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 jam

# Konfigurasi Domain
DOMAINS = {
    "hyperbug.my.id": {
        "template": "hyperbug.html",
        "mail_dir": "/var/mail/vhosts/hyperbug.my.id"
    },
    "coloros.hyperbug.my.id": {
        "template": "hyperbug.html",
        "mail_dir": "/var/mail/vhosts/hyperbug.my.id"
    },
    "funtouchos.hyperbug.my.id": {
        "template": "hyperbug.html",
        "mail_dir": "/var/mail/vhosts/hyperbug.my.id"
    }
}

domain_utama = "hyperbug.my.id"

# Konfigurasi Postfix
POSTFIX_VIRTUAL_MAILBOX = "/etc/postfix/virtual_mailbox"
POSTFIX_VIRTUAL_ALIAS = "/etc/postfix/virtual_alias"

# Daftar Nama
NAMES = [
    "naruto", "sasuke", "sakura", "kakashi", "hinata", "itachi", "gaara", "lee", "neji",
    "goku", "vegeta", "bulma", "piccolo", "frieza", "cell", "trunks", "gohan", "krillin", "yamcha",
    "luffy", "zoro", "nami", "usopp", "sanji", "chopper", "robin", "franky", "brook", "jinbe",
    "eren", "mikasa", "levi", "armin", "hange", "erwin", "reiner", "bertholdt", "annie", "ymir",
    "kirito", "asuna", "klein", "agil", "sinon", "leafa", "yui", "eugeo", "alice", "admina",
    "cloud", "tifa", "aerith", "barret", "sephiroth", "zack", "cid", "yuffie", "vincent", "redxiii",
    "linkko", "zelda", "ganon", "mario", "luigi", "peachella", "bowser", "yaoshi", "toad", "daisy",
    "sanchou", "ash", "misty", "brock", "gary", "jessie", "james", "meowth", "lucario", "eevee",
    "dante", "vergil", "nero", "trish", "sparda", "vii", "bayonetta", "jeanne", "pardi", "sumito",
    "alucard", "trevor", "sylphia", "grant", "richter", "maria", "shanoa", "soma", "julius", "yoko",
    "ryuuji", "ken", "chunliv", "guilevin", "camelya", "nakuma", "sagato", "avega", "kane", "sakura",
    "subaru", "yae", "raiden", "liukang", "kitana", "mileena", "jax", "sonya", "kunglao", "baraka",
    "harry", "hermione", "ron", "dumbledore", "snape", "voldemort", "luna", "neville", "sirius", "bellatrix",
    "frodo", "gandalf", "aragorn", "legolas", "gimli", "boromir", "sam", "merry", "pippin", "sauron",
    "jon", "sansa", "arya", "bran", "tyrion", "daenerys", "cersei", "jaime", "theon", "brienne", "robin", "misbah",
    "hartono", "supriyadi", "sukarton", "sumanto", "sulastri", "sukris", "rusdi", "amba", "narji", "sudarsono",
    "suhendro", "sumiyati", "jarwo", "sutik", "suharto", "anfal", "niki", "abil", "rafi", "aqil", "suli", "asep", "conis",
    "reinhard", "sinaga", "yotsuba", "nagomi", "ririsa", "amano", "kaori", "gojo", "venti", "jean", "mona", "lisa",
    "kamaru", "norman", "yakovlev", "pavel", "mikail", "alisa", "mikhailovna", "kujou", "yuki", "suou",
    "masha", "kuze", "alya", "furina", "neuvillete", "nopal", "navia", "herta", "nahida", "nadia", "solikin", "yanto",
    "nur", "nurjannah", "jannah", "fatihuddin", "munawwir", "somad", "somat", "nurhadi", "hadi", "elsyafa",
    "andre", "maulaana", "ade", "saputra", "safitri", "misbahulharun", "harun", "izza", "azizatul", "zahra"
    ,"anisya", "aesyah", "krisna", "carly", "reza", "mahendra", "anis", "suprapto", "chizuru", "sora","ainz",
    "pico","isla","souma","hanto","rudeus", "suryo", "adrian", "handoyo", "salim", "kabul"
]


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
        domain = random.choice(list(DOMAINS.keys()))
        new_email = f"{username}@{domain}"
        alias_email = f"{username}@{domain_utama}"
        self.mailbox_path = f"{DOMAINS[domain]['mail_dir']}/{username}"
        
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
    
    return render_template(DOMAINS[domain]["template"], 
                         email=session.get('current_email'),
                         generated_time=session.get('generated_time'))

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
        mail_path = f"{DOMAINS[domain]['mail_dir']}/{username}"
        
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
    app.run(host='0.0.0.0', port=80)
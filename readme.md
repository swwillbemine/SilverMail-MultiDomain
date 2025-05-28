# SilverMail-MultiDomain
### *"Leave it to me, I'll hack through any system!"* - Silver Wolf

<div align="center">

![SilverMail Logo](https://cdn.eula.my.id/silvermail_logo_fix.png)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04+-orange.svg)](https://ubuntu.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/swwillbemine/SilverMail-MultiDomain?style=social)](https://github.com/swwillbemine/SilverMail-MultiDomain)

*A temporary email service inspired by ~~My Wife~~ the legendary hacker Silver Wolf*

</div>

---

## 🎯 About SilverMail

Just like Silver Wolf infiltrates the most secure systems, SilverMail penetrates the complexity of temporary email services with elegance and efficiency. This Python-based application runs seamlessly on Ubuntu servers, providing disposable email addresses for privacy-conscious users.

> *"Every system has its vulnerabilities. SilverMail is your digital anonymity shield."*

### ✨ Features

- 🔒 **Anonymous Email Generation** - Create temporary emails instantly
- 🌐 **Multi-Domain Support** - Handle multiple domains like a pro hacker
- ⚡ **Real-time Email Reception** - Instant message delivery
- 🎨 **Clean Web Interface** - Cyberpunk-inspired UI
- 🛡️ **Privacy First** - No registration required
- 🔄 **Auto-cleanup** - Emails auto-delete for privacy

---

## 🖥️ System Requirements

| Component | Minimum Specs |
|-----------|---------------|
| **OS** | Ubuntu 22.04+ |
| **RAM** | 1GB+ |
| **Storage** | 8GB+ |
| **Network** | Public IP & Domain |
| **SSL** | Optional (Recommended) |

---

## 🚀 Live Demo

Experience the power of Silver Wolf's creation:
🌟 **[SilverMail Demo](http://silvermail.eula.my.id/)**

---

## 📦 Installation Guide

### Step 1: Clone the Repository
```bash
# Download SilverMail Codes
git clone https://github.com/swwillbemine/SilverMail-MultiDomain.git
cd SilverMail-MultiDomain
```

### Step 2: Install Postfix Mail Server
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Postfix
sudo apt install postfix -y
```

### Step 3: Configure Postfix
Edit the main configuration file:
```bash
sudo nano /etc/postfix/main.cf
```

Replace with this configuration (adjust domain to match yours):
```ini
# SilverMail Postfix Configuration
smtpd_banner = $myhostname ESMTP $mail_name (SilverWolf-Powered)
biff = no
append_dot_mydomain = no

# Aliases
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases

# Domain Configuration
myhostname = silvermail.my.id // changes this with your domain //
mydestination = localhost.localdomain, localhost
relayhost =

# Network Settings
inet_interfaces = all
inet_protocols = ipv4

# Virtual Mail Configuration
home_mailbox = Maildir/
mailbox_command =
virtual_mailbox_base = /var/mail/vhosts
virtual_mailbox_maps = hash:/etc/postfix/virtual_mailbox
virtual_alias_maps = hash:/etc/postfix/virtual_alias
virtual_mailbox_domains = silvermail.my.id // changes this with your domain //
virtual_alias_domains = 
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000

# Security
mynetworks = 127.0.0.0/8
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination

# Misc
recipient_delimiter = +
compatibility_level = 2
```

### Step 4: Create Mailbox Directory Structure
```bash
# Create virtual mail directories
sudo mkdir -p /var/mail/vhosts/silvermail.my.id

# Create vmail user and group
sudo groupadd -g 5000 vmail
sudo useradd -g vmail -u 5000 vmail -d /var/mail/vhosts -s /bin/false

# Set proper permissions
sudo chown -R vmail:vmail /var/mail/vhosts
sudo chmod -R 770 /var/mail/vhosts
```

### Step 5: Configure Virtual Mailboxes
```bash
# Create virtual mailbox file
sudo nano /etc/postfix/virtual_mailbox
```

Add your first mailbox:
```
silverwolf@silvermail.my.id    silvermail.my.id/silverwolf/
```

Apply changes:
```bash
sudo postmap /etc/postfix/virtual_mailbox
```

### Step 6: Configure Virtual Aliases
```bash
# Create virtual alias file
sudo nano /etc/postfix/virtual_alias
```

Add alias mapping:
```
silverwolf@silvermail.my.id    silverwolf@silvermail.my.id
```

Apply changes:
```bash
sudo postmap /etc/postfix/virtual_alias
```

### Step 7: Set File Permissions
```bash
sudo chmod 644 /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
sudo chown root:root /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
```

### Step 8: Restart Postfix Service
```bash
sudo systemctl restart postfix
sudo systemctl enable postfix
```

### Step 9: Deploy Web Interface
1. **Configure Environment**: Edit `.env` file with your settings
2. **Set Domains**: Edit `assets/domains.json` (first domain = primary domain)
3. **Install Dependencies**:
```bash
sudo apt install python3-pip -y
pip3 install -r requirements.txt
```

4. **Launch Server**:
```bash
gunicorn app:app -b 0.0.0.0:80 -w 4 --preload
```

---

## 🔄 Auto-Start Configuration

### Create System Service
```bash
sudo nano /etc/systemd/system/silvermail.service
```

Service configuration:
```ini
[Unit]
Description=SilverMail Gunicorn Service - Powered by Silver Wolf
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/SilverMail
ExecStart=/usr/local/bin/gunicorn app:app -b 0.0.0.0:80 -w 4 --preload
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable silvermail
sudo systemctl start silvermail

# Check status
sudo systemctl status silvermail
```

---

## 🧹 Maintenance Commands

### Clean Email Cache
Sometimes you need to wipe the digital traces, just like Silver Wolf:

```bash
# 1. Stop Postfix
sudo systemctl stop postfix

# 2. Remove all user directories
sudo rm -rf /var/mail/vhosts/silvermail.my.id/*

# 3. Reset virtual mailbox
sudo rm /etc/postfix/virtual_mailbox
sudo nano /etc/postfix/virtual_mailbox
# Add: silverwolf@silvermail.my.id    silvermail.my.id/silverwolf/
sudo postmap /etc/postfix/virtual_mailbox

# 4. Reset virtual alias
sudo rm /etc/postfix/virtual_alias
sudo nano /etc/postfix/virtual_alias  
# Add: silverwolf@silvermail.my.id    silverwolf@silvermail.my.id
sudo postmap /etc/postfix/virtual_alias

# 5. Restart Postfix
sudo systemctl start postfix
```

---

## 🎮 Silver Wolf Easter Eggs

- **Domain Theme**: All default configurations use `silvermail.my.id`
- **Default User**: `silverwolf@silvermail.my.id` 
- **Hacker Aesthetic**: Cyberpunk-inspired interface
- **Privacy Focus**: Just like Silver Wolf's stealth operations

---

## 🤝 Contributing

Want to help improve Silver Wolf's creation? 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-hack`)
3. Commit your changes (`git commit -m 'Add some amazing hack'`)
4. Push to the branch (`git push origin feature/amazing-hack`)
5. Open a Pull Request

---

## 📞 Support

Having trouble? Even Silver Wolf had to debug her code sometimes:

- 📋 **Issues**: [GitHub Issues](https://github.com/swwillbemine/SilverMail-MultiDomain/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/swwillbemine/SilverMail-MultiDomain/discussions)
- 📧 **Email**: Contact via our demo site

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Created with 💖 for Silver Wolf

*"In the world of 1s and 0s, privacy is the ultimate currency."*

**⭐ Star this repository, or Silver Wolf will hack your system!**

[![GitHub Stars](https://img.shields.io/github/stars/swwillbemine/SilverMail-MultiDomain?style=for-the-badge&logo=github)](https://github.com/swwillbemine/SilverMail-MultiDomain)

---

**🔗 Useless Links**
[Website](http://silvermail.eula.my.id/) • [Documentation](https://github.com/swwillbemine/SilverMail-MultiDomain/wiki) • [Releases](https://github.com/swwillbemine/SilverMail-MultiDomain/releases)

</div>
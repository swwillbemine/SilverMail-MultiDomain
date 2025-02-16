# SilverMail-MultiDomain
![Logo](https://cdn.eula.my.id/silvermail_logo_fix.png)

Aplikasi layanan email sementara berbasis Python dan berjalan di Ubuntu, server ini memerlukan IP Publik dan domain, SSL opsional. 

## Minimum System Requirement

Ubuntu 22.04 or newer\
1GB RAM or upper\
8GB Storage or upper

## Demo
[HyperBug](http://hyperbug.my.id/)

## Installation
### 1. Clone Repository
```
git clone https://github.com/aha-ng/SilverMail-MultiDomain.git
```

### 2. Install Postfix
```bash
sudo apt update
sudo apt upgrade -y

sudo apt install postfix -y
```

### 3. Konfigurasi
Edit file utama konfigurasi Postfix:
```bash
sudo nano /etc/postfix/main.cf
```
Isi seperti ini, domain menyesuaikan (silvermail.my.id)
```
smtpd_banner = $myhostname ESMTP $mail_name (Debian/GNU)
biff = no
append_dot_mydomain = no

alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
myhostname = silvermail.my.id
mydestination = localhost.localdomain, localhost
relayhost =
inet_interfaces = all
inet_protocols = ipv4
home_mailbox = Maildir/
mailbox_command =
virtual_mailbox_base = /var/mail/vhosts
virtual_mailbox_maps = hash:/etc/postfix/virtual_mailbox
virtual_alias_maps = hash:/etc/postfix/virtual_alias
virtual_mailbox_domains = silvermail.my.id
virtual_alias_domains = onyamail.my.id
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000

mynetworks = 127.0.0.0/8

smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination

recipient_delimiter = +

compatibility_level = 2
```
### 4. Buat directory untuk Mailbox
```
sudo mkdir -p /var/mail/vhosts/silvermail.my.id
sudo groupadd -g 5000 vmail
sudo useradd -g vmail -u 5000 vmail -d /var/mail/vhosts -s /bin/false
sudo chown -R vmail:vmail /var/mail/vhosts
sudo chmod -R 770 /var/mail/vhosts
```
### 5. Menambah Virtual Mailbox
Buka file ini
```
sudo nano /etc/postfix/virtual_mailbox
```
Tambahkan 1 email kemudian simpan
```
silverwolf@silvermail.my.id    silvermail.my.id/silverwolf/
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_mailbox
```
### 6. Menambah Virtual Alias
Buka file ini
```
sudo nano /etc/postfix/virtual_alias
```
Tambahkan 1 email kemudian simpan
```
silverwolf@silvermail.my.id    silverwolf@silvermail.my.id
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_alias
```
### 7. Tambah izin file jika diperlukan
```
sudo chmod 644 /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
sudo chown root:root /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
```
### 8. Restart Postfix
```
sudo systemctl restart postfix
sudo systemctl enable postfix
```
### 9. Instalasi WEB Interface
1. Edit file .env sesuai konfigurasi anda
2. edit file `assets/domains.json` sesuai domain anda (domain pertama adalah domain utama)
3. jalankan command
```python
sudo apt install python3-pip -y
pip3 install -r requirements.txt
```
4. Kemudian command untuk menjalankan web server
```
gunicorn app:app -b 0.0.0.0:80 -w 4 --preload
```

## Autorun on start
### 1. Buat File Service (ganti port 80 menjadi 443 jika menggunakan https/ssl)
```
nano /etc/systemd/system/silvermail.service
```
Isi file service
```
[Unit]
Description=SilverMail Gunicorn Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/SilverMail
ExecStart=/usr/local/bin/gunicorn app:app -b 0.0.0.0:80 -w 4 --preload
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Reload
```
systemctl daemon-reload
systemctl enable silvermail
systemctl start silvermail
```

### 3. Cek Status
```
systemctl status silvermail
```

## Delete Email Cache
### 1. Stop Postfix
```
systemctl stop postfix
```
### 2. Hapus semua direktory user

```
sudo rm -rf /var/mail/vhosts/silvermail.my.id/*
```
### 3. Hapus semua Virtual Mailbox dan buat ulang
Hapus file
```
sudo rm /etc/postfix/virtual_mailbox
```
Buat ulang file virtual_mailbox
```
sudo nano /etc/postfix/virtual_mailbox
```
Tambahkan 1 email kemudian simpan
```
silverwolf@silvermail.my.id    silvermail.my.id/silverwolf/
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_mailbox
```

### 4. Hapus semua Virtual Alias dan buat ulang
Hapus file
```
sudo rm /etc/postfix/virtual_alias
```
BUat ulang file virtual_alias
```
sudo nano /etc/postfix/virtual_alias
```
Tambahkan 1 email kemudian simpan
```
silverwolf@silvermail.my.id    silverwolf@silvermail.my.id
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_alias
```
# SilverMail-MultiDomain

Aplikasi layanan email sementara berbasis Python dan berjalan di Ubuntu, server ini memerlukan IP Publik dan domain, ssl tidak diperlukan. 

## Minimum System Requirement

Ubuntu 22.04 or newer\
*AMD EPYC 9754 or Intel Xeon 6900\
*1024GB RAM or upper\
*Nvidia N100 or upper\
*10TB SSD



## Installation

### 1. Install Postfix
```bash
sudo apt update
sudo apt upgrade -y

sudo apt install postfix -y
```

### 2. Konfigurasi
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
myhostname = hyperbug.my.id
mydestination = localhost.localdomain, localhost
relayhost =
inet_interfaces = all
inet_protocols = ipv4
home_mailbox = Maildir/
mailbox_command =
virtual_mailbox_base = /var/mail/vhosts
virtual_mailbox_maps = hash:/etc/postfix/virtual_mailbox
virtual_alias_maps = hash:/etc/postfix/virtual_alias
virtual_mailbox_domains = hyperbug.my.id
virtual_alias_domains = coloros.hyperbug.my.id funtouchos.hyperbug.my.id
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000

mynetworks = 127.0.0.0/8, 192.168.50.0/24

recipient_delimiter = +

compatibility_level = 2
```
### 3. Buat directory untuk Mailbox
```
sudo mkdir -p /var/mail/vhosts/hyperbug.my.id
sudo groupadd -g 5000 vmail
sudo useradd -g vmail -u 5000 vmail -d /var/mail/vhosts -s /bin/false
sudo chown -R vmail:vmail /var/mail/vhosts
sudo chmod -R 770 /var/mail/vhosts
```
### 4. Menambah Virtual Mailbox
Buka file ini
```
sudo nano /etc/postfix/virtual_mailbox
```
Tambahkan 1 email kemudian simpan
```
silverwolf@hyperbug.my.id    hyperbug.my.id/silverwolf/
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_mailbox
```
### 5. Menambah Virtual Alias
Buka file ini
```
sudo nano /etc/postfix/virtual_alias
```
Tambahkan 1 email kemudia simpan
```
silverwolf@hyperbug.my.id    silverwolf@hyperbug.my.id
```
Jalankan command berikut
```
sudo postmap /etc/postfix/virtual_alias
```
### 6. Tambah izin file jika diperlukan
```
sudo chmod 644 /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
sudo chown root:root /etc/postfix/virtual_alias /etc/postfix/virtual_alias.db
```
### 7. Restart Postfix
```
sudo systemctl restart postfix
sudo systemctl enable postfix
```
### 8. Instalasi WEB Interface
1. Edit domain di file app.py sesuai domain anda
2. jalankan command
```python
sudo apt install python3-pip -y
pip3 install -r requirements.txt
```
3. Kemudian command untuk menjalankan web server
```
gunicorn app:app -b 0.0.0.0:80 -w 4 --preload
```

## Autorun on start
### 1. Buat File Service
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


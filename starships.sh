#!/bin/bash
apt update && apt upgrade -y && apt install -y python3-dev iptables-persistent build-essential python3-pip nginx jq
pip3 install -U setuptools requests wheel
pip3 install flask flask-restful Gunicorn 
mkdir -p /var/www/html/starships
cp app3.py wsgi3.py /var/www/html/starships/.
cat > /etc/systemd/system/starships.service <<'_EOF'
[Unit]
Description=Starships Gunicorn daemon
After=network.target

[Service]
User=root
Group=root
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/html/starships/
ExecStart=/usr/local/bin/gunicorn -w 4 --pid /var/run/gpid --bind unix:/var/run/gunicorn.socket wsgi3:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
_EOF
systemctl start starships && systemctl enable starships && systemctl daemon-reload
rm -f /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
cat > /etc/nginx/sites-available/starships <<'_EOF'
upstream starships {
    server unix:/var/run/gunicorn.socket fail_timeout=0;
}
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    # imaginary server name
    server_name starships.com www.starships.com;
    client_max_body_size 4G;

    keepalive_timeout 5;

    location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
            proxy_buffering off;
            proxy_pass http://starships/;
    }


}
_EOF
cat > /etc/iptables/rules.v4 <<'_EOF'
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
COMMIT
_EOF
ln -s /etc/nginx/sites-available/starships /etc/nginx/sites-enabled/starships
systemctl restart nginx
iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
curl -s 127.0.0.1 | jq '.'

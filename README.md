# Flask-RestAPI-Starship
<h1>Deployment Method1</h1>
<h3>*Note: I made a simple bash script which simply setting up this app and will run that so you can skip from deploying method2:</h3>
    <p>*** It tested only in ubuntu 18.04 ***</p>
 <pre>
 git clone https://github.com/H4mid2019/Flask-RestAPI-Starship.git
 cd Flask-RestAPI-Starship/
 chmod +x starships.sh
 sudo ./starships.sh
 </pre>
 <br/>
<h1>Deployment Method2</h2>
<p>First of all, I started with installation prerequisites and Ubuntu 18.04 running on my server(Amazon EC2). So I installed the following programs. nginx, pip, python3,6>= , flask, flask-restful, requests by the following commands in the terminal:</p>
<p>*Note: I logged in as a root user.</p>
<pre>
apt update && apt upgrade -y && apt install -y python3-dev build-essential python3-pip  nginx
</pre>
<p>update the necessary packages for installing and retrieving data</p>
<pre>
pip3 install -U setuptools requests wheel
</pre>
<p>installing flask, flask-restful(for RESTful-API), and gunicorn(for web-server)</p>
<pre>
pip3 install flask flask-restful Gunicorn
</pre>

<p>I'v made a folder under “/var/www/html” named “starships” and put the codes there.
There are 2 methods of REST-API with flask. I coded in 3 different ways using them.You can find the first in "app" the second in "app2" and the third in "app3".</p>

<p>The most difference between app3 and two others is that the app3 is much faster in answering the client. Because it keeps itself updated from API every 15 seconds, but the others don't. They receive data from the server at runtime just after the user request and then will deliver to the client.</p>

<p>I prefer the "app3" so I configure Nginx and Gunicorn (wsgi3) for app3 by the way the first app is perfectly fine.</p>

<p>So I wanna run Gunicorn like this :</p>
<pre>
gunicorn -w 4 --pid /var/run/gpid --bind unix:/var/run/gunicorn.socket wsgi3:app
</pre>
where "w" stands for workers so we get higher speed(based on Gunicorn documentation for each core of processor 4 workers is fine)
I wanna Gunicorn to be bind as a Unix socket so I think it's faster and at least one of the port of servers will be still empty.
so I added a file which its name is "starships.service" to "/etc/systemd/system" and configured that like below to introduce our Gunicorn as service achieving a stable running Gunicorn service even after restarting the server. and I configured that to run after network configured
<pre>
[Unit]
Description=Starships Gunicorn daemon
After=network.target

[Service]
User=root
Group=root
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/html/starships/
ExecStart=/usr/local/bin/gunicorn -w 4 --pid /var/run/gpid --bind unix:/var/run/gunicorn.socket wsgi2:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
</pre>

So now I check the service correctly works and then I will enable that for to be sure It will be run in next system restart
<pre>
systemctl start starships   # for starting the service 
systemctl status starships  # for checking the service which is correct
systemctl enable starships  # to be sure the service will be run in next restarts

systemctl daemon-reload  # totally reloads daemon 
</pre>
Then I add a new file to “/etc/nginx/sites-available/” with "startships" name which contains below configuration:
<pre>
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
</pre>
Then I run the flow command to make a link of these file in the "/etc/nginx/site-enabled" folder 
<pre>
ln -s /etc/nginx/sites-available/starships /etc/nginx/sites-enabled/starships
</pre>

also, I delete the default configure of nginx with this command
<pre>
rm /etc/nginx/sites-available/default 
rm etc/nginx/sites-enabled/default # for being sure 
</pre>

then I check my nginx configuration with this command:
<pre>
nginx -t
</pre>
so I will restart the nginx service
<pre>
systemctl restart nginx
</pre>
also, I should open port 80 in firewall
<pre>
iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
</pre>
and also in security groups in AWS settings.
then our starships servers work properly and nice. 

Test the Server :
   For checking our server we can use normal browsers because normal requests are GET but it returns string we can use plugins like postman for Chrome or curl and jq in Ubuntu Terminal or  requests and json in Python two examples :
<pre>
# command line example :
# first we have to install jq 

apt install jq 
</pre>
<p>For retrieving data from server:</p>
<pre>
# first run this command for being sure that servers retrieve json output :

curl -v 127.0.0.1 

* Rebuilt URL to: 127.0.0.1/
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 80 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1
> User-Agent: curl/7.58.0
> Accept: */*
< HTTP/1.1 200 OK
< Server: nginx/1.14.0 (Ubuntu)
< Date: Tue, 24 Dec 2019 01:55:30 GMT
< Content-Type: application/json
< Content-Length: 3299
< Connection: keep-alive
</pre>
The third line from the bottom shows that the output is JSON. 
Then for getting beauty json:
<pre>
curl -s 127.0.0.1 |  jq ‘.’ 
</pre>
In Python:
<pre>
import requests
import json

res = requests.get('http://127.0.0.1/')
print(json.dumps(json.loads(res.text), indent=3))
</pre>

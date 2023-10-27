# material_server

## Install dependencies

        pip install -r requirements.txt

## Launch

        python runserver
        python runserver_waitress

## SSL

[Install openssl tutorial](https://www.osradar.com/install-openssl-windows/)

1. Install the pyOpenSSl package

``` cmd
        pip install pyopenssl
```

2. Create a self-signed SSL certificate and key by running 

``` cmd
   openssl req -x509 -newkey rsa:4096 
    -nodes -out cert.pem -keyout key.pem -days 365
```

This will create two files, _cert.pem_ and _key.pem_

3. Sample Flask app

``` python
from flask import Flask
from OpenSSL import SSL

app = Flask(__name__)

context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(ssl_context=context)
```
This code creates an SSL context using the _cert.pem_ and _key.pem_ files and then passes it to the _app.run()_ method    
 

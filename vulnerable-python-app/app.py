from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
    return response

# Apply proxy fix if behind a reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Secure Flask App</title>
            <style>
                .mixed-color {
                    color: blue;
                    background-color: white;
                    font-size: 24px;
                }
            </style>
        </head>
        <body>
            <p class="mixed-color">Hello, I'm Kavita. I'm developing & testing a secure app with Trivy.</p>
        </body>
    </html>
    '''

if __name__ == "__main__":
    # Never run with debug=True in production!
    app.run(host="0.0.0.0", port=7002)
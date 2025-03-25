from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <style>
                .mixed-color {
                    color: blue;
                    background-color: white;
                    font-size: 24px;
                }
            </style>
        </head>
        <body>
            <p class="mixed-color">Hello, I'm Kavita. I'm developing & testing a secure app.</p>
        </body>
    </html>
    '''

if __name__ == "__main__":
    # Turn off debug in production environment
    app.run(host="0.0.0.0", port=7002, debug=os.environ.get('FLASK_ENV') == 'development')

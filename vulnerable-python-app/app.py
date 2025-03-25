from flask import Flask, request

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
            <p class="mixed-color">Hello, I'm Kavita. I'm developing & testing a vulnerable app through Trivy.</p>
        </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7002, debug=True)

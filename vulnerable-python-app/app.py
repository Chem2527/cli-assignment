from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, I'm Kavita. This is a secure Flask app."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7002)  # debug=False by default
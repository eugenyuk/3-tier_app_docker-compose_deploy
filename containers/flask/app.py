from flask import Flask

app = Flask(__name__)

# Process requests to '/' URI
@app.route('/')
def hello():
    return 'Hello from Flask!\n'

if __name__ == '__main__':
    app.run()

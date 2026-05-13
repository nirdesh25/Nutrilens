from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello! Flask is working!</h1><p>If you see this, the server is running correctly.</p>"

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Simple Test Server")
    print("📍 URL: http://localhost:5001")
    print("📍 Alternative: http://127.0.0.1:5001")
    print("=" * 50)
    app.run(host='localhost', port=5001, debug=True)
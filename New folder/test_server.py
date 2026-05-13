#!/usr/bin/env python3
"""
Simple test server to verify Flask is working
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎉 Flask Server is Working!</h1>
    <p>Your Smart Inventory Management System should work now.</p>
    <p><a href="/test">Test Page</a></p>
    '''

@app.route('/test')
def test():
    return '''
    <h2>✅ Test Successful!</h2>
    <p>Flask is running correctly on your system.</p>
    <p><a href="/">Back to Home</a></p>
    '''

if __name__ == '__main__':
    print("Starting test server...")
    print("Open your browser to: http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)
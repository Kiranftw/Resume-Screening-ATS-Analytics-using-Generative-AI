from flask import Flask, render_template, request, redirect, url_for
from DataProcessing import DocumentProcessing
import os

app = Flask(__name__)
FOLDER = "./uploads"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)
app.config['UPLOAD_FOLDER'] = FOLDER


@app.route('/')
def Dashboard():
    return render_template('Dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
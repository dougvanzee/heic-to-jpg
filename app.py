from flask import Flask, request, send_file, render_template, redirect, url_for, session
from functools import wraps
import os
from PIL import Image
import pillow_heif
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.permanent_session_lifetime = 60 * 60 * 24 * 30  # 30 days

USERNAME = os.environ.get("APP_USERNAME", "admin")
PASSWORD = os.environ.get("APP_PASSWORD", "password123")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if not file or not file.filename.lower().endswith('.heic'):
        return "Only HEIC files are supported", 400

    heic_data = pillow_heif.read_heif(file.read())
    image = Image.frombytes(heic_data.mode, heic_data.size, heic_data.data, "raw")

    output = BytesIO()
    image.save(output, format='JPEG')
    output.seek(0)

    return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='converted.jpg')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # use Render's assigned port or default 5000
    app.run(host="0.0.0.0", port=port)

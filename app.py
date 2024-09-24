from flask import Flask, request, render_template, send_from_directory, url_for
import os, random, string, json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
LINKS_FILE = 'links.json'
USER_UPLOADS_FILE = 'user_uploads.json'

link_to_filename = {}
user_uploads = {}

def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_links():
    with open(LINKS_FILE, 'w') as f:
        json.dump(link_to_filename, f)

def load_user_uploads():
    if os.path.exists(USER_UPLOADS_FILE):
        with open(USER_UPLOADS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_uploads():
    with open(USER_UPLOADS_FILE, 'w') as f:
        json.dump(user_uploads, f)

def generate_link():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename
        link = generate_link()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        link_to_filename[link] = filename
        save_links()

        user_ip = request.remote_addr
        if user_ip not in user_uploads:
            user_uploads[user_ip] = []
        user_uploads[user_ip].append({'filename': filename, 'link': link})
        save_user_uploads()

        file_url = url_for('serve_file', link=link, _external=True)
        return render_template('index.html', file_url=file_url)

@app.route('/my_uploads')
def my_uploads():
    user_ip = request.remote_addr
    uploads = user_uploads.get(user_ip, [])
    return render_template('my_uploads.html', uploads=uploads)

@app.route('/file/<link>')
def serve_file(link):
    if link in link_to_filename:
        filename = link_to_filename[link]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            if filename.endswith(('mp4', 'webm', 'ogg')):
                return render_template('video_player.html', video_url=url_for('uploaded_file', filename=filename), filename=filename)
            elif filename.endswith(('png', 'jpg', 'jpeg', 'gif')):
                return render_template('image_preview.html', image_url=url_for('uploaded_file', filename=filename), filename=filename)
            else:
                return render_template('file_preview.html', filename=filename, file_url=url_for('uploaded_file', filename=filename))
        else:
            return "File not found", 404
    else:
        return "Invalid link", 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True) 
    link_to_filename = load_links()
    user_uploads = load_user_uploads()
    app.run(host='0.0.0.0', port=5000, debug=True)

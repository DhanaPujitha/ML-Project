import subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GENERATED_FOLDER'] = 'static/generated'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['GENERATED_FOLDER']):
    os.makedirs(app.config['GENERATED_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    handwriting_image = request.files['handwritingImage']
    text_file = request.files['textFile']
    
    if handwriting_image and text_file:
        # Save uploaded files
        handwriting_image_filename = secure_filename(handwriting_image.filename)
        text_file_filename = secure_filename(text_file.filename)
        
        handwriting_image_path = os.path.join(app.config['UPLOAD_FOLDER'], handwriting_image_filename)
        text_file_path = os.path.join(app.config['UPLOAD_FOLDER'], text_file_filename)
        
        handwriting_image.save(handwriting_image_path)
        text_file.save(text_file_path)
        
        # Call adjust.py script in a separate process
        adjust_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'adjusted_image.png')
        adjust_process = subprocess.Popen(['python', 'adjust.py', handwriting_image_path, adjust_output_path])
        adjust_process.wait()
        # Call hw.py script in a separate process
        generated_image_path = os.path.join(app.config['GENERATED_FOLDER'], 'generated_handwritten_text.png')
        hw_process = subprocess.Popen(['python', 'hw.py', handwriting_image_path, text_file_path, generated_image_path])
        
        # Wait for adjust.py and hw.py processes to complete (optional)
        hw_process.wait()
        
        return jsonify({
            'success': True,
            'image_url': f'/generated/generated_handwritten_text.png'
        })
    
    return jsonify({'success': False}), 500

@app.route('/generated/<filename>')
def generated_file(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

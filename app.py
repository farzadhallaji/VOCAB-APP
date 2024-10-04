from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
from markupsafe import Markup
import shutil

app = Flask(__name__)

# Define the number of HTML files to show per page
WORD_PER_PAGE = 23

# Directories for each type
directories = {
    "known": "./known",
    "pronunciation": "./pronunciation",
    "guessable": "./guessable",
    "unknown": "./unknown",
    "unfamiliar": "./unfamiliar",
    "not-reviewed": "./not-reviewed"
}

# Ensure directories exist
for directory_path in directories.values():
    os.makedirs(directory_path, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def list_folders():
    selected_main_folder = request.form.get('main_folder', 'not-reviewed')
    selected_sub_folder = request.form.get('sub_folder', '')

    # Path for the main selected folder
    main_folder_path = directories[selected_main_folder]
    main_folders = list(directories.keys())
    sub_folders = [f.name for f in os.scandir(main_folder_path) if f.is_dir()]

    files_content = {}
    if request.method == 'POST' and selected_sub_folder:
        # Path for the selected sub-folder
        sub_folder_path = os.path.join(main_folder_path, selected_sub_folder)
        if os.path.isdir(sub_folder_path):
            html_files = [f for f in os.listdir(sub_folder_path) if f.endswith('.html')][:WORD_PER_PAGE]
            files_content = {f: Markup(open(os.path.join(sub_folder_path, f), 'r').read()) for f in html_files}

    return render_template('index.html', main_folders=main_folders, sub_folders=sub_folders,
                           selected_main_folder=selected_main_folder, selected_sub_folder=selected_sub_folder, files_content=files_content)


@app.route('/move-file', methods=['POST'])
def move_file():
    filename = request.form['filename']
    target_folder = request.form['target_folder']
    source_main_folder = request.form['source_main_folder']
    source_sub_folder = request.form['source_sub_folder']

    source_folder_path = os.path.join(directories[source_main_folder], source_sub_folder)
    source_path = os.path.join(source_folder_path, filename)

    if os.path.exists(source_path):
        # Move the file to the target directory
        target = os.path.join(directories[target_folder], source_sub_folder)
        os.makedirs(target, exist_ok=True)
        target_path = os.path.join(target, filename)
        shutil.move(source_path, target_path)
        # Return success message in JSON format
        return {"status": "success"}, 200

    return {"status": "error", "message": "File not found"}, 404


@app.route('/files/<path:filename>')
def serve_file(filename):
    # Validate and serve a file from the filesystem safely
    safe_path = secure_filename(filename)  # Ensuring the filename is secure
    directory = os.path.dirname(safe_path)  # Extract directory path
    filename = os.path.basename(safe_path)  # Ensure only the filename without path
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)  # or any other port you prefer

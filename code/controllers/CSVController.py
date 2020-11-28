from code.main import app
from flask import request, redirect, flash, render_template
from werkzeug.utils import secure_filename
import os

def has_allowed_ext(filename, extensions):
    # print(filename.rsplit('.', 1))
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route('/test', methods=['GET'])
def test():
    return render_template("csv.html")

@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    if 'csv_file' in request.files:
        file = request.files['csv_file']
        # print(file.filename.rsplit('.', 1))
        if file and has_allowed_ext(file.filename, ('csv')):
            filename = secure_filename(file.filename)
            storage_location = os.path.join('storage', 'csv_files')
            if not os.path.exists(storage_location):
                os.makedirs(storage_location)

            file.save(os.path.join(storage_location, filename))
            return redirect(request.referrer)
    flash('errror')
    return redirect(request.referrer)
            #file.save(os.path.join('../storage'))

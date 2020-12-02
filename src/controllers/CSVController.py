from src.main import app
from flask import request, redirect, flash, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import pandas
import time

def has_allowed_ext(filename, extensions):
    # print(filename.rsplit('.', 1))
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


def create_directory(*args, **kwargs):
    if 'file' in kwargs:
        return os.path.join(create_directory(*args), kwargs.get('file'))
    location = os.path.join(*args)
    if not os.path.exists(location):
        os.makedirs(location)
    return location


def hash_filename(filename):
    _, ext = secure_filename(filename).rsplit('.', 1)
    current_time = int(round(time.time() * 1000))
    return str(hash(str(current_time) + filename)) + '.' + ext


@app.route('/test', methods=['GET'])
def test():
    return render_template("csv.html")


@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    """
    check if file upload extension is CSV
    create a unique hash based on file name
    save the file with unique hash name
    convert CSV to JSON data
    if required columns are present then return
    otherwise everything values and redirects back
    :return: Success HTTP 200 / Fail HTTP 301
    """
    if 'csv_file' in request.files:
        file = request.files['csv_file']
        if file and has_allowed_ext(file.filename, ['csv']):
            filename = hash_filename(file.filename)
            save_location = create_directory(app.storage_path, 'csv_files', file=filename)
            file.save(save_location)
            data = pandas.read_csv(save_location)
            columns = set(['timestamp', 'temp_f', 'temp_c'])
            if columns.issubset(data.to_dict().keys()):
                print(data.to_json(orient='records'))
                return jsonify(data.to_json(orient='records'))
            else:
                flash('CSV must have [%s] columns' % ', '.join(columns))
        else:
            flash('File must be CSV')
    else:
        flash('Could not upload or parse file')
    return redirect(request.referrer)

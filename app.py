import re
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from database import db, init_db  # Import database and initialization
from models import Carrot, Potato
from datetime import datetime

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'sqlite:///sensitive_data.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Initialize the database
init_db(app)

ALLOWED_EXTENSIONS = {'txt'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def classify_data(content):
    patterns = {
        "PAN": r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
        "Health ID": r"\b\d{6,10}\b",
        "Medical Record ID": r"\bMED-\d{9}\b",
        "Test Results": r"\b(Positive|Negative)\b",
    }

    classified_data = []

    for classification, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                if classification == "Health ID" and match == "123456789":
                    continue
                classified_data.append({
                    "data": match,
                    "classification": classification
                })
        else:
            classified_data.append({
                "data": "Not Found",
                "classification": classification
            })

    return classified_data


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Check if the file already exists in the database
            existing_file = Carrot.query.filter_by(filename=filename).first()
            if existing_file:
                return jsonify({
                    "error": "File with this name already exists."
                }), 409

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(filepath)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                upload_time = datetime.utcnow()  # Use UTC for consistency
                carrot = Carrot(filename=filename, upload_time=upload_time)
                db.session.add(carrot)
                db.session.commit()

                classified_data = classify_data(content)

                for entry in classified_data:
                    potato = Potato(
                        carrot_id=carrot.id,
                        sensitive_data=entry['data'],
                        classification=entry['classification']
                    )
                    db.session.add(potato)
                db.session.commit()

                return jsonify({
                    "message": "File uploaded and scanned successfully",
                    "status": "success"
                }), 200

            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"Error processing file: {e}"}), 500
        else:
            return jsonify({
                "error": "Invalid file type. Only .txt files are allowed."
            }), 400

    return render_template('index.html')


@app.route('/list')
def list_files():
    scans = db.session.query(Carrot, Potato).join(Potato).all()

    grouped_scans = {}
    for carrot, potato in scans:
        if carrot.filename not in grouped_scans:
            grouped_scans[carrot.filename] = []
        grouped_scans[carrot.filename].append({
            "carrot_id": carrot.id,
            "potato_id": potato.id,
            "sensitive_data": potato.sensitive_data,
            "classification": potato.classification,
            "upload_time": carrot.upload_time
        })

    return render_template('list.html', grouped_scans=grouped_scans)


@app.route('/delete/<int:potato_id>', methods=['POST'])
def delete_row(potato_id):
    try:
        potato = Potato.query.get(potato_id)
        if potato:
            db.session.delete(potato)
            db.session.commit()
            return redirect(url_for('list_files'))
        else:
            return jsonify({"error": "Row not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error deleting row: {e}"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8080)

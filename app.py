import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class ViewCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=0)

# Function to initialize the database
def initialize_database():
    db.create_all()
    if ViewCount.query.count() == 0:
        initial_view = ViewCount(count=0)
        db.session.add(initial_view)
        db.session.commit()

@app.before_request
def before_request():
    initialize_database()

@app.route('/increment', methods=['POST'])
def increment():
    try:
        view_count = ViewCount.query.first()
        view_count.count += 1
        db.session.commit()
        return jsonify({'message': 'View incremented', 'current_count': view_count.count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/views', methods=['GET'])
def get_views():
    try:
        view_count = ViewCount.query.first()
        return jsonify({'view_count': view_count.count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

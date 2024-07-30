import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

if not os.getenv('DATABASE_URL'):
    raise ValueError("No DATABASE_URL set for Flask application")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ViewCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=0)

def initialize_database():
    try:
        db.create_all()
        if ViewCount.query.count() == 0:
            initial_view = ViewCount(count=0)
            db.session.add(initial_view)
            db.session.commit()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.session.rollback()

@app.before_first_request
def before_first_request():
    initialize_database()

@app.after_request
def after_request(response):
    db.session.close()
    return response

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

from flask import Flask, jsonify
import psycopg
import os

app = Flask(__name__)

# Load database connection URL
DB_URL = os.getenv("DATABASE_URL")

def test_db_connection():
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

@app.route('/test-db', methods=['GET'])
def test_db():
    if test_db_connection():
        return jsonify({"message": "Database connected successfully!"})
    return jsonify({"error": "Failed to connect to the database."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

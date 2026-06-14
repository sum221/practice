from flask import Flask, render_template, request, jsonify
import sqlite3
import sys

app = Flask(__name__)
DATABASE = 'exercises.db'

def init_db():
    """Initialize database with sample exercises"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Create table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS exercises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        type TEXT DEFAULT 'fill_blank'
                    )''')
        
        # Check if empty and seed with Simple Present examples
        c.execute('SELECT count(*) FROM exercises')
        if c.fetchone()[0] == 0:
            sample_data = [
                ("She _____ (go) to school every day.", "goes", "fill_blank"),
                ("_____ you like pizza?", "Do", "fill_blank"),
                ("The sun _____ in the east.", "rises", "fill_blank"),
                ("We _____ not play football on Sundays.", "do", "fill_blank"),
                ("He _____ (work) at a bank.", "works", "fill_blank")
            ]
            c.executemany('INSERT INTO exercises (question, correct_answer, type) VALUES (?, ?, ?)', sample_data)
            conn.commit()
            print("✓ Database initialized with sample exercises")
        
        conn.close()
    except Exception as e:
        print(f"✗ Database error: {e}")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT id, question FROM exercises")
        rows = c.fetchall()
        conn.close()
        
        exercises = [{"id": row[0], "question": row[1]} for row in rows]
        return jsonify(exercises)
    except Exception as e:
        print(f"Error fetching exercises: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check', methods=['POST'])
def check_answer():
    try:
        data = request.json
        exercise_id = data.get('id')
        user_answer = data.get('answer').strip().lower()
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT correct_answer FROM exercises WHERE id=?", (exercise_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            correct = row[0].strip().lower()
            is_correct = user_answer == correct
            return jsonify({
                "correct": is_correct, 
                "message": "Correct!" if is_correct else f"Incorrect. The answer was '{row[0]}'."
            })
        
        return jsonify({"error": "Exercise not found"}), 404
    except Exception as e:
        print(f"Error checking answer: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/add', methods=['POST'])
def add_exercise():
    try:
        data = request.json
        question = data.get('question')
        answer = data.get('answer')
        
        if not question or not answer:
            return jsonify({"error": "Missing fields"}), 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO exercises (question, correct_answer) VALUES (?, ?)", (question, answer))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error adding exercise: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        init_db()
        print("=" * 40)
        print("Starting English Practice Server...")
        print("=" * 40)
        
        # Try port 5000 first, then fall back to others
        for port in [5000, 5001, 8080]:
            try:
                app.run(debug=True, host='0.0.0.0', port=port)
                break
            except OSError as e:
                print(f"Port {port} unavailable, trying next...")
                
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Critical error starting server: {e}")
        sys.exit(1)

from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
from .load_school_data import load_school_data
from .errorrecog import log_error

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Create a directory for logs
if not os.path.exists('logs'):
    os.makedirs('logs')

# Load school data from JSON file
school_data = load_school_data()

# Function to calculate the new grade
def calculate_grade(current_percentage, new_scores):
    total_percentage = current_percentage
    total_weight = 1
    for score in new_scores:
        weight = score.get('weight', 1)
        total_percentage += score['percentage'] * weight
        total_weight += weight
    return total_percentage / total_weight

# Function to get the letter grade
def get_letter_grade(percentage):
    if percentage >= 93:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

@app.route('/')
def index():
    return render_template('index.html', school_data=school_data)

@app.route('/get_schools', methods=['POST'])
def get_schools_endpoint():
    try:
        data = request.get_json()
        district = data['district']
        grade = data['grade']
        schools = school_data.get(district, {}).get(grade, [])
        return jsonify(schools)
    except Exception as e:
        log_error(e)
        return jsonify({"error": "An error occurred while fetching the school data."}), 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        school_name = request.form['school_name']
        district = request.form['district']
        grade_number = request.form['grade_number']
        return redirect(url_for('calculate', student_id=student_id, first_name=first_name, last_name=last_name,
                                school_name=school_name, district=district, grade_number=grade_number))
    except Exception as e:
        log_error(e)
        return render_template('error.html'), 500

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        try:
            student_id = request.form['student_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            school_name = request.form['school_name']
            district = request.form['district']
            grade_number = request.form['grade_number']
            current_percentage = float(request.form['current_percentage'])
            new_scores = []
            for i in range(int(request.form['num_assignments'])):
                percentage = float(request.form[f'percentage_{i}'])
                weight = float(request.form.get(f'weight_{i}', 1))
                category = request.form[f'category_{i}']
                new_scores.append({'percentage': percentage, 'weight': weight, 'category': category})
            new_percentage = calculate_grade(current_percentage, new_scores)
            letter_grade = get_letter_grade(new_percentage)

            # Create a directory for the district
            district_path = os.path.join('logs', district)
            if not os.path.exists(district_path):
                os.makedirs(district_path)

            # Log the student information
            log_file = os.path.join(district_path, f'{school_name}.txt')
            with open(log_file, 'a') as f:
                f.write(f'{first_name} {last_name}, ID: {student_id}, Grade: {grade_number}, Percentage: {new_percentage:.2f}%, Letter: {letter_grade}\n')

            return render_template('calculate.html', student_id=student_id, first_name=first_name, last_name=last_name,
                                   school_name=school_name, district=district, grade_number=grade_number,
                                   new_percentage=new_percentage, letter_grade=letter_grade, new_scores=new_scores)
        except Exception as e:
            log_error(e)
            return render_template('error.html'), 500
    else:
        try:
            student_id = request.args.get('student_id')
            first_name = request.args.get('first_name')
            last_name = request.args.get('last_name')
            school_name = request.args.get('school_name')
            district = request.args.get('district')
            grade_number = request.args.get('grade_number')
            return render_template('calculate.html', student_id=student_id, first_name=first_name, last_name=last_name,
                                   school_name=school_name, district=district, grade_number=grade_number)
        except Exception as e:
            log_error(e)
            return render_template('error.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

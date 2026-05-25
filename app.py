from flask import Flask, render_template, request
import os
import PyPDF2
import docx

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

skills = [
    "Python", "Java", "C++", "HTML", "CSS",
    "JavaScript", "SQL", "Flask", "Machine Learning"
]

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/generated_resume', methods=['POST'])
def generated_resume():

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    skills = request.form['skills']
    education = request.form['education']
    projects = request.form['projects']

    return render_template(
        'generated_resume.html',
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        education=education,
        projects=projects
    )

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['resume']

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(filepath)
        else:
            text = ""

        found_skills = []
        missing_skills = []

        for skill in skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)
            else:
                missing_skills.append(skill)

        total_skills = len(skills)
        matched_skills = len(found_skills)
        score = int((matched_skills / total_skills) * 100)

        suggestion = ""
        if score >= 80:
          suggestion = "Excellent resume. Your resume is ATS friendly."
        elif score >= 50:
         suggestion = "Good resume, but you can add more relevant skills."
        else:
         suggestion = "Your resume needs improvement. Add more technical skills."        

        return render_template(
            'result.html',
            found_skills=found_skills,
            missing_skills=missing_skills,
            score=score,
            suggestion=suggestion
        )

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

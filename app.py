import random
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = '비밀키'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100 ), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)
    

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    words = word.query.all()
    return render_template("index.html", words=words)


@app.route('/add', methods=['GET', 'POST'])
def add_word():
    if request.method == 'POST':
        new_word = word(
            word=request.form['word'],
            meaning=request.form['meaning']
        )
        db.session.add(new_word)
        db.session.commit()
        return redirect('/')
    return render_template("add.html")


# 🔸 퀴즈 출제
@app.route('/quiz')
def quiz():
    words = word.query.all()
    if not words:
        return "단어가 없습니다. 먼저 단어를 추가하세요."
    question = random.choice(words)
    session['answer'] = question.meaning
    return render_template("quiz.html", word=question.word)


# 🔸 정답 체크
@app.route('/check', methods=['POST'])
def check():
    user_answer = request.form['meaning'].strip().lower()
    correct_answer = session.get('answer', '').strip().lower()
    result = (user_answer == correct_answer)
    return render_template("result.html", result=result, correct=correct_answer, user=user_answer)


@app.route('/quiz/mcq')
def quiz_mcq():
    words = word.query.all()
    if len(words) < 4:
        return "객관식 퀴즈는 최소 4개 이상의 단어가 필요합니다."
    

    question = random.choice(words)
    choices = random.sample([w.meaning for w in words if w.id != question.id], 3)
    choices.append(question.meaning)
    random.shuffle(choices)


    session['answer'] = question.meaning
    session['question_word'] = question.word
    return render_template("quiz_mcq.html", word=question.word, choices=choices)


@app.route('/check/mcq', methods=['POST'])
def check_mcq():
    user_answer = request.form['choice'].strip()
    correct_answer = session.get('answer', '')
    question_word = session.get('question_word', '')
    result = (user_answer == correct_answer)


    if not result:
        wrong_list = session.get('wrong_answers', [])
        wrong_list.append({'word': question_word, 'correct': correct_answer})
        session['wrong_answers'] = wrong_list

    return render_template("result_mcq.html", result=result, correct=correct_answer, user=user_answer)


@app.route('/review')
def review():
    wrong_list = session.get('wrong_answers', [])
    return render_template("review.html", wrong_list=wrong_list)


@app.route('/review/quiz')
def review_quiz():
    wrong_list = session.get('wrong_answers', [])
    if not wrong_list:
        return "복습할 단어가 없습니다."
    

    question = random.choice(wrong_list)
    session['answer'] = question['correct']
    session['question_word'] = question['word']
    return render_template("quiz_mcq.html", word=question['word'], choices=[question['correct'], "오답 예시1", "오답 예시2", "오답 예시3"])


if __name__ == '__main__':
    app.run(debug=True)
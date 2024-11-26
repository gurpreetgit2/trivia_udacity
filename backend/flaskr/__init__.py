from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in questions]
    return formatted_questions[start:end]


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        if not categories:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
            }
        )

    @app.route("/questions", methods=["GET"])
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()
        current_questions = paginate_questions(request, questions)
        if not current_questions:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(404)
        try:
            question.delete()
            db.session.commit()
            return jsonify({"success": True, "deleted": question_id})
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    @app.route("/questions", methods=["POST"])
    def add_question():
        data = request.get_json()
        question_text = data.get("question")
        answer = data.get("answer")
        category = data.get("category")
        difficulty = data.get("difficulty")

        if not (question_text and answer and category and difficulty):
            abort(400)

        try:
            new_question = Question(
                question=question_text,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )
            new_question.insert()
            return jsonify({"success": True})
        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        data = request.get_json()
        search_term = data.get("searchTerm", "")

        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        if not questions:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(questions),
            }
        )

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.filter_by(category=str(category_id)).all()
        if not questions:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(questions),
                "current_category": category_id,
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        data = request.get_json()
        previous_questions = data.get("previous_questions", [])
        quiz_category = data.get("quiz_category", {})

        if quiz_category.get("id"):
            questions = (
                Question.query.filter_by(category=str(quiz_category["id"]))
                .filter(Question.id.notin_(previous_questions))
                .all()
            )
        else:
            questions = Question.query.filter(
                Question.id.notin_(previous_questions)
            ).all()

        if not questions:
            return jsonify({"success": True, "question": None})

        next_question = random.choice(questions).format()
        return jsonify({"success": True, "question": next_question})

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable entity"}
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    return app

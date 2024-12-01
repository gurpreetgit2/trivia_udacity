from sqlalchemy import inspect, text
import os
import unittest
import json
from flaskr import create_app
from models import db, Question, Category
import subprocess
from dotenv import load_dotenv


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    # Load environment variables from .env file
    load_dotenv()

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.getenv("DB_NAME_TEST")
        self.database_user = os.getenv("DB_USER_TEST")
        self.database_password = os.getenv("DB_PASS_TEST")
        self.database_host = os.getenv("DB_HOST_TEST")
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Path to the trivia.psql file
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # Directory of this script
        psql_file_path = os.path.join(base_dir, "trivia.psql")

        # load test db with data
        try:
            # Load the initial test data
            with open(psql_file_path, "r") as psql_file:
                subprocess.run(
                    ["psql", self.database_name],
                    stdin=psql_file,
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            print(f"Error setting up the test database: {e}")
            raise

        # Create app with the test configuration
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    from sqlalchemy import inspect, text

    def tearDown(self):
        """
        Executed after each test.
        Drop all relations.
        """
        with self.app.app_context():
            db.session.remove()  # Clear the session

            # Use raw SQL to drop tables
            with db.engine.connect() as connection:
                transaction = connection.begin()  # Begin a transaction
                try:
                    # Reflect the database and drop each table with CASCADE
                    inspector = inspect(db.engine)
                    for table_name in inspector.get_table_names():
                        print(f"Dropping table: {table_name}")
                        connection.execute(
                            text(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                        )

                    transaction.commit()  # Commit the transaction
                    print("All tables dropped successfully.")
                except Exception as e:
                    transaction.rollback()  # Rollback in case of an error
                    print(f"Error dropping tables: {e}")

    def test_get_categories_success(self):
        """Test retrieving all categories."""
        response = self.client.get("/categories")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["categories"])

    def test_get_categories_failure(self):
        """Test 404 error when no categories exist."""
        with self.app.app_context():
            db.session.query(Category).delete()
            db.session.commit()

        response = self.client.get("/categories")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        print(f"The status code is: {response.status_code}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_questions_success(self):
        """Test retrieving paginated questions."""
        response = self.client.get("/questions?page=1")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_get_questions_failure(self):
        """Test 404 error when no questions are available."""
        with self.app.app_context():
            db.session.query(Question).delete()
            db.session.commit()

        response = self.client.get("/questions")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_delete_question_success(self):
        """Test deleting an existing question."""
        with self.app.app_context():
            question = db.session.query(Question).first()
            question_id = question.id if question else None

        if question_id:
            response = self.client.delete(f"/questions/{question_id}")
            data = json.loads(response.data)
            print(f"The response JSON is: {data}")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["success"])
            self.assertEqual(data["deleted"], question_id)

    def test_delete_question_failure(self):
        """Test 404 error when deleting a non-existent question."""
        response = self.client.delete("/questions/9999")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_add_question_success(self):
        """Test adding a new question."""
        new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": "1",
            "difficulty": 2,
        }
        response = self.client.post("/questions", json=new_question)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["success"])

    def test_add_question_failure(self):
        """Test 400 error when adding a question with incomplete data."""
        incomplete_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
        }
        response = self.client.post("/questions", json=incomplete_question)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])

    def test_search_questions_success(self):
        """Test searching for questions."""
        search_data = {"searchTerm": "autobiography"}
        response = self.client.post("/questions/search", json=search_data)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])

    def test_search_questions_failure(self):
        """Test 404 error when searching for a non-existent term."""
        search_data = {"searchTerm": "xyz"}
        response = self.client.post("/questions/search", json=search_data)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_questions_by_category_success(self):
        """Test retrieving questions by category."""
        response = self.client.get("/categories/1/questions")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])

    def test_get_questions_by_category_failure(self):
        """Test 404 error when category has no questions."""
        response = self.client.get("/categories/999/questions")
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_play_quiz_success(self):
        """Test playing quiz with available questions."""
        quiz_data = {
            "previous_questions": [],
            "quiz_category": {"id": "1"},
        }
        response = self.client.post("/quizzes", json=quiz_data)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["question"])

    def test_play_quiz_failure(self):
        """Test playing quiz with no available questions."""
        quiz_data = {
            "previous_questions": [1],
            "quiz_category": {"id": "999"},
        }
        response = self.client.post("/quizzes", json=quiz_data)
        data = json.loads(response.data)
        print(f"The response JSON is: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNone(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

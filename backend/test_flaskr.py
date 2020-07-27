import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        database_name = "trivia_test"
        database_user = "trivia_test"
        database_user_pass = "0123456"
        self.database_path = "postgres://{}:{}@{}/{}".format(database_user, database_user_pass, 'localhost:5432', database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
          "question": "question_test",
          "answer": "answer2",
          "difficulty": 4,
          "category": 2
        }
        self.quiz_data = {
          'category': 2,
          'previous_questions': [21]
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions_by_category(self):
        res = self.client().get('/api/questions?category_id=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(all(item['category'] == '1' for item in data['questions']))

    def test_get_questions_of_invalid_category(self):
        res = self.client().get('/api/questions?category_id=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_get_questions_with_invalid_page_num(self):
        res = self.client().get('/api/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete('/api/questions/11')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)

    def test_delete_not_exists_question(self):
        res = self.client().delete('/api/questions/2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_question_successful_creation(self):
        res = self.client().post('/api/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_question_failed_creation(self):
       res = self.client().post('/api/questions', json={})
       data = json.loads(res.data)

       self.assertEqual(res.status_code, 400)
       self.assertEqual(data['success'], False)
       self.assertEqual(data['message'], 'bad request')

    def test_get_next_question(self):
        res = self.client().post('/api/get-question', json=self.quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_next_question_with_invalid_data(self):
        res = self.client().post('/api/get-question', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_search_for_questions(self):
        res = self.client().post('/api/questions/search', json={'keyword': 'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
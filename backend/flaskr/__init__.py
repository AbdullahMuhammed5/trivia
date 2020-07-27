import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, not_


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  Using the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  GET requests for all available categories.
  '''
  @app.route('/api/categories')
  def list_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total': len(formatted_categories)
    })

  def paginate_questions(request, questions_query):
      page = request.args.get('page', 1, type=int)
      start =  (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = [question.format() for question in questions_query]
      current_page = questions[start:end]

      return current_page

  '''
  - GET requests for questions, including pagination (every 10 questions).
  This endpoint should return a list of questions, 
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 

  - Get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/api/questions')
  def retrieve_questions():

    if request.args.get('category_id'):
      category_id = request.args.get('category_id')
      questions = Question.query.filter_by(category=category_id).order_by(Question.id).all()
    else:
      questions = Question.query.order_by(Question.id).all()

    questions_paginated = paginate_questions(request, questions)

    if len(questions_paginated) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'questions': questions_paginated,
        'total_questions': len(Question.query.all()),
        'categories': [category.format() for category in Category.query.all()],
        'current_category': 1
    })

  '''
  DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      abort(422)

  '''
  POST request for creating a new question,
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/api/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    difficulty = body.get('difficulty', None)
    category_id = body.get('category', None)

    try:
      question = Question(question=question, answer=answer, difficulty=difficulty, category=category_id)
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id
      })
    except:
      abort(422)

  '''
  Get questions based on a search term.
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions/search', methods=['POST'])
  def questions_search():
    term = request.get_json()['keyword']
    term = "%{}%".format(term)

    try:
      results = Question.query.filter(Question.question.ilike(term)).all()
      paginated_results = paginate_questions(request, results)

      return jsonify({
        'success': True,
        'questions': paginated_results,
        'total_results': len(results)
      })
    except:
      abort(422)


  # done
  '''
  POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/api/get-question', methods=['POST'])
  def get_question():

    try:

      body = request.get_json()

      category = body.get('category', None)
      previous_questions = body.get('previous_questions', None)
      print(category)
      print(previous_questions)

      if category == 0: # return question for any category
        question = Question.query.filter(Question.id.notin_(previous_questions)) \
                          .order_by(func.random()).limit(1).first()
      else: # return question form specific category
        question = Question.query.filter_by(category=category).filter(Question.id.notin_(previous_questions)) \
                          .order_by(func.random()).limit(1).first()
      question_data = None
      if question:
        question_data = {
          'id': question.id,
          'question': question.question,
          'answer': question.answer,
          'difficulty': question.difficulty,
          'category': question.category
        }

      return jsonify({
        'success': True,
        'question': question_data,
        'previous_questions': previous_questions
      })
    except:
      abort(422)

  '''
  Error handlers for all expected errors
  including 400, 404, 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400
  
  return app

    
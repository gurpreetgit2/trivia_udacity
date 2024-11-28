# Trivia API Documentation

This documentation provides detailed information about the available API endpoints in the Trivia application. Each endpoint is described with its URL, request parameters, and expected response body.

## API Endpoints

### 1. GET `/categories`
**Description**: Fetches all categories.

**Request Parameters**: None

**Response Body**:
```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art"
    // other categories
  }
}
```
### 2. GET `/questions`
**Description**: Fetches all questions with pagination.

**Request Parameters**: page (optional): Page number for pagination (default: 1)

**Response Body**:
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": "1",
      "difficulty": 1
    }
    // other questions
  ],
  "total_questions": 50
}
```
### 3. DELETE /questions/question_id
**Description**: Deletes a specific question.

**Request Parameters**: None

**Response Body**:
```json
{
  "success": true,
  "deleted": 1
}
```
### 4. POST /questions
**Description**: Adds a new question.

**Request Parameters**: None

**Request Body**:
```json
{
  "question": "What is the largest planet?",
  "answer": "Jupiter",
  "category": "1",
  "difficulty": 3
}
```

**Response Body**:
```json
{
  "success": true
}
```
### 5. POST /questions/search
**Description**: Adds a new question.

**Request Parameters**: None

**Request Body**:
```json
{
  "searchTerm": "planet"
}
```
**Response Body**:
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the largest planet?",
      "answer": "Jupiter",
      "category": "1",
      "difficulty": 3
    }
    // other matching questions
  ],
  "total_questions": 1
}
```
### 6. GET /categories/category_id/questions
**Description**: Fetches questions for a specific category.

**Request Parameters**: None

**Response Body**:
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": "1",
      "difficulty": 1
    }
    // other questions in the category
  ],
  "total_questions": 10,
  "current_category": 1
}
```
### 7. POST /quizzes
**Description**: Fetches the next question for a quiz.

**Request Parameters**: None

**Request Body**:
```json
{
  "previous_questions": [1, 2],
  "quiz_category": {
    "id": "1",
    "type": "Science"
  }
}
```
**Response Body**:
```json
{
  "success": true,
  "question": {
    "id": 3,
    "question": "What is the boiling point of water?",
    "answer": "100°C",
    "category": "1",
    "difficulty": 1
  }
}
```
### 8. ERROR HANDLING
**The API returns error responses in the following format**:
```json
{
  "success": false,
  "error": 404,
  "message": "Resource not found"
}
```
**Error Codes**:
- 400: Bad request
- 404: Resource not found
- 422: Unprocessable entity


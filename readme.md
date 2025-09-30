# Backend – Exam System

This backend was developed according to the **initial group project plan** submitted at the start of the course.  

The backend was originally built with **Django** to support a separated architecture (Vue frontend + Django backend).  
It includes all the required APIs for managing students, exams, and questions, as well as features for statistics and result analysis.  

Although the team later moved to a combined **Next.js architecture**, this Django backend still demonstrates the original planned design and fully implements the project requirements.  



## Getting Started

Follow the steps below to run the backend locally:

**1. Clone the repository**

```bash
git clone <your-repo-link>
cd backend
```

**2. Create and activate a virtual environment**

```
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

**3. Install dependencies**

```
pip install -r requirements.txt
```

**4. Run database migrations**

```
python manage.py makemigrations
python manage.py migrate
```

**5. Create a superuser (for admin access)**

```
python manage.py createsuperuser
```

**6. Start the development server**

```
python manage.py runserver
```

**7. Access the backend**

- API endpoints: `http://127.0.0.1:8000/api/`



## User API

**Base path**: `/api/user/`

### 1. User Login

**Endpoint**  
`POST /api/user/login/`

**Description**  
Authenticate a user and return a JWT token.  
This endpoint does **not** require a token.

**Request Body**
```json
{
  "username": "admin",
  "password": "yourpassword"
}
```

**Response (200 OK)**
```json
{
  "token": "<JWT_TOKEN>",
  "user": {
    "uid": "12345",
    "username": "admin",
    "email": "admin@example.com",
    "is_superuser": true
  }
}
```

**Response (400 Bad Request)**
```json
{
  "detail": "Invalid username or password"
}
```

**Notes**
- Use the token in headers for all protected endpoints:  
  `Authorization: JWT <your_token>`  
- Superuser-only endpoints require `is_superuser = true`.

---

## Questions API

**Base path**: `/api/questions/`

This module manages exam questions and choices.  
Supports CRUD operations, search, filter, and CSV bulk import.

All `/api/questions/` endpoints **require authentication (JWT)**, unless specifically whitelisted.  

Example header:  `Authorization: JWT <your_token>`

---

### 1. List Questions

**Endpoint**  
`GET /api/questions/`

**Query Parameters**
- `search`: search by `name` or `question_text`  
- `category`: filter by category  
- `level`: filter by difficulty  

**Response**
```json
[
  {
    "id": 1,
    "name": "Math Q1",
    "type": "Single Choice",
    "level": "Level 1",
    "category": "Math",
    "marks": 5,
    "question_text": "What is 2 + 2?",
    "choices": [
      {"id": 10, "text": "3", "is_correct": false},
      {"id": 11, "text": "4", "is_correct": true}
    ]
  }
]
```

---

### 2. Retrieve Question

**Endpoint**  
`GET /api/questions/{id}/`

**Description**  
Retrieve a single question by ID.

---

### 3. Create Question

**Endpoint**  
`POST /api/questions/`

**Request Body**
```json
{
  "name": "Math Q1",
  "type": "Single Choice",
  "level": "Level 1",
  "category": "Math",
  "marks": 5,
  "question_text": "What is 2 + 2?",
  "choices": [
    {"text": "3", "is_correct": false},
    {"text": "4", "is_correct": true}
  ]
}
```

**Response (201 Created)**
```json
{
  "id": 1,
  "name": "Math Q1",
  "type": "Single Choice",
  "level": "Level 1",
  "category": "Math",
  "marks": 5,
  "question_text": "What is 2 + 2?",
  "choices": [
    {"id": 10, "text": "3", "is_correct": false},
    {"id": 11, "text": "4", "is_correct": true}
  ]
}
```

---

### 4. Update Question

**Endpoint**  
`PUT /api/questions/{id}/`

**Description**  
Update an existing question by ID.

---

### 5. Delete Question

**Endpoint**  
`DELETE /api/questions/{id}/`

**Description**  
Delete a question by ID.

---

### 6. Import Questions from CSV

**Endpoint**  
`POST /api/questions/import_csv/`

**Description**  
Bulk import questions and choices from a CSV file.

**Expected CSV Header**
```
name,type,level,category,marks,question,choices,correctIndex
```

**Example Row**
```csv
Math Q1,Single Choice,Level 1,Math,5,What is 2+2?,3|4,1
```

- `choices` separated by `|`  
- `correctIndex` is comma-separated list of correct choices (0-based index)  

**Response (201 Created)**
```json
{
  "message": "Imported 10 questions"
}
```

---





## Test Papers API

**Base path**: `/api/test-papers/`

This module manages exam papers. Teachers can create, update, delete, and preview test papers.  
It also supports dynamic generation of questions based on level configurations (count-based or marks-based).

---

### 1. List Test Papers

**Endpoint**  
`GET /api/test-papers/`

**Description**  
Retrieve a list of all available test papers.

**Response (200 OK)** (example)
```json
[
  {
    "id": 1,
    "title": "Math Paper 1",
    "level": "Level 1",
    "category": "Math",
    "created_at": "2025-09-29T10:00:00Z",
    "pass_percentage": 50
  }
]
```

---

### 2. Retrieve Test Paper

**Endpoint**  
`GET /api/test-papers/{id}/`

**Description**  
Retrieve details of a specific test paper by ID.

---

### 3. Create Test Paper

**Endpoint**  
`POST /api/test-papers/`

**Request Body (JSON)**  
(Example, structure depends on your `TestPaperSerializer`)
```json
{
  "title": "Math Paper 1",
  "level": "Level 1",
  "category": "Math",
  "pass_percentage": 50,
  "level_config": {
    "Level 1": {
      "mode": "count",
      "exam_questions": 5
    },
    "Level 2": {
      "mode": "marks",
      "total_marks": 20
    }
  }
}
```

**Response (201 Created)**  
```json
{
  "id": 1,
  "title": "Math Paper 1",
  "level": "Level 1",
  "category": "Math",
  "pass_percentage": 50,
  "level_config": {
    "Level 1": {"mode": "count", "exam_questions": 5},
    "Level 2": {"mode": "marks", "total_marks": 20}
  }
}
```

---

### 4. Update Test Paper

**Endpoint**  
`PUT /api/test-papers/{id}/`

**Description**  
Update details of a test paper.

---

### 5. Delete Test Paper

**Endpoint**  
`DELETE /api/test-papers/{id}/`

**Description**  
Delete a test paper by ID.

---

### 6. Generate Questions

**Endpoint**  
`GET /api/test-papers/{id}/generate/`

**Description**  
Dynamically generate questions for a test paper based on its `level_config`.  
This endpoint **does not save the generated questions** to the database.

**Rules**

- `mode == "count"` → Select exactly `exam_questions` questions. If not enough, return error.  
- `mode == "marks"` → Select a combination of questions that sum exactly to `total_marks`. If impossible, return error.  

**Response (200 OK)** (example)
```json
{
  "id": 1,
  "title": "Math Paper 1",
  "category": "Math",
  "pass_percentage": 50,
  "generated_questions": [
    {
      "id": 10,
      "question_text": "What is 2 + 2?",
      "type": "Single Choice",
      "marks": 5,
      "level": "Level 1"
    },
    {
      "id": 11,
      "question_text": "Solve 3x + 2 = 11",
      "type": "Single Choice",
      "marks": 5,
      "level": "Level 1"
    }
  ],
  "summary": {
    "Level 1": {"mode": "count", "need": 5, "got": 5},
    "Level 2": {"mode": "marks", "need": 20, "got": 20}
  }
}
```

**Response (400 Bad Request)** (if cannot generate enough questions)
```json
{
  "detail": "Generate failed",
  "errors": [
    "[Level 2] Cannot reach exact total marks = 20 with available questions."
  ],
  "summary": {
    "Level 1": {"mode": "count", "need": 5, "got": 5},
    "Level 2": {"mode": "marks", "need": 20, "got": 15}
  }
}
```



## Students API

**Base path**: `/api/students/`

This module manages student records and their exam attempts.

---

### 1. List Students

**Endpoint**  
`GET /api/students/`

**Description**  
Retrieve a list of all registered students.

**Response (200 OK)** (example)
```json
[
  {
    "id": "uuid-student",
    "student_no": "2025001",
    "name": "Alice",
    "email": "alice@example.com",
    "created_at": "2025-09-29T10:00:00Z"
  }
]
```

---

### 2. Retrieve Student

**Endpoint**  
`GET /api/students/{id}/`

**Description**  
Retrieve details of a specific student by ID.

---

### 3. Create Student

**Endpoint**  
`POST /api/students/`

**Request Body (JSON)**  
```json
{
  "student_no": "2025002",
  "name": "Bob",
  "email": "bob@example.com"
}
```

**Response (201 Created)**  
```json
{
  "id": "uuid-student",
  "student_no": "2025002",
  "name": "Bob",
  "email": "bob@example.com",
  "created_at": "2025-09-30T09:00:00Z"
}
```

---

### 4. Update Student

**Endpoint**  
`PUT /api/students/{id}/`

**Description**  
Update details of an existing student.

---

### 5. Delete Student

**Endpoint**  
`DELETE /api/students/{id}/`

**Description**  
Delete a student by ID.

---

### 6. Get Student Exam Attempts

**Endpoint**  
`GET /api/students/{student_id}/attempts/`

**Description**  
Retrieve all exam attempts for a specific student.  

**Response (200 OK)** (example)
```json
{
  "attempts_detail": [
    {
      "attempt_id": "uuid-attempt",
      "paper_id": 2,
      "paper_title": "Math Paper 1",
      "score": 15,
      "total_marks": 20,
      "submitted_at": "2025-09-30T10:15:00Z"
    },
    {
      "attempt_id": "uuid-attempt-2",
      "paper_id": 3,
      "paper_title": "Science Paper 1",
      "score": 18,
      "total_marks": 25,
      "submitted_at": "2025-10-01T11:00:00Z"
    }
  ]
}
```



## Exam API

**Base path**: `/api/exam/`

This module handles the exam workflow: starting an exam, submitting answers, and retrieving statistics.

---

### 1. Start Exam

**Endpoint**  
`POST /api/exam/start/`

**Description**  
Start a new exam attempt. This endpoint does **not** require a token.  

**Request Body (JSON)**
```json
{
  "student_no": "2025001",
  "name": "Alice",
  "email": "alice@example.com",
  "paper_id": 2
}
```

**Response (201 Created)**
```json
{
  "attempt_id": "uuid-string",
  "attempt_token": "uuid-token",
  "paper_id": 2,
  "started_at": "2025-09-30T10:00:00Z"
}
```

---

### 2. Submit Exam

**Endpoint**  
`POST /api/exam/submit/`

**Description**  
Submit answers for an exam attempt. This endpoint does **not** require a token.

**Request Body (JSON)**  
(Example, actual structure depends on `SubmitExamSerializer`)
```json
{
  "attempt_id": "uuid-string",
  "answers": [
    {"question_id": 1, "selected_choice_ids": [10]},
    {"question_id": 2, "text_answer": "My written answer"}
  ]
}
```

**Response (200 OK)**
```json
{
  "attempt_id": "uuid-string",
  "paper_id": 2,
  "student_no": "2025001",
  "name": "Alice",
  "score": 15,
  "total_marks": 20,
  "duration_seconds": 450,
  "submitted_at": "2025-09-30T10:15:00Z",
  "details": [
    {
      "question_id": 1,
      "is_correct": true,
      "marks_awarded": 5,
      "selected_choice_ids": [10],
      "text_answer": null
    }
  ]
}
```

---

### 3. Paper Stats (Admin)

**Endpoint**  
`GET /api/exam/admin/papers/{paper_id}/stats/`

**Description**  
Get aggregated statistics for a specific exam paper.  
Optionally include wrong choice breakdown.

**Query Parameters**  
- `wrong_choices=1` → include wrong choice distribution per question.

**Response (200 OK)** (simplified example)
```json
{
  "paper_id": 2,
  "summary": {
    "total_attempts": 30,
    "avg_score": 12.5,
    "max_score": 20,
    "avg_duration": 600,
    "sum_score": 375
  },
  "by_question": [
    {"question_id": 1, "attempts": 30, "correct": 20, "wrong": 10, "avg_marks": 4.5}
  ],
  "wrong_choice_breakdown": {
    "1": [
      {
        "choice_id": 11,
        "text": "3",
        "wrong_selected": 8,
        "selected_total": 12,
        "wrong_rate_per_attempt": 0.26
      }
    ]
  }
}
```

---

### 4. Paper Result (Admin)

**Endpoint**  
`GET /api/exam/admin/papers/{paper_id}/result/`

**Description**  
Get detailed results for all student attempts of a paper.

**Response (200 OK)**
```json
{
  "paper_id": 2,
  "paper_title": "Math Level 1",
  "attempts_count": 3,
  "attempts": [
    {
      "student_id": "uuid-student",
      "student_no": "2025001",
      "student_name": "Alice",
      "score": 15,
      "total_marks": 20,
      "submitted_at": "2025-09-30T10:15:00Z"
    }
  ]
}
```

---

### 5. Global Stats (Admin)

**Endpoint**  
`GET /api/exam/admin/global-stats/`

**Description**  
Get overall statistics across all students, papers, and levels.

**Response (200 OK)** (example)
```json
{
  "student_count": 120,
  "paper_count": 5,
  "question_count": 200,
  "attempt_count": 400,
  "levels": {
    "Level 1": {
      "students": 80,
      "passed_students": 60,
      "questions": 50,
      "accuracy": 75.0
    },
    "Level 2": {
      "students": 40,
      "passed_students": 25,
      "questions": 60,
      "accuracy": 62.5
    }
  }
}
```

---

### 6. Question Choice Stats (Admin)

**Endpoint**  
`GET /api/exam/questions/{question_id}/choice-stats/`

**Description**  
Get detailed statistics for a single question and its choices.

**Response (200 OK)** (example)
```json
{
  "id": 1,
  "text": "What is 2 + 2?",
  "type": "Single Choice",
  "marks": 5,
  "category": "Math",
  "level": "Level 1",
  "attempts": 30,
  "choices": [
    {
      "choice_id": 10,
      "text": "3",
      "is_correct": false,
      "selected_total": 12,
      "wrong_selected": 8,
      "wrong_rate_per_attempt": 0.26
    },
    {
      "choice_id": 11,
      "text": "4",
      "is_correct": true,
      "selected_total": 18,
      "wrong_selected": 0,
      "wrong_rate_per_attempt": 0.0
    }
  ]
}
```


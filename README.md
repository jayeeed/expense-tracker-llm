# Expense Management System
This project is an expense management system built using FastAPI, PostgreSQL, and LangChain. It allows users to manage their expenses by adding, searching, and analyzing expense data through both text and image inputs..

## Project Structure

```
.
├── __pycache__/
├── .env
├── .gitignore
├── .vercel/
│   ├── project.json
│   ├── README.txt
├── .vscode/
│   ├── launch.json
│   ├── settings.json
├── app/
│   ├── __init__.py
│   ├── db_utils.py
│   ├── langchain_utils.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── expense.py
│   ├── tool_factory.py
├── filtered_expenses.csv
├── ingest.py
├── launch.json
├── main.py
├── README.md
├── requirements_short.txt
├── requirements.txt
├── vercel.json
```

### Key Files and Directories
- app: Contains the main application code.
    - `db_utils.py`: Database utility functions for initializing the database and executing queries.
    - `langchain_utils.py`: Utility functions for handling `LangChain` interactions.
    - `routers/`: Contains `FastAPI` routers.
      - `expense.py`: Router for `handling` expense-related endpoints.
    - `tool_factory.py`: Defines various tools for expense management, such as `creating`, `searching`, and `analyzing` expenses.
- `ingest.py`: Script for `ingesting` data from the CSV file into the database.
- `main.py`: Entry point for the `FastAPI` application.
- `requirements.txt`: Lists of dependencies.

### Workflow
1. Setting Up the Database
The database is initialized using the `init_db` function in `db_utils.py`. This function creates the `expenses` table if it does not exist.

2. Ingesting Data
Data from the CSV file is ingested into the database using the `ingest_data` function in `ingest.py`.

3. Running the Application
The `FastAPI` application is started using the `main.py` file. It includes the expense router and sets up CORS middleware.

4. Handling Requests
The application handles various types of requests through the endpoints defined in `expense.py`. The `handle_expense` endpoint processes user input to either save or search for expenses.

5. Using Tools
Various tools for managing expenses are defined in `tool_factory.py`. These tools include functions for creating expenses, searching by fields, summing expenses, identifying anomalies, and more.

#### Example Input and Output
#### Adding an Expense
#### Input:

```
{
  "id": "12345",
  "date": "2024-11-12",
  "amount": 100.0,
  "category": "food",
  "description": "Lunch at restaurant"
}
```

#### Output:

```
{
  "id": "12345",
  "date": "2024-11-12",
  "amount": 100.0,
  "category": "food",
  "description": "Lunch at restaurant"
}
```

#### Searching for Expenses
#### Input:
```
{
  "category": "food"
}
```

#### Output:

```
[
  {
    "id": "fec42ee936934b0aaff8612ffe1623fe",
    "date": "2025-01-06",
    "amount": 92.24,
    "category": "food",
    "description": "snacks"
  },
  {
    "id": "49755dfcec004e47a3c365969d054e78",
    "date": "2024-11-18",
    "amount": 12.49,
    "category": "food",
    "description": "restaurant"
  }
]
```

#### Summing Expenses by Category
#### Input:

```
{
  "category": "food"
}
```

#### Output:

```
{
  "total": 104.73
}
```

### Deployment
The application can be deployed on Vercel using the configuration in `vercel.json`.

Running the Application Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Set up the database by running the `ingest.py` script:
```
python ingest.py
```

3. Start the FastAPI application:
```
uvicorn main:app --reload
```

4. Access the application at `http://localhost:8000`

### Conclusion
This project provides a comprehensive system for managing expenses, including features for adding, searching, and analyzing expense data. The integration with LangChain allows for advanced processing of both text and image inputs.
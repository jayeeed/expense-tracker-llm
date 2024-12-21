json_schema = {
    "title": "ExpenseCreate",
    "description": "Schema for storing expense data",
    "type": "object",
    "properties": {
        "date": {"type": "string", "description": "Date of the expense."},
        "amount": {
            "type": "integer",
            "description": "Amount of the expense.",
        },
        "category": {
            "type": "string",
            "description": "Type of category for the expense.",
            "default": "General",
        },
        "description": {
            "type": "string",
            "description": "Short summary of the expense.",
            "default": "No description",
        },
    },
    "required": ["amount", "category"],
}

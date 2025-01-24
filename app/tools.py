image_tool = [
    {
        "type": "function",
        "function": {
            "name": "parse_expense_input",
            "description": "Extract total expense data from image of a receipt",
            "parameters": {
                "type": "object",
                "properties": [
                    {
                        "name": "date",
                        "type": "str",
                        "description": "Date of the expense",
                        "example": "2025-01-01",
                    },
                    {
                        "name": "amount",
                        "type": "int",
                        "description": "Amount spent",
                        "example": 101.69,
                    },
                    {
                        "name": "category",
                        "type": "str",
                        "description": "Category of the expense",
                        "example": "Food",
                    },
                    {
                        "name": "description",
                        "type": "str",
                        "description": "Description of the expense",
                        "example": "Lunch at McDonald's",
                    },
                ],
                "required": ["date, amount", "category, description"],
            },
        },
    }
]

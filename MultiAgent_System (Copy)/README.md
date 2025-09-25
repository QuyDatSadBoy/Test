# FastAPI Project Template 🚀

A modern, production-ready FastAPI template for building scalable APIs with clean architecture.

## Project Structure 📁
```
api-fastapi-template/
├── alembic/                # Database migrations
│   ├── versions/          # Migration versions
│   └── env.py            # Alembic environment configuration
├── api/
│   ├── main.py             # Main file
│   ├── core/             # Core functionality
│   │   ├── config.py     # Environment and app configuration
│   │   ├── database.py   # Database connection and sessions
│   │   ├── exceptions.py # Global exception handlers
│   │   ├── logging.py    # Logging configuration
│   │   └── middleware.py # Authentication and security
│   ├── src/
│   │   └── keywords/     # Keywords module
│   │       ├── models.py     # Database models
│   │       ├── repository.py # Data access layer
│   │       ├── routes.py     # API endpoints
│   │       ├── schemas.py    # Pydantic models
│   │       └── service.py    # Business logic
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── test_keywords/    # Keywords module tests
│   └── conftest.py      # Test configurations
└── requirements.txt      # Project dependencies
```

## Requirements 📋
- Python 3.8+
- PostgreSQL
- Conda (optional, for environment management)

## Setup and Installation 🛠️

### Using Conda (Recommended)

1. Create and activate a new conda environment:
```bash
conda create -n fastapi-env python=3.8
conda activate fastapi-env
```

2. Clone the repository:
```bash
git clone <repository-url>
cd api-fastapi-template
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Using Python venv

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup 🌍

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

## Running the Project 🚀

1. Start the application:
```bash
uvicorn api.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations 🔄

1. Initialize the database:
```bash
alembic upgrade head
```

2. Create a new migration:
```bash
alembic revision --autogenerate -m "your migration message"
```

## Testing 🧪

For detailed testing information, please refer to [tests/README.md](tests/README.md).

Quick test commands:
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=api tests/

# Run specific test file
pytest tests/test_keywords/test_keyword_crud.py
```

## Development Tools 🛠️

1. Install pre-commit hooks:
```bash
pre-commit install
```

2. Format code:
```bash
black .
isort .
```

## Creating New Modules 📦

To create a new module in the `src` folder, follow the comprehensive **Module Creation Template**:

### 📋 Quick Start
1. **Read the Template**: See [MODULE_CREATION_TEMPLATE.md](./MODULE_CREATION_TEMPLATE.md) for detailed guidelines
2. **Follow the Structure**: Use the established **Route → Service → Repository → Database** flow
3. **Check Examples**: Reference the `keywords` module in `api/src/keywords/` as a working example

### 🏗️ Basic Steps
1. Create a new directory in `api/src/`:
```bash
mkdir api/src/your_module
```

2. Create the following files in your module directory:
```bash
touch api/src/your_module/__init__.py
touch api/src/your_module/models.py      # Database models
touch api/src/your_module/repository.py  # Data access layer
touch api/src/your_module/routes.py      # API endpoints
touch api/src/your_module/schemas.py     # Pydantic models
touch api/src/your_module/service.py     # Business logic
```

3. **Follow the Template**: Use the detailed templates in [MODULE_CREATION_TEMPLATE.md](./MODULE_CREATION_TEMPLATE.md) for each file

4. Register your module's router in `api/main.py`:
```python
from api.src.your_module.routes import router as your_module_router

app.include_router(your_module_router)
```

5. Create tests for your module:
```bash
mkdir tests/test_your_module
touch tests/test_your_module/test_your_module_crud.py
```

### 🎯 Key Principles
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Use FastAPI's dependency injection system
- **Error Handling**: Implement proper exception handling
- **Documentation**: Add comprehensive docstrings and type hints
- **Testing**: Write unit tests for each layer

### 📚 Template Features
- Complete file templates for all layers
- Naming conventions and best practices
- Error handling patterns
- Performance optimization guidelines
- Security considerations
- Testing strategies
- Database migration guidelines

**For detailed implementation guidelines, see [MODULE_CREATION_TEMPLATE.md](./MODULE_CREATION_TEMPLATE.md)**

## API Documentation 📚

Once the application is running, you can access:
- Interactive API documentation (Swagger UI): http://localhost:8000/docs
- Alternative API documentation (ReDoc): http://localhost:8000/redoc

## Contributing 🤝

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request



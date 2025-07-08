# Tests

This folder contains all test files for the Library Management System.

## Test Files

- `test_app.py` - Main application tests ✅ (8 tests passing)
- `test_circulation_scanner.py` - Circulation and scanner functionality tests
- `test_edit_member.py` - Member editing functionality tests
- `test_member_lookup.py` - Member lookup functionality tests
- `test_server.py` - Server functionality tests
- `test_ssl.py` - SSL/HTTPS functionality tests

## Running Tests

### Run all tests:
```bash
python -m pytest tests/
```

### Run a specific test file:
```bash
python tests/test_app.py
```

### Run tests with verbose output:
```bash
python -m pytest tests/ -v
```

### Run tests with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

### Alternative: Run tests directly with Python
```bash
python tests/test_app.py
python tests/test_member_lookup.py
python tests/test_server.py
```

## Test Status

✅ **test_app.py**: All 8 tests passing
- Database isolation fixed with unique ISBNs and member IDs
- Proper session management implemented
- DetachedInstanceError resolved

## Test Dependencies

Make sure you have the following packages installed for running tests:
```bash
pip install pytest pytest-cov
```

## Notes

- All tests should be run from the root directory of the project
- Tests use isolated in-memory SQLite databases for each test method
- Unique test data is generated to avoid constraint violations
- Database cleanup is performed after each test
- If you see deprecation warnings, they are from SQLAlchemy and don't affect test results
- The tests validate API endpoints, database operations, and business logic

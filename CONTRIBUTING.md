# Contributing to ApproveHub

Thank you for your interest in contributing to **ApproveHub**. This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A GitHub account

### Setting Up the Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/<your-username>/ApproveHub.git
cd ApproveHub

# Create a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Initialise the development database
python init_db.py

# Start the development server
python app.py
```

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below.

3. **Run the test suite** to ensure nothing is broken:
   ```bash
   python -m unittest test_system_flow.py test_auth_and_pwa.py test_production_features.py
   ```

4. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "feat: add document expiry notification system"
   ```

5. **Push to your fork** and open a Pull Request against `main`.

## Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Purpose |
|:---|:---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `style:` | Code formatting (no logic changes) |
| `refactor:` | Code restructuring (no feature/fix) |
| `test:` | Adding or updating tests |
| `chore:` | Build process, dependency updates |

## Coding Standards

- **Python:** Follow PEP 8. Use type hints for function signatures. Add docstrings to all public functions and classes.
- **HTML/CSS:** Use semantic HTML5 elements. Follow the existing design system variables defined in `web/static/css/style.css`.
- **JavaScript:** Vanilla JS only (no frameworks). Use `const`/`let` (no `var`).
- **Security:** Never commit secrets, API keys, or credentials. Use environment variables for all sensitive configuration.

## Project Structure

| Directory | Purpose |
|:---|:---|
| `backend/routes/` | Flask Blueprint route handlers |
| `backend/utils/` | Shared utility modules (hashing, security, stamping) |
| `backend/models.py` | SQLAlchemy ORM model definitions |
| `web/templates/` | Jinja2 HTML templates |
| `web/static/` | CSS, JavaScript, images, PWA assets |

## Reporting Issues

When reporting bugs, please include:
- Steps to reproduce the issue
- Expected vs. actual behaviour
- Browser/device information (if UI-related)
- Relevant error messages or log output

## Contact

For questions about the project architecture or contribution guidelines, reach out to:

**Shreeyash Solunke** — Project Architect & Lead Developer  
Department of Information Technology, VIT Pune  
GitHub: [@ShreeyashSolunke08](https://github.com/ShreeyashSolunke08)

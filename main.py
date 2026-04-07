"""Main entry point for the NotebookUm Flask application using Granian server"""

import os
from app import create_app

# Create Flask application
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # Development mode: use Flask's built-in server
    # Production mode: use Granian (run with: granian --interface wsgi main:app)
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])

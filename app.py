import logging
from app import create_app
import os
# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
# os.environ['OPENAI_API_KEY'] = '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'
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5006)
import os
from waitress import serve
from api import create_app  # Import your app

# Run from the same directory as this script
this_files_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(this_files_dir)
app=create_app()

serve(app, host='127.0.0.1', port=4999, url_scheme='https')
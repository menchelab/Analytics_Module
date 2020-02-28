venv\Scripts\activate
pip install flask_cors
pip install pymysql
$env:FLASK_ENV="development"
$env:FLASK_APP="__init__.py"
flask run --port 1337
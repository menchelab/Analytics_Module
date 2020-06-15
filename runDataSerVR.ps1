$host.ui.RawUI.WindowTitle = 'DataSerVR'
$host.UI.RawUI.BackgroundColor='darkgray'

Clear-Host
venv\Scripts\activate
pip install flask_cors
pip install pymysql
$env:FLASK_ENV="development"
$env:FLASK_APP="app.py"
flask run --port 1337


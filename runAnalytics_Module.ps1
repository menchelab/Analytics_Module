$host.ui.RawUI.WindowTitle = 'DataSerVR'
$host.UI.RawUI.BackgroundColor='darkgray'

Clear-Host
#create virtual env in windows and activate it and install requirements.txt
py -3 -m venv venv
venv\Scripts\activate
#pip install flask_cors
#pip install pymysql
python -m pip install -r requirements.txt
$env:FLASK_ENV="development"
$env:FLASK_APP="app.py"
#flask run --port 1337
python app.py
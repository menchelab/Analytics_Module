# DataServer

*The DataServer is a flexible interface between the MySQL database
containing network data and the VR-based front end. It is implemented
in Flask, a minimalist Python-based framework for web development.*

# Installing and running locally (mac/linux/windows)

1. Make sure you are running Python 3 (we tested with 3.6 and up),
   preferably in a virtual environment. If using Windows check out the guide at: https://flask.palletsprojects.com/en/1.1.x/installation/ for instructions about how to get a virtualenv set up right.
1. Clone this repository `git clone git@github.com:menchelab/dataserver.git`
1. Navigate to the repo `cd dataserver`
1. Install dependencies `pip install -r requirements.txt`
1. Set your flask environment `export FLASK_APP=app` (note that you can
   also use app_lite if you don't want the API)
1. Optionally, configure it as a development environment, which would
   make the server reload with every code change. `export FLASK_ENV=development`
1. Configure your database file. To do this, copy db_config_template.py
   to db_config.py and fill in your database locations, usernames, and
   passwords.
1. Finally, spin up the server: `flask run`. The output message
   in the console will tell you the web address for the server,
   typically http://127.0.0.1:5000/.

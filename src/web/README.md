# Watson Besserwisserbot

## Development

Please keep the following things in mind:

* Create and commit migrations after the database scheme changed (e.g. model changes). `./manage.py makemigrations`
* From time to time, look for new versions of the dependencies, listed in `requirements.txt` and `bower.json`, test them and commit updated files.

### Install/run locally

* git clone THIS_REPO
* cd web
* virtualenv -p python3 venv
* source venv/bin/activate
* pip install -r requirements.txt
* ./manage.py migrate
* ./manage.py createsuperuser
* ./manage.py runserver


## Deployment

### Installation
* Install `python3`, `python3-pip`, `python3-virtualenv` and `bower` (the latter maybe via `npm`)
* Maybe create a user for Django/WSGI applications (e.g. `django`)
* Clone this repository into a proper directory (e.g. `/srv/web`)
* Maybe create MySQL database and proper user
* Create the file `web/settings_local.py` and fill it with production settings (it will be imported by `settings.py` and overrides default settings)
* Create a virtualenv (e.g. `virtualenv -p python3 venv`)
* For serving WSGI applications, one can install `uwsgi`, create an ini file under `/etc/uwsgi/` with the proper configuration (see `uwsgi.sample.ini`) and configure the webserver to use mod-proxy-uwsgi to make the application accessible. The webserver should also serve the static files.
* Run all the relevant commands from the Updates section

### Updates

* `systemctl stop uwsgi`
* `git pull`
* `bower install` when the `bower.json` file changed
* Install `grunt-cli` and `grunt-ts` in `bwb_webapp/static/bwb_webapp/script` if you want to edit the typescript sources
* `source venv/bin/activate` when one of the `pip` or `./manage.py` steps are necessary
* `pip install -r requirements.txt` when the `requirements.txt` file changed
* `./manage.py migrate` when a new migrations file is available
* `./manage.py collectstatic` when a static file changed (or `bower install` was run)
* `deactivate` when virtualenv was activated
* `chown -R django:django .`
* `systemctl start uwsgi`

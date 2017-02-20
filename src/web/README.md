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
* script/update
* ./manage.py createsuperuser
* ./manage.py runserver


## Deployment

### Using Docker

Create a `web/settings_local.py` file and fill it with your settings.

You can build an image of the web application using the `Dockerfile`.

To bring up the whole project, you can use `docker-compose` from within the top level `src` folder.

### Manually

#### Installation
* Install `python3`, `python3-pip`, `python3-virtualenv` and `bower` (the latter maybe via `npm`)
* Maybe create a user for Django/WSGI applications (e.g. `django`)
* Clone this repository into a proper directory (e.g. `/srv/web`)
* Maybe create MySQL database and proper user
* Create the file `web/settings_local.py` and fill it with production settings (it will be imported by `settings.py` and overrides default settings)
* Create a virtualenv (e.g. `virtualenv -p python3 venv`)
* For serving WSGI applications, one can install `uwsgi`, create an ini file under `/etc/uwsgi/` with the proper configuration (see `uwsgi.sample.ini`) and configure the webserver to use mod-proxy-uwsgi to make the application accessible. The webserver should also serve the static files.
* Run all the relevant commands from the Updates section

#### Updates

* `git pull`
* Install `grunt-cli` and `grunt-ts` in `bwb_webapp/static/bwb_webapp/script` if you want to edit the typescript sources
* `source venv/bin/activate`
* `script/update --prod`
* `deactivate`

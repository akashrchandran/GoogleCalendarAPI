# Google Calendar API
It used OAUTH to get acess to your google account and get information about your events and return them as json.

## Get client_secret.json
To get client_secret.json you need to go to [Google API Console](https://console.developers.google.com/apis/dashboard) and create a new project. Then you need to enable Google Calendar API and create credentials. After that you will be able to download client_secret.json.

## How to use

- Clone it and run `pip install -r requirements.txt` to install all dependencies.
- Run `python manage.py runserver` to start the server.

## Endpoints

Go to `http://127.0.0.1:8000/rest/v1/calendar/init/` and authorize with your google account. After that you will be redirected.

A page containing `'upcoming_events'` and `'all_events'` will be displayed containing all your events in json format.
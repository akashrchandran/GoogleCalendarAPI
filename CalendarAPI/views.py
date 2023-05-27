from datetime import datetime, timezone
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from  google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# google credentials file name
CRED_FILE = 'client_secret.json'
# google calendar scope
SCOPE = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI  = '/rest/v1/calendar/redirect/'


def GoogleCalendarInitView(request):
    # Initialize authorization flow
    if not os.path.exists(CRED_FILE):
        return HttpResponse("Please download client_secret.json file from google developer console and place it in project root directory")
    flow = Flow.from_client_secrets_file(CRED_FILE, scopes=SCOPE)
    flow.redirect_uri = f"http://{request.get_host()}{REDIRECT_URI}"
    authorization_url, state = flow.authorization_url()
    # state is used to prevent CSRF, keep this for later.
    request.session['state'] = state
    # redirect to google authorization url
    return redirect(authorization_url)

def GoogleCalendarRedirectView(request):
    # get state from session
    state = request.session.get('state')
    # check if state is None
    if state is None:
        return redirect('/rest/v1/calendar/init/')
    # Initialize authorization flow and this time with state
    flow = Flow.from_client_secrets_file(CRED_FILE, scopes=SCOPE, state=state)
    flow.redirect_uri = REDIRECT_URI
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    # build google calendar service
    try:
        # return events
        return get_events(credentials)
    except HttpError as err:
        # return error
        return JsonResponse({'error': err._get_reason()})


def get_events(credentials):
    service = build('calendar', 'v3', credentials=credentials)
    # get all events
    all_events_result = service.events().list(calendarId='primary').execute()
    all_events = all_events_result.get('items', [])
    now = datetime.now(timezone.utc).isoformat()
    # get upcoming events by passing minimum time as now
    upcoming_events_result = service.events().list(calendarId='primary',timeMin=now,singleEvents=True,orderBy='startTime').execute()
    upcoming_events = upcoming_events_result.get('items', [])
    # return upcoming events and all events
    return JsonResponse({'upcoming_events': upcoming_events, 'all_events': all_events})

def HomePage(request):
    return HttpResponse("<h1>Home Page</h1>Authorize to access <a href='/rest/v1/calendar/init/'>Google Calendar</a>")
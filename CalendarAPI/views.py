import os
from datetime import datetime, timezone

from django.http import HttpResponse
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework.decorators import api_view
from rest_framework.response import Response

# google credentials file name
CRED_FILE = 'client_secret.json'
# google calendar scope
SCOPE = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI  = "http://localhost:8000/rest/v1/calendar/redirect/"

@api_view(['GET'])
def GoogleCalendarInitView(request):
    # Initialize authorization flow
    if not os.path.exists(CRED_FILE):
        return Response("Please download client_secret.json file from google developer console and place it in project root directory")
    flow = Flow.from_client_secrets_file(CRED_FILE, scopes=SCOPE)
    flow.redirect_uri = REDIRECT_URI
    print(flow.redirect_uri)
    authorization_url, state = flow.authorization_url()
    # state is used to prevent CSRF, keep this for later.
    request.session['state'] = state
    # redirect to google authorization url
    return redirect(authorization_url)

@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    # get state from session
    state = request.session.get('state')
    try:
        # Initialize authorization flow and this time with state
        flow = Flow.from_client_secrets_file(CRED_FILE, scopes=SCOPE, state=state)
        flow.redirect_uri = REDIRECT_URI
        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        # return events
        return get_events(credentials)
    except HttpError as err:
        # return error
        return Response({'error': err._get_reason()})

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
    return Response({'upcoming_events': upcoming_events, 'all_events': all_events})

def HomePage(request):
    return HttpResponse("<h1>Home Page</h1>Authorize to access <a href='/rest/v1/calendar/init/'>Google Calendar</a>")
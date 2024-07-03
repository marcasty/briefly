import sys
from datetime import datetime
sys.path.append('..')
from .gmail import get_google_api_service  # Changed to absolute import

DEBUG = 1

async def get_today_events():
    service = get_google_api_service("calendar", "v3")
    
    # Get the start and end of today
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
    end = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
    
    events_result = service.events().list(calendarId='primary', timeMin=start, timeMax=end,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    today_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        today_events.append({
            'summary': event['summary'],
            'start': start,
            'end': end,
            'description': event.get('description', 'No description'),
            'location': event.get('location', 'No location')
        })
    
    if DEBUG >= 1:
        print(f"Found {len(events)} events for today.", flush=True)
        for event in today_events:
            print(f"Summary: {event['summary']}", flush=True)
            print(f"Start: {event['start']}", flush=True)
            print(f"End: {event['end']}", flush=True)
            print(f"Description: {event['description']}", flush=True)
            print(f"Location: {event['location']}", flush=True)
            print("---", flush=True)
    
    return today_events

if __name__ == '__main__':
    events = get_today_events()
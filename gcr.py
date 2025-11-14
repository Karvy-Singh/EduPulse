import os
import json
import time
import pickle
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly"
]

TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'
STATE_FILE = 'classroom_state.json'
POLL_INTERVAL = 300  # seconds between checks

def authenticate():
    """Authenticate and return the Classroom API service."""
    creds = None
    
    # Load existing credentials
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('classroom', 'v1', credentials=creds)

def load_state():
    """Load the last known state (timestamps of last seen items)."""
    if not os.path.exists(STATE_FILE):
        return {}
    
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save the current state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def iso_to_timestamp(iso_string):
    """Convert ISO format timestamp to comparable format."""
    if not iso_string:
        return None
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.timestamp()
    except:
        return None

def check_announcements(service, course_id, last_timestamp):
    """Check for new announcements in a course."""
    new_items = []
    
    try:
        results = service.courses().announcements().list(
            courseId=course_id,
            orderBy='updateTime desc',
            pageSize=10
        ).execute()
        
        announcements = results.get('announcements', [])
        
        for announcement in announcements:
            update_time = iso_to_timestamp(announcement.get('updateTime'))
            
            if not last_timestamp or (update_time and update_time > last_timestamp):
                new_items.append({
                    'type': 'announcement',
                    'id': announcement.get('id'),
                    'text': announcement.get('text', 'No text'),
                    'creatorUserId': announcement.get('creatorUserId'),
                    'creationTime': announcement.get('creationTime'),
                    'updateTime': announcement.get('updateTime')
                })
    
    except HttpError as error:
        print(f"Error fetching announcements: {error}")
    
    return new_items

def check_coursework(service, course_id, last_timestamp):
    """Check for new coursework/assignments in a course."""
    new_items = []
    
    try:
        results = service.courses().courseWork().list(
            courseId=course_id,
            orderBy='updateTime desc',
            pageSize=10
        ).execute()
        
        coursework = results.get('courseWork', [])
        
        for work in coursework:
            update_time = iso_to_timestamp(work.get('updateTime'))
            
            if not last_timestamp or (update_time and update_time > last_timestamp):
                new_items.append({
                    'type': 'coursework',
                    'id': work.get('id'),
                    'title': work.get('title', 'No title'),
                    'description': work.get('description', 'No description'),
                    'dueDate': work.get('dueDate'),
                    'dueTime': work.get('dueTime'),
                    'creationTime': work.get('creationTime'),
                    'updateTime': work.get('updateTime')
                })
    
    except HttpError as error:
        print(f"Error fetching coursework: {error}")
    
    return new_items

def format_due_date(due_date, due_time):
    """Format due date and time nicely."""
    if not due_date:
        return "No due date"
    
    date_str = f"{due_date.get('year')}-{due_date.get('month'):02d}-{due_date.get('day'):02d}"
    
    if due_time:
        hours = due_time.get('hours', 0)
        minutes = due_time.get('minutes', 0)
        time_str = f" at {hours:02d}:{minutes:02d}"
    else:
        time_str = ""
    
    return date_str + time_str

def check_classroom_updates():
    """Main function to check for new classroom activities."""
    service = authenticate()
    state = load_state()
    
    # Get all courses
    try:
        results = service.courses().list(pageSize=100).execute()
        courses = results.get('courses', [])
        
        if not courses:
            print("No courses found.")
            return
        
        print(f"Checking {len(courses)} courses for updates...")
        
        new_state = state.copy()
        any_updates = False
        
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            
            # Initialize state for new courses
            if course_id not in state:
                state[course_id] = {
                    'last_announcement_check': None,
                    'last_coursework_check': None
                }
            
            # Check announcements
            last_announcement_time = state[course_id].get('last_announcement_check')
            announcements = check_announcements(service, course_id, last_announcement_time)
            
            if announcements:
                any_updates = True
                print("=" * 70)
                print(f"📢 NEW ANNOUNCEMENTS in {course_name}")
                print("=" * 70)
                
                for ann in announcements:
                    print(f"Time: {ann['creationTime']}")
                    print(f"Text: {ann['text'][:200]}...")
                    print("-" * 70)
                
                # Update timestamp
                latest_time = max(iso_to_timestamp(a['updateTime']) for a in announcements)
                new_state[course_id]['last_announcement_check'] = latest_time
            
            # Check coursework
            last_coursework_time = state[course_id].get('last_coursework_check')
            coursework = check_coursework(service, course_id, last_coursework_time)
            
            if coursework:
                any_updates = True
                print("=" * 70)
                print(f"📝 NEW COURSEWORK in {course_name}")
                print("=" * 70)
                
                for work in coursework:
                    print(f"Title: {work['title']}")
                    print(f"Description: {work['description'][:200]}...")
                    print(f"Due: {format_due_date(work.get('dueDate'), work.get('dueTime'))}")
                    print(f"Posted: {work['creationTime']}")
                    print("-" * 70)
                
                # Update timestamp
                latest_time = max(iso_to_timestamp(w['updateTime']) for w in coursework)
                new_state[course_id]['last_coursework_check'] = latest_time
        
        if not any_updates:
            print("No new updates found.")
        
        # Save updated state
        save_state(new_state)
    
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    print("Google Classroom Monitor Starting...")
    print(f"Will check for updates every {POLL_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    # First run authentication
    try:
        authenticate()
        print("Authentication successful!\n")
    except Exception as e:
        print(f"Authentication failed: {e}")
        exit(1)
    
    while True:
        try:
            check_classroom_updates()
            print(f"\nNext check in {POLL_INTERVAL} seconds...\n")
        except KeyboardInterrupt:
            print("\nMonitor stopped by user.")
            break
        except Exception as e:
            print(f"Error during check: {e}")
        
        time.sleep(POLL_INTERVAL)

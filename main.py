import argparse
from datetime import date, timedelta
import os
import requests

# helper classes
from classcharts_helper import ClassChartsSession, ClassChartsStudent

API_URL = os.getenv("api_url", "")

def _get_activity(session_id, student_id, days=90):
    """Get student activity."""
    today = date.today()
    from_date = today - timedelta(days=days)
    url = f"{API_URL}/activity/{student_id}/?from={from_date}&to={today}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        print(f"Activity: {response.json()}")

def _get_behaviour(session_id, student_id, days=90):
    """Get student behaviour."""
    today = date.today()
    from_date = today - timedelta(days=days)
    url = f"{API_URL}/behaviour/{student_id}/?from={from_date}&to={today}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        print(f"Behaviour: {response.json()}")

def _get_homework(session_id, student_id, display_date, days):
    """Get student homework."""
    today = date.today()
    from_date = today - timedelta(days=days)
    url = f"{API_URL}/homeworks/{student_id}/?display_date={display_date}&from={from_date}&to={today}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        print(f"Homework: {response.json()}")

def _get_students(session_id, all):
    """Get all students."""
    url = f"{API_URL}/pupils"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    students = []
    for student in response.json()['data']:
        students.append(ClassChartsStudent(**student))
    if all:
        return students
    else:
        print("Select a pupil to view:")
        for idx, student in enumerate(students, start=1):
            print(f"#{idx}: {student.first_name} {student.last_name} ({student.school_name})")
        input_student = int(input("Enter the number of the pupil you want to view\n"))
        return ClassChartsStudent(**response.json()['data'][input_student - 1])

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Probe for ClassCharts data')
    subparsers = parser.add_subparsers(dest='func', help='description')
    # create the parser for the "activity" command
    parser_activity = subparsers.add_parser('activity', help='get activity for the last n days (default 30)')
    parser_activity.add_argument('--days', type=int, default=30, required=False)
    # create the parser for the "behaviour" command
    parser_behaviour = subparsers.add_parser('behaviour', help='get behaviour for the last n days (default 30)')
    parser_behaviour.add_argument('--days', type=int, default=30, required=False)
    # create the parser for the "homework" command
    parser_homework = subparsers.add_parser('homework', help='get homework for the last n days (default 30)')
    parser_homework.add_argument('--days', type=int, default=30, required=False)
    parser_homework.add_argument('--display_date', type=str, default='issue_date', choices=['issue_date', 'due_date'])
    # parse the args
    return parser.parse_args(args)

def main():
    """ClassCharts API main function."""
    all = False
    args = parse_args()

    cs = ClassChartsSession()
    print(f"Attempting to log in as {cs.username}...")
    cs_session = cs.login()

    if cs_session['success'] == 1:
        print(f"Hello {cs_session['data']['name']}! You have successfully logged in to ClassCharts.")
        print(f"Your session ID is {cs.session_id}")
        print()
    else:
        print("Login failed. Please check your credentials and try again.")
        return

    if args.func == None:
        all = True

    students = _get_students(cs.session_id, all)

    if args.func == None:
        """List pupils."""
        print("Listing all pupils for this account...")
        if students:
            for student in students:
                print("-" * len("Listing all pupils for this account..."))
                print()
                print(f"Name: {student.first_name} {student.last_name} ({student.school_name} - {student.id})")
                if student.display_homework:
                    print(f"Homework: submitted: {student.homework_submitted_count}, to do: {student.homework_todo_count}, excused: {student.homework_excused_count}, late: {student.homework_late_count}, completed: {student.homework_completed_count}, not completed: {student.homework_not_completed_count}")
                if student.display_detentions:
                    print(f"Detentions pending: {student.detention_pending_count} (total this term: {student.detention_yes_count})")
                    print()
                #print()
                return
    print(f"Selected pupil: {students}, ID: {students.id} ({students.school_name})")

    if args.func == 'activity':
        _get_activity(cs.session_id, students.id, days=args.days)
    if args.func == 'behaviour':
        _get_behaviour(cs.session_id, students.id, days=args.days)
    if args.func == 'homework':
        _get_homework(cs.session_id, students.id, display_date=args.display_date, days=args.days)

if __name__ == '__main__':
    main()
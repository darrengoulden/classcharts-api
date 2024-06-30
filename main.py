import argparse
from datetime import datetime, date, timedelta
from lxml import html
import os
import requests

# helper classes
from classcharts import Session, Student, Homework, Timetable

API_URL = os.getenv("api_url", "")

def _tabulate(data):
    """Tabulate data - data is an array (rows) or arrays (columns)"""
    lengths = [0] * len(data[0])
    for row in data:
        for ind in range(len(row)):
            if len(str(row[ind])) > lengths[ind]:
                lengths[ind] = len(str(row[ind]))
    for row in data:
        for ind in range(len(row)):
            print(str(row[ind]), end=" ")
            print(" " * (lengths[ind] - len(str(row[ind]))), end=" ")
        print("")

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

def _get_homework(session_id, student_id, display_type, days, index=None):
    """Get student homework."""
    today = date.today()
    from_date = today - timedelta(days=days)
    url = f"{API_URL}/homeworks/{student_id}/?display_date={display_type}&from={from_date}&to={today}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        header = ['Number', 'Title', 'Subject', 'Lesson', 'Teacher', 'Due Date', 'Estimated Completion Time', 'Status']
        homework_assignment_data = [header]
        homework_assignments = []
        for assignment in response.json()['data']:
            homework_assignments.append(Homework(**assignment))
        if index:
            homework = homework_assignments[index - 1]
            est_time = f"{homework.completion_time_value} {homework.completion_time_unit}"
            print(f"Selected homework assignment: {index}")
            print()
            print(f"Title: {homework.title}")
            print(f"Subject: {homework.subject}")
            print(f"Lesson: {homework.lesson}")
            print(f"Teacher: {homework.teacher}")
            print(f"Due Date: {homework.due_date}")
            print(f"Estimated Completion Time: {homework.completion_time_value} {homework.completion_time_unit}") if homework.completion_time_value else print(f"Estimated Completion Time: n/a")
            print(f"Status: {homework.status['state']}")
            print(f"Description: {html.fromstring(homework.description).text_content()}")
            return
        for idx, assignment in enumerate(sorted(homework_assignments, key=lambda homework_assignments:homework_assignments.due_date), start=1):
            if assignment.homework_type == 'Homework':
                est_time = f"{assignment.completion_time_value} {assignment.completion_time_unit}"
                hw = [idx, assignment.title, assignment.subject, assignment.lesson, assignment.teacher, assignment.due_date, est_time if assignment.completion_time_value else 'n/a', assignment.status['state']]
            homework_assignment_data.append(hw)
        _tabulate(homework_assignment_data)
        print()
        print(f"Assignments due this week: {response.json()['meta']['this_week_due_count']}")
        print(f"Assignments completed this week: {response.json()['meta']['this_week_completed_count']}")
        print(f"Assignments outstanding this week: {response.json()['meta']['this_week_outstanding_count']}")

def _get_classes(session_id, student_id):
    """Get all classes."""
    url = f"{API_URL}/classes/{student_id}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        print(f"Classes: {response.json()}")
    else:
        print("No classes found.")
        print(response.json()['error'])

def _get_timetable(session_id, student_id, date_required=date.today()):
    """Get timetable."""
    url = f"{API_URL}/timetable/{student_id}/?date={date_required}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    # get all timetable dates
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        timetable_dates = []
        timetable_day_data = []
        period_data = {}
        for date in response.json()['meta']['timetable_dates']:
            timetable_dates.append(date)
        for day in timetable_dates:
            try:
                url = f"{API_URL}/timetable/{student_id}/?date={day}"
                response = requests.get(url, headers=header)
                response.raise_for_status()
                for lessons in response.json()['data']:
                    timetable_day_data.append(Timetable(**lessons))
                for period in response.json()['meta']['periods']:
                    period_data[period['number']] = [period['start_time'], period['end_time']]
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
        timetable_header = ['Date', 'Teacher', 'Lesson Name', 'Subject', 'Period Number', 'Room Name', 'Start Time', 'End Time']
        timetable_data = [timetable_header]
        timetable_data.append(["-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10])
        for timetable_day in timetable_day_data:
            if timetable_day.period_number in period_data:
                timetable_day.start_time = period_data[timetable_day.period_number][0]
                timetable_day.end_time = period_data[timetable_day.period_number][1]
            timetable_data.append([timetable_day.date, timetable_day.teacher_name, timetable_day.lesson_name, timetable_day.subject_name, timetable_day.period_number, timetable_day.room_name, timetable_day.start_time, timetable_day.end_time])
            if timetable_day.period_number == '5':
                timetable_data.append(["-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10, "-" * 10])        
        _tabulate(timetable_data)
        print()
    else:
        print("No timetable found.")
        print(response.json()['error'])

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
        students.append(Student(**student))
    if all:
        return students
    else:
        print("Select a pupil to view:")
        for idx, student in enumerate(students, start=1):
            print(f"#{idx}: {student.first_name} {student.last_name} ({student.school_name})")
        input_student = int(input("Enter the number of the pupil you want to view\n"))
        return Student(**response.json()['data'][input_student - 1])

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
    parser_homework.add_argument('--number', type=int, required=False)
    # create the parser for the "classes" command
    parser_classes = subparsers.add_parser('classes', help='get classes')
    # create the parser for the "timetable" command
    parser_timetable = subparsers.add_parser('timetable', help='get timetable')
    parser_timetable.add_argument('--date', type=lambda d: datetime.strptime(d, '%Y-%m-%d'), default=date.today(), required=False)
    # parse the args
    return parser.parse_args(args)

def main():
    """ClassCharts API main function."""
    all = False
    args = parse_args()

    cs = Session()
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
                return
    print(f"Selected pupil: {students}, ID: {students.id} ({students.school_name})")
    print()

    if args.func == 'activity':
        _get_activity(cs.session_id, students.id, days=args.days)
    if args.func == 'behaviour':
        _get_behaviour(cs.session_id, students.id, days=args.days)
    if args.func == 'homework':
        _get_homework(cs.session_id, students.id, display_type=args.display_date, days=args.days, index=args.number)
    if args.func == 'classes':
        _get_classes(cs.session_id, students.id)
    if args.func == 'timetable':
        _get_timetable(cs.session_id, students.id, date_required=args.date)

if __name__ == '__main__':
    main()

import argparse
import csv
from datetime import datetime, date, timedelta
from lxml import html
import os
import requests

# helper classes
from classcharts import AttendanceData, AttendanceMeta, Announcements, Detentions, Homework, Session, Student, Timetable

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

def _get_badges(session_id, student_id):
    """Get badges."""
    url = f"{API_URL}/eventbadges/{student_id}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        if response.json()['data']:
            print(f"Badges: {response.json()}")
        else:
            print("No badges found.")
            
def _get_announcements(session_id, student_id):
    """Get announcements."""
    url = f"{API_URL}/announcements/{student_id}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        announcements = []
        for announcement in response.json()['data']:
            announcements.append(Announcements(**announcement))
        for announcement in announcements:
            print(f"Title: {announcement.title} ({announcement.teacher_name})")
            print(f"Date: {announcement.timestamp}")
            print(f"Requires consent: {announcement.requires_consent}")
            print("-" * len(f"Date: {announcement.timestamp}"))
            print(f"Description: {html.fromstring(announcement.description).text_content()}")
            print("-" * len(f"Date: {announcement.timestamp}"))
            print(f"Attachments - Filename: {announcement.attachments[0]['filename']}, URL: {announcement.attachments[0]['url']}") if announcement.attachments else print("Attachments: None")
            print()

def _get_detentions(session_id, student_id, save_csv=False):
    """Get detentions."""
    url = f"{API_URL}/detentions/{student_id}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    if response.json()['success'] == 1:
        csv_file = 'detentions.csv'
        detentions = []
        for detention in response.json()['data']:
            detentions.append(Detentions(**detention))
        detention_header = ['Date', 'Time', 'Length', 'Location', 'Lesson', 'Type', 'Teacher', 'Notes']
        detention_data = [detention_header]
        if save_csv:
            with open(csv_file, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(detention_header)
                for detention in detentions:
                    if detention.lesson:
                        lesson = f"{detention.lesson['subject']['name']}"
                    else:
                        lesson = "N/A"
                    if detention.teacher:
                        teacher = f"{detention.teacher['title']} {detention.teacher['first_name']} {detention.teacher['last_name']}"
                    else:
                        teacher = "N/A"
                    csv_writer.writerow([detention.date, detention.time, detention.length, detention.location, lesson, detention.detention_type['name'], teacher, detention.notes])
            print(f"Detentions saved to {csv_file}")
            return
        for detention in detentions:
            if detention.lesson:
                lesson = f"{detention.lesson['name']} ({detention.lesson['subject']['name']})"
            else:
                lesson = "N/A"
            if detention.teacher:
                teacher = f"{detention.teacher['title']} {detention.teacher['first_name']} {detention.teacher['last_name']}"
            else:
                teacher = "N/A"
            detention_data.append([detention.date, detention.time, detention.length, detention.location, lesson, detention.detention_type['name'], teacher, detention.notes])
        _tabulate(detention_data)
        print()

def _get_attendance(session_id, student_id, days):
    """Get attendance."""
    today = date.today()
    from_date = today - timedelta(days=days)
    url = f"{API_URL}/attendance/{student_id}?from={from_date}&to={today}"
    header = {'Content-Type' : 'application/json', 'Authorization': f'Basic {session_id}'}
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    # attenfance meta data
    attendance_meta = AttendanceMeta(**response.json()['meta'])
    # attendance data
    attendance_data = []
    attendance_data_complete = {}
    if response.json()['success'] == 1:
        attendance_data.append(response.json()['data'])
    for attendance_date in attendance_meta.dates:
        for attendance_session in attendance_data[0][attendance_date]:
            session_data = AttendanceData(**attendance_data[0][attendance_date][attendance_session])
            attendance_data_complete[attendance_date] = session_data
    data_properties = {
        'yes': 0,
        'present': 0,
        'ignore': 0,
        'no': 0,
        'absent': 0,
        'excused': 0,
        'late': 0
    }
    late_minutes = 0
    for school_day_data in attendance_data_complete.values():
        if school_day_data.status == 'yes':
            data_properties['yes'] += 1
        if school_day_data.status == 'present':
            data_properties['present'] += 1
        if school_day_data.status == 'ignore':
            data_properties['ignore'] += 1
        if school_day_data.status == 'no':
            data_properties['no'] += 1
        if school_day_data.status == 'absent':
            data_properties['absent'] += 1
        if school_day_data.status == 'excused':
            data_properties['excused'] += 1
        if school_day_data.status == 'late':
            data_properties['late'] += 1
            late_minutes += school_day_data.late_minutes
    print(f"Attendance data for range: {attendance_meta.start_date.split("T")[0]}-{attendance_meta.end_date.split("T")[0]}")
    print()
    print(f"Total days present: {data_properties['present']}")
    print(f"Total days absent: {data_properties['absent']}")
    print(f"Total days excused: {data_properties['excused']}")
    print(f"Total days ignored: {data_properties['ignore']}")
    print(f"Total days late: {data_properties['late']}")
    print(f"Total minutes late: {late_minutes}") if late_minutes > 0 else print()
    print(f"Total days: {sum(x for x in data_properties.values() if x > 0)}")
    print()
    print(f"Percentage attendance of date range: {attendance_meta.percentage}%")
    print(f"Percentage attendance since August: {attendance_meta.percentage_since_august}%")
    print()

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
    # create the parser for the "badges" command
    parser_badges = subparsers.add_parser('badges', help='get badges')
    # create the parser for the "annoucements" command
    parser_announcements = subparsers.add_parser('announcements', help='get announcements')
    # create the parser for the "detentions" command
    parser_detentions = subparsers.add_parser('detentions', help='get detentions')
    parser_detentions.add_argument('--csv', type=bool, required=False)
    # create the parser for the "attendance" command
    parser_attendance = subparsers.add_parser('attendance', help='get attendance')
    parser_attendance.add_argument('--days', type=int, default=30, required=False)
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
    if args.func == 'announcements':
        _get_announcements(cs.session_id, students.id)
    if args.func == 'attendance':
        _get_attendance(cs.session_id, students.id, days=args.days)
    if args.func == 'badges':
        _get_badges(cs.session_id, students.id)
    if args.func == 'behaviour':
        _get_behaviour(cs.session_id, students.id, days=args.days)
    if args.func == 'classes':
        _get_classes(cs.session_id, students.id)
    if args.func == 'detentions':
        _get_detentions(cs.session_id, students.id, save_csv=args.csv)
    if args.func == 'homework':
        _get_homework(cs.session_id, students.id, display_type=args.display_date, days=args.days, index=args.number)
    if args.func == 'timetable':
        _get_timetable(cs.session_id, students.id, date_required=args.date)

if __name__ == '__main__':
    main()

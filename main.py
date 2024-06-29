import click
import os
import requests

API_URL = "https://www.classcharts.com/apiv2parent"


class ClassChartsStudent:
    """ClassCharts student class."""
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.avatar_url = kwargs.get("avatar_url")
        self.has_birthday = kwargs.get("has_birthday")
        self.is_disabled = kwargs.get("is_disabled")
        self.school_name = kwargs.get("school_name")
        self.school_logo = kwargs.get("school_logo")
        self.timezone = kwargs.get("timezone")
        self.display_homework = kwargs.get("display_homework")
        self.display_rewards = kwargs.get("display_rewards")
        self.display_behaviour = kwargs.get("display_behaviour")
        self.display_parent_behaviour = kwargs.get("display_parent_behaviour")
        self.display_detentions = kwargs.get("display_detentions")
        self.display_report_cards = kwargs.get("display_report_cards")
        self.display_classes = kwargs.get("display_classes")
        self.display_attendance = kwargs.get("display_attendance")
        self.display_attendance_type = kwargs.get("display_attendance_type")
        self.display_attendance_percentage = kwargs.get("display_attendance_percentage")
        self.display_announcements = kwargs.get("display_announcements")
        self.display_academic_reports = kwargs.get("display_academic_reports")
        self.display_activity = kwargs.get("display_activity")
        self.display_activity_detentions = kwargs.get("display_activity_detentions")
        self.display_timetable = kwargs.get("display_timetable")
        self.display_mental_health = kwargs.get("display_mental_health")
        self.display_two_way_communications = kwargs.get("display_two_way_communications")
        self.display_absences = kwargs.get("display_absences")
        self.display_mental_health_no_tracker = kwargs.get("display_mental_health_no_tracker")
        self.can_upload_attachments = kwargs.get("can_upload_attachments")
        self.display_event_badges = kwargs.get("display_event_badges")
        self.display_avatars = kwargs.get("display_avatars")
        self.display_concern_submission = kwargs.get("display_concern_submission")
        self.display_custom_fields = kwargs.get("display_custom_fields")
        self.display_covid_tests = kwargs.get("display_covid_tests")
        self.can_record_covid_tests = kwargs.get("can_record_covid_tests")
        self.detention_yes_count = kwargs.get("detention_yes_count")
        self.detention_no_count = kwargs.get("detention_no_count")
        self.detention_pending_count = kwargs.get("detention_pending_count")
        self.detention_upscaled_count = kwargs.get("detention_upscaled_count")
        self.homework_todo_count = kwargs.get("homework_todo_count")
        self.homework_late_count = kwargs.get("homework_late_count")
        self.homework_not_completed_count = kwargs.get("homework_not_completed_count")
        self.homework_excused_count = kwargs.get("homework_excused_count")
        self.homework_completed_count = kwargs.get("homework_completed_count")
        self.homework_submitted_count = kwargs.get("homework_submitted_count")
        self.announcements_count = kwargs.get("announcements_count")
        self.messages_count = kwargs.get("messages_count")
        self.pusher_channel_name = kwargs.get("pusher_channel_name")
        self.name = kwargs.get("name")
        self.detention_alias_plural_uc = kwargs.get("detention_alias_plural_uc")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClassChartsSession:
    """ClassCharts session class."""
    def __init__(self):
        self.username = os.getenv("email", "")
        self.password = os.getenv("password", "")
        self.session_id = None
        self.success = 0

    def login(self):
        """Login to ClassCharts and get an Accces token (session_id)."""
        url = f"{API_URL}/login"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'} 
        data = {
            "email": self.username,
            "password": self.password
        }
        try:
            response = requests.post(url, data=data, headers=header)
            response.raise_for_status()
            if response.json()['success'] == 1:
                self.session_id = response.json()['meta']['session_id']
                self.success = response.json()['success']
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        
    def ping(self):
        """Refresh ClassCharts login session_id.
        Access tokens should be refreshed every 180 seconds."""
        url = f"{API_URL}/ping"
        header = {'Content-Type' : 'application/x-www-form-urlencoded', 'Authorization': f'Basic {self.session_id}'}
        data = {
            "include_data": True
        }
        try:
            response = requests.post(url, data=data, headers=header)
            response.raise_for_status()
            if response.json()['success'] == 1:
                self.session_id = response.json()['meta']['session_id']
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)


def _get_students(session_id, listall):
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
    if listall:
        return students
    else:
        click.echo("Select a pupil to view:")
        for idx, student in enumerate(students, start=1):
            click.echo(f"#{idx}: {student.first_name} {student.last_name} ({student.school_name})")
        input_student = click.prompt("Enter the number of the pupil you want to view", type=int)
        return ClassChartsStudent(**response.json()['data'][input_student - 1])

@click.command()
@click.option("--listall", is_flag=True, help="List all pupils.")
def main(listall):
    """ClassCharts CLI."""
    cs = ClassChartsSession()
    click.echo(f"Attempting to log in as {cs.username}...")
    cs_session = cs.login()

    if cs_session['success'] == 1:
        click.echo(f"Hello {cs_session['data']['name']}! You have successfully logged in to ClassCharts.")
        click.echo(f"Your session ID is {cs.session_id}")
    else:
        click.echo("Login failed. Please check your credentials and try again.")
        return

    students = _get_students(cs.session_id, listall)

    if listall:
        """List pupils."""
        click.echo("Listing all pupils for this account...")
        if students:
            for student in students:
                click.echo("-" * len("Listing all pupils for this account..."))
                click.echo(f"Name: {student.first_name} {student.last_name} ({student.id})")
                click.echo(f"School: {student.school_name}")
                click.echo("-" * len(f"School: {student.school_name}"))
                if student.display_homework:
                    click.echo(f"Homework submitted: {student.homework_submitted_count}")
                    click.echo(f"Homework to do: {student.homework_todo_count}")
                    click.echo(f"Homework excused: {student.homework_excused_count}")
                    click.echo(f"Homework late: {student.homework_late_count}")
                    click.echo(f"Homework completed: {student.homework_completed_count}")
                    click.echo(f"Homework not completed: {student.homework_not_completed_count}")
                    click.echo("-" * len(f"Homework not completed: {student.homework_not_completed_count}"))
                if student.display_detentions:
                    click.echo(f"Detentions pending: {student.detention_pending_count}")
                    click.echo(f"Detentions this term: {student.detention_yes_count}")
                    click.echo("-" * len(f"Detentions this term: {student.detention_yes_count}"))
                click.echo("")
                return
    print(students.id)

if __name__ == '__main__':
    main()
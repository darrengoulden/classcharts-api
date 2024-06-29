"""ClassCharts helper module."""

import os
import requests


class Session():
    """ClassCharts session class."""
    def __init__(self):
        self.api_url = os.getenv("api_url", "")
        self.username = os.getenv("email", "")
        self.password = os.getenv("password", "")
        self.session_id = None
        self.success = 0

    def login(self):
        """Login to ClassCharts and get an Access token (session_id)."""
        url = f"{self.api_url}/login"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'} 
        data = {
            "email": self.username,
            "password": self.password
        }
        response = self._make_request(url, 'POST', header, data)
        self.session_id = response['meta']['session_id']
        self.success = response['success']
        return response
        
    def ping(self):
        """Refresh ClassCharts login session_id.
        Access tokens should be refreshed every 180 seconds."""
        url = f"{self.api_url}/ping"
        header = {'Content-Type' : 'application/x-www-form-urlencoded', 'Authorization': f'Basic {self.session_id}'}
        data = {
            "include_data": True
        }
        response = self._make_request(url, 'POST', header, data)
        self.session_id = response['meta']['session_id']
        return response

    def _make_request(self, url, method, header, data=None):
        """Make a request to ClassCharts API."""
        try:
            response = requests.request(
                method,
                url,
                headers=header,
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)


class Student:
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


class Homework():
    """ClassCharts homework class."""
    def __init__(self, **kwargs):
        self.lesson = kwargs.get("lesson")
        self.subject = kwargs.get("subject")
        self.teacher = kwargs.get("teacher")
        self.homework_type = kwargs.get("homework_type")
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.meta_title = kwargs.get("meta_title")
        self.description = kwargs.get("description")
        self.issue_date = kwargs.get("issue_date")
        self.due_date = kwargs.get("due_date")
        self.completion_time_unit = kwargs.get("completion_time_unit")
        self.completion_time_value = kwargs.get("completion_time_value")
        self.publish_time = kwargs.get("publish_time")
        self.status = kwargs.get("status")
        self.validated_links = kwargs.get("validated_links")
        self.validated_attachments = kwargs.get("validated_attachments")

    def __str__(self):
        return f"{self.title} ({self.subject}) - {self.due_date}"

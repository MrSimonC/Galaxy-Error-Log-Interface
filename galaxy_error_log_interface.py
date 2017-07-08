from slackclient import SlackClient
import datetime
import os
import sys
__version__ = '1.1'
# v1.1 = updated slack calling


class ErrorLog:
    """
    Checks if the error log (updated every 10 mins) has been updated in the last 15 mins, as if not, could indicate
    messaging has gone down
    """
    def __init__(self, error_log_path):
        self.folder_path = error_log_path

    @staticmethod
    def most_recent_file(folder):
        """
        Returns most recently modified file with timestamp
        :param folder: folder to process
        :return: filename_full_path, dateobject
        """
        files = ErrorLog.get_files(folder)
        files_with_mod_dates = [[os.path.abspath(file),
                                 datetime.datetime.fromtimestamp(os.path.getmtime(file))]  # modified date
                                for file in files]
        if not files_with_mod_dates:
            return None, None
        most_recent_file = files_with_mod_dates[0][0]
        most_recent_file_date = files_with_mod_dates[0][1]
        for file, mod_date in files_with_mod_dates:
            if mod_date > most_recent_file_date:
                most_recent_file = file
                most_recent_file_date = mod_date
        return most_recent_file, most_recent_file_date

    @staticmethod
    def get_files(folder):
        return [os.path.join(folder, file) for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

    def last_log_is_within_minutes_of_now(self, minutes=15):
        """
        Checks if the last modify date of the latest Galaxy error file is within (15) mins tollerance.
        If not, the interface is likely down.
        :param minutes: int of minutes behind now time to check for
        :return: True if modify date is ok, False not (i.e. interface down)
        """
        recent_error_file, recent_error_file_time = self.most_recent_file(self.folder_path)
        if recent_error_file_time > datetime.datetime.now() - datetime.timedelta(minutes=minutes):
            print('OK: error log within {0} minutes of current time'.format(minutes))
            return True
        else:
            print('Warning: error log was last updated {0}'.format(recent_error_file_time.strftime('%H:%M')))
            ErrorLog.slack_notify(recent_error_file_time.strftime('%H:%M'))
            return False

    @staticmethod
    def slack_notify(modify_time, me_only=False):
        s = SlackClient(os.environ['SLACK_LORENZOBOT'])
        message = 'Galaxy Interface Warning: Galaxy error log was last updated {0}, ' \
                  'indicating the interface may be down... can you please check?'.format(modify_time)
        if me_only:
            # IM me only
            simon_id = ErrorLog._slack_get_value(s.api_call('users.list'), 'Simon Crouch', 'real_name', 'id', 'members')
            user_dm_channel = ErrorLog._slack_get_value(s.api_call('im.list'), simon_id, 'user', 'id', 'ims')
            response = s.api_call('chat.postMessage', as_user=True, channel=user_dm_channel, text=message)
        else:
            # Back Office group
            response = s.api_call('chat.postMessage', as_user=True, channel='backoffice', text=message)
        if not response['ok']:
            return False
        return True

    @staticmethod
    def _slack_get_value(slack_response, search_value, search_field, return_field, classifier):
        """
        Traverses a slack response to obtain a single value
        :param slack_response: json response from slackclient api_call
        :param search_value: value to search for
        :param search_field: field to search for the value in
        :param return_field: field who's value you want to return
        :param classifier: specific slack identifying string which is found in the slack_response e.g. 'groups'
        :return: string value
        """
        if not slack_response['ok']:
            return False
        for item in slack_response[classifier]:
            if search_field in item and search_value == item[search_field] and return_field in item:
                return item[return_field]


if __name__ == '__main__':
    e = ErrorLog(r'\\nbsvr139\SFTP\GalaxyConfig\LIVE')
    try:  # -t = send test direct message to Simon Crouch
        if sys.argv[1] == '-t':
            e.slack_notify('Test message from slack_lorenzobot.py', True)
            sys.exit(0)
    except IndexError:
        pass
    e.last_log_is_within_minutes_of_now()

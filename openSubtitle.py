from FileOperations import File
from urllib.parse import urlencode

import os
import requests
import requests_cache
import json
import sys


class OpenSubtitles(object):

    def __init__(self):
        requests_cache.install_cache(cache_name='opensubtitle_cache', backend='sqlite', expire_after=600)
        requests_cache.remove_expired_responses()
        self.login_token = ""
        self.user_downloads_remaining = ""
        self.folder_path = ""
        self.file_name = ""
        self.sublanguage = ""
        self.forced = ""
        try:
            with open("credentials.json", "r") as fp:
                credentials = json.load(fp)
            self.username = credentials['username']
            self.password = credentials['password']
            self.apikey = credentials['api-key']

        except FileNotFoundError:
            print("No credentials file found at \"" + os.path.dirname(os.path.realpath(__file__)) + "/.credentials\"")
        except KeyError:
            print("Incorrectly formatted secrets in .credentials file")
    def login(self):

        login_url = "https://www.opensubtitles.com/api/v1/login"
        login_headers = {'api-key': self.apikey, 'content-type': 'application/json'}
        login_body = {'username': self.username, 'password': self.password}

        try:
            login_response = requests.post(login_url, data=json.dumps(login_body), headers=login_headers)
            login_response.raise_for_status()
            login_json_response = login_response.json()

            self.login_token = login_json_response['token']
        except requests.exceptions.HTTPError as httperr:
            raise SystemExit(httperr)
        except requests.exceptions.RequestException as reqerr:
            raise SystemExit("Failed to login: " + reqerr)
        except ValueError as e:
            raise SystemExit("Failed to parse login JSON response: " + e)

        user_url = "https://www.opensubtitles.com/api/v1/infos/user"
        user_headers = {'api-key': self.apikey, 'authorization': self.login_token}

        try:
            with requests_cache.disabled():
                user_response = requests.get(user_url, headers=user_headers)
                user_response.raise_for_status()

                user_json_response = user_response.json()
                self.user_downloads_remaining = user_json_response['data']['remaining_downloads']

        except requests.exceptions.HTTPError as httperr:
            raise SystemExit(
                httperr)
        except requests.exceptions.RequestException as reqerr:
            raise SystemExit("Failed to login: " + reqerr)
        except ValueError as e:
            raise SystemExit("Failed to parse user JSON response: " + e)
    def search_for_subtitle(self, full_file_path, sublanguage, forced=False):

        self.folder_path = str(os.path.dirname(full_file_path))
        self.file_name = str(os.path.basename(full_file_path))
        self.sublanguage = sublanguage
        self.forced = forced

        try:
            file_to_inspect = File(full_file_path)
        except FileNotFoundError as fileerr:
            SystemExit("Input video file could not be found")

        try:
            query_params = {'moviehash': file_to_inspect.get_hash(),
                            'foreign_parts_only': 'only' if forced else 'exclude',
                            'languages': self.sublanguage,
                            'query': self.file_name}

            query_url = 'https://www.opensubtitles.com/api/v1/subtitles?'
            query_headers = {'api-key': self.apikey}
            query_response = requests.get(query_url, params=query_params, headers=query_headers)
            query_response.raise_for_status()
            query_json_response = query_response.json()

            query_file_no = query_json_response['data'][0]['attributes']['files'][0]['file_id']
            query_file_name = query_json_response['data'][0]['attributes']['files'][0]['file_name']

            return {'file_no': query_file_no, 'file_name': query_file_name}

        except requests.exceptions.HTTPError as httperr:
            raise SystemExit(httperr)
        except requests.exceptions.RequestException as reqerr:
            raise SystemExit("Failed to login: " + reqerr)
        except ValueError as e:
            raise SystemExit("Failed to parse search_subtitle JSON response: " + e)
        except IndexError as inerr:
            print("No subtitle found at OpenSubtitles for " + self.file_name)



    def download_subtitle(self, file_no, output_directory=None, output_filename=None, overwrite=False):

        download_directory = self.folder_path if output_directory is None else output_directory

        download_filename = os.path.splitext(self.file_name)[0] if output_filename is None else output_filename
        download_filename += "." + self.sublanguage
        download_filename += ".forced" if self.forced else ""
        download_filename += ".srt"

        download_url = "https://www.opensubtitles.com/api/v1/download"
        download_headers = {'api-key': self.apikey,
                            'authorization': self.login_token,
                            'content-type': 'application/json'}
        download_body = {'file_id': file_no}

        if os.path.exists(download_directory + os.path.sep + download_filename) and not overwrite:
            print("Subtitle file " + download_directory + os.path.sep + download_filename + " already exists")
            return None

        if self.user_downloads_remaining > 0:

            try:
                download_response = requests.post(download_url, data=json.dumps(download_body), headers=download_headers)
                download_json_response = download_response.json()

                download_link = download_json_response['link']

                download_remote_file = requests.get(download_link)
                try:
                    open(download_directory + os.path.sep + download_filename, 'wb').write(download_remote_file.content)
                    print("Saved subtitle to " + download_directory + os.path.sep + download_filename)
                except IOError:
                    print("Failed to save subtitle to " + download_directory + os.path.sep + download_filename)


            except requests.exceptions.HTTPError as httperr:
                raise SystemExit(httperr)
            except requests.exceptions.RequestException as reqerr:
                raise SystemExit("Failed to login: " + reqerr)
            except ValueError as e:
                raise SystemExit("Failed to parse search_subtitle JSON response: " + e)
        else:
            print("Download limit reached. Please upgrade your account or wait for your quota to reset (~24hrs)")
            sys.exit(0)
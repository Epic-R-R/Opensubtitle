![opensubtitle-img](https://raw.githubusercontent.com/Epic-R-R/Opensubtitle/master/img/Opensubtitles-770x410.jpg)

# Opensubtitle API
A simple API for download subtitle from opensubtitle for movies and series
**API is currently in BETA**
# API


Change credentials.json file:
```json
{
    "username": "YOURUSER",
    "password": "YOURPASS",
    "api-key": "YOURAPIKEY"
}
```
```python
from openSubtitle import OpenSubtitles
op = OpenSubtitles()
op.login()
file_info = os.get_subtitle_file_info("MOVIE FILE PATH", "en", True)
op.download_subtitle(file_info['file_no'])
```

### Search for a subtitle:
```python
get_subtitle_file_info(full_file_path, sublanguage, forced)
```
* full_file_path = *required*
* sublanguage = *required*
* forced = *optional* (default=False)

Returns dictionary:

    { file_no : XXXXX, file_name: XXXX }

### Download subtitle:
```python
download_subtitle(file_no, output_directory, output_filename, overwrite)
```
* file_no = *required*
* output_directory = *optional* (default=same as video file)
* output_filename = *optional* (default=same as video file)
* overwrite = *optional* (default=False)

from openSubtitle import OpenSubtitles
import sys


def main():

    op = OpenSubtitles()
    op.login()

    print(f"Downloads remaining: {str(op.user_downloads_remaining)}")

    file_info = op.search_for_subtitle("MOVIE FILE PATH", "en", True)

    op.download_subtitle(file_info['file_no'])

if __name__ == "__main__":
    main()
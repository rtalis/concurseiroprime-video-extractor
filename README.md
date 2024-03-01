# Video Downloader for E-Learning Platform

This project provides a Python script for downloading videos from a specific e-learning platform. It supports downloading regular video files and videos embedded from YouTube. The script automates the process of logging into the platform, navigating through course materials, and saving videos locally for offline access. Additionally, it handles video and audio streams separately, merging them into a single file where necessary.

## Features

- Automatic login to the e-learning platform.
- Navigation through course materials to find video links.
- Support for downloading YouTube embedded videos.
- Merging video and audio streams into a single file.
- Organizing downloaded videos into a directory structure based on course content.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or later.
- pip for installing Python packages.
- Google Chrome or Chromium browser installed on your system.
- ffmpeg installed for processing video and audio streams.

## Installation

To set up the project environment:

1. Clone the repository to your local machine:

```   git clone https://github.com/yourusername/yourprojectname.git```

Navigate to the project directory:



cd yourprojectname

    Install the required Python packages:

bash

pip install -r requirements.txt

Usage

To use the video downloader, follow these steps:

    Set your environment variables for EMAIL and PASSWORD to log into the e-learning platform securely:

bash

export email='your_email@example.com'
export password='yourpassword'

    Run the script:

bash

python downloader.py

    Follow the on-screen instructions to select and download videos.

Contributing

Contributions to this project are welcome. Please follow the standard fork-and-pull request workflow on GitHub. If you plan to propose a significant change, please discuss it in an issue before submitting a pull request.
Acknowledgments

This project uses several open-source packages:

    Selenium for web automation.
    PyTube for downloading YouTube videos.
    Requests and BeautifulSoup for web scraping.

License

This project is licensed under the MIT License - see the LICENSE file for details.
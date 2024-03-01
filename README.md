# Video Downloader for E-Learning brazilian Platform

This project provides a Python script for downloading videos from a specific e-learning brazilian platform. It supports downloading video files from securely embedded vimeo and videos embedded from YouTube. The script automates the process of logging into the platform, navigating through course materials, and saving videos locally for offline access. Additionally, it handles video and audio streams separately, merging them into a single file where necessary.

The main reason for this code is to help other pleople with examples of capturing streaming videos with selenium
and other web scrapping techniques. This is an quick and dirty code, done in a couple of spare hours for practice
and for learning. 

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

    `git clone https://github.com/rtalis/yourprojectname.git`

2. Navigate to the project directory:

    `cd yourprojectname`

3. Install the required Python packages:


    `pip install -r requirements.txt`

## Usage

To use the video downloader, follow these steps:

1. Set your environment variables for EMAIL and PASSWORD to log into the e-learning platform securely:

    `export email='your_email@example.com'`
    `export password='yourpassword'`

2. Set up the variables on the beginning of the script:

    `COURSE_NAME = "YOUR_COURSE"`

    `...`

3. Run the script:

    `python3 main.py`

The script will start downloading automatically, checking for pree

Contributing

Contributions to this project are welcome. Please follow the standard fork-and-pull request workflow on GitHub. If you plan to propose a significant change, please discuss it in an issue before submitting a pull request.
Acknowledgments

This project uses several open-source packages:

    Selenium for web automation.
    PyTube for downloading YouTube videos.
    Requests and BeautifulSoup for web scraping.

License

This project is licensed under the MIT License - see the LICENSE file for details.
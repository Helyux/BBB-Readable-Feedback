<div id="shields" align="center">

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
![Compatibility][compatibility-shield]
[![Xing][xing-shield]][xing-url]
</div>

# BBB-Readable-Feedback

Did you activate the 
[feedback feature](https://docs.bigbluebutton.org/admin/customize.html#collect-feedback-from-the-users)
in BigBlueButton (BBB) but you can't read all the jibberish in the logfile?
This simple script creates humanly readable output from the feedback logs of your BigBlueButton (BBB) instance.

It has 6 simple cmd parameters you **can** use, none of which is required:

| Short | Parameter | Default | Explanation |
| :--- | :--- | :--- | :--- |
| -h | --help | None | Displays this table
| -p | --path | /var/log/nginx/ | Provide the full path to the directory containing the feedback logs |
| -s | --silent | False | If True the script won't have any output |
| -pz | --parsezip | False | If True unzip `.gz` logs and parse them aswell |
| -tf | --tofile | False | If True write the output to `html5-client-readable.log` |
| -csv |  | False | If True write the output to `BBB-Feedback.csv` |


## Installation

* Make sure you got atleast `Python 3.6` installed: `python3 -V`
* Copy the script or clone this repo to the server containing the BBB instance:
`git clone https://github.com/Helyux/BBB-Readable-Feedback`

## Example Use

Execute `python3 ReadFeedback.py -pz -tf`

This will parse all `html5-client.log` files in the directory `/var/log/nginx/`, even those who are already
zipped (`-pz`) and display something like this:
![Screenshot](https://user-images.githubusercontent.com/10271600/192272049-36805aa0-a2e1-4de7-8e0d-7c1edd5816e9.png)
It'll also write the displayed info to the file
`html5-client-readable.log` in the given path. (`-tf`)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Helyux/BBB-Readable-Feedback.svg?style=for-the-badge
[contributors-url]: https://github.com/Helyux/BBB-Readable-Feedback/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Helyux/BBB-Readable-Feedback.svg?style=for-the-badge
[forks-url]: https://github.com/Helyux/BBB-Readable-Feedback/network/members
[stars-shield]: https://img.shields.io/github/stars/Helyux/BBB-Readable-Feedback.svg?style=for-the-badge
[stars-url]: https://github.com/Helyux/BBB-Readable-Feedback/stargazers
[issues-shield]: https://img.shields.io/github/issues/Helyux/BBB-Readable-Feedback.svg?style=for-the-badge
[issues-url]: https://github.com/Helyux/BBB-Readable-Feedback/issues
[license-shield]: https://img.shields.io/github/license/Helyux/BBB-Readable-Feedback.svg?style=for-the-badge
[license-url]: https://github.com/Helyux/BBB-Readable-Feedback/blob/master/LICENSE
[xing-shield]: https://img.shields.io/static/v1?style=for-the-badge&message=Xing&color=006567&logo=Xing&logoColor=FFFFFF&label
[xing-url]: https://www.xing.com/profile/Lukas_Mahler10
[compatibility-shield]: https://img.shields.io/badge/bbb--compatibility-2.3%20%7C%202.4%20%7C%202.5-success?style=for-the-badge
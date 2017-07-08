# Galaxy Error Log Interface

## Background
Interface (between CSC Lorenzo and Galaxy) uptime monitoring system (which should be realtime) which observes when the interface goes down, then informs Back Office team via Slack.

Process Galaxy error log to see if it hasn't been updated in the last 15 mins, which could indicate that the Lorenzo to Galaxy interface maybe down (as the error log is updated every 10 minutes by the interface and is the only method of monitoring the interface).

## Prerequisite
Install "Visual C++ Redistributable for Visual Studio 2015 x86.exe" (on 32-bit, or x64 on 64-bit) which allows Python 3.5 dlls to work, found here:
https://www.microsoft.com/en-gb/download/details.aspx?id=48145

## Installation and Running
Make a folder in "C:\Program Files\Galaxy Error Log Interface" (or another location of you choice) and put all the following files in there:
- Galaxy Error Log Interface.xml
- galaxy_error_log_interface.exe

In Windows Task Scheduler, Import Task, choose the .xml file, then change the "Run only when user is logged on" username to your own.
OR create a new task with the following attributes:
- General: Run only when user is logged on
- Trigger: at 8am everyday, repeat every 10 minutes indefinitely
- Actions: Start a program: "C:\Program Files\Galaxy Error Log Interface\galaxy_error_log_interface.exe"
    - Start in (optional): C:\Program Files\Galaxy Error Log Interface
- Settings:
    - Allow ask to be run on demand
    - Stop the task if it runs longer than: 3 days
    - If the running task does not end when requested, force it stop
    - If the task is already running, then the following rule applies: Stop the existing instance

## Notes
### Explorer
The user whom this program is run under MUST have read access to folder: `\\nbsvr139\SFTP\GalaxyConfig\LIVE`

### SDPlus API
This program communicates with the sdplus API via an sdplus api technician key which can be obtained via the sdplus section: Admin, Assignees, Edit Assignee (other than yourself), Generate API Key.  
This program will look for an API key in a windows variable under name "SDPLUS_ADMIN". You can set this on windows with:
`setx SDPLUS_ADMIN <insert your own SDPLUS key here>`
in a command line.

### Slack
This program communicates with slack API via an API Token which can be obtained by: https://it-nbt.slack.com/services/B1FCFC4RL (or Browse Apps  > Custom Integrations  > Bots  > Edit configuration)
This program will look for an API key in a windows variable under name "SLACK_LORENZOBOT". You can set this on windows with:
`setx SLACK_LORENZOBOT <insert your own SDPLUS key here>`
in a command line.

_Written by:_  
_Simon Crouch, late 2016 in Python 3.5_
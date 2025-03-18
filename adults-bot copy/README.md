
# Adults Community Telegram Bot

The bot lets users create simple polls (time and place polls). Based on results, it sends a message with the meeting place and time. Users can suggest or remove places with a 24-hour anonymous poll that manages the database. On the meeting day, remind users to add a photo to the group, which will be uploaded to Google Drive.


## Acknowledgements

 - [Google API Developer Console](https://console.cloud.google.com/)
 - [Google Firebase](https://console.firebase.google.com)



## Constants and Settings Overview (app/constants)
Contains security sensitive data and global settings of the bot. Change with caution!

| File | Description     
| :-------- | :------- 
| `adbot-db-login.json` | File that contains keys and logins for the Firebase Database.|
| `config.ini` | Contains tokens, path to logins and some other security sensitive data. |
| `global_settings.py` | Contains all bot's and system's settings that could be edited (text, poll duration, places list, etc) |
| `google_drive_creds.json` | File that contains keys and logins for the Google Drive API |


## Commands Overview (app/handlers)
Contains all the bot's commands and handlers. For further development please drop all new commands right there.

| File | Description     
| :-------- | :------- 
| `__init__.py` | Initializes all routers and handlers in the list. |
| `add_place.py` | Add required place to the database using /add_place command and its argument. |
| `remove_place.py` | Removes required place from the database using /remove_place command and its argument|
| `revote_day.py` | Create revote 48 hour revote day poll using /revote_day command|
| `revote_time.py` | Create revote 48 hour revote time poll using /revote_time command|
| `start.py` | Prepare init process with /start command. It init database with a group and starts main init process with a polls.|

## Keyboard Overview (app/keyboards)
Contains all the bot's keyboards (reply or inline). Please drop new right there if any.

| File | Description     
| :-------- | :------- 
| `inline.py` | Creates inline keyboard for the DM /start command. Also provides user-friendly URL to add the bot to the required group with all required permissions. |

## Utilities Overview (app/utils)
Contains all utils that bot should use. Processes, recoveries and APIs interactions should be placed there. 

| File | Description     
| :-------- | :------- 
| `google_drive.py` | Interacts with Google Drive API and provides function to upload the image to the required folder in the Drive. |
| `meeting_cycle.py` | Creates meeting cycle and checks current status of the meeting. |
| `poll_closure.py` | Checks if the poll finished using close_time variable from the database. |
| `process_poll.py` | Processes poll and write or update data in the database and notify users about poll changes. |
| `restore.py` | This file is crucial for the bot recovering. This script will recover all previous polls and cycles in case if the bot accidentaly shuted down on the backend side. |

## Database Reference (app/database/db.py)

#### Add data to the database
Add and push data to the database using reference and chat ID. 

```python
  add_data(ref: str, id: int, data: dict)
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `ref` | `string` | **Required**. Reference to add |
| `id` | `integer` | **Required**. Group ID |
| `data` | `dict` | **Required**. Data to add |


#### Get data from the database
Get required data from the database using reference.

```python
  get_data(ref: str, id: int) -> dict
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `ref` | `string` | **Required**. Reference to get |
| `id` | `integer` | **Required**. Group ID |

Returns a ```dict``` of data.

#### Update data in the database
Updates specific data in the database reference.

```python
  update_data(group_id: int, data: dict)
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `group_id` | `integer` | **Required**. Group ID |
| `data` | `dict` | **Required**. Data to update |

#### Delete data in the database
Deletes specific data from the database with reference.

```python
  delete_data(ref: str, id: int)
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `group_id` | `integer` | **Required**. Group ID |
| `data` | `dict` | **Required**. Data to update |

#### Get all data from the database
Gets and returns dictionary with given data from the database.

```python
  get_all(name: str) -> dict
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `name` | `string` | **Required**. Name of DB reference (e.g 'groups') |


## Global Settings (app/constants/global_settings.py)

### Variables
``PHOTO_HASHTAG_TRIGGER``: set a hashtag or a trigger text for a photo to upload at the end of the meeting.

``MIN_VOTES``: Minimal votes to finish the poll.

``POLL_CLOSE_TIME``: Close time for the general polls (add_place, remove_place). Adjust value in hours.

``POLL_CLOSE_TIME``: Close time for the revote polls (revote_day, revote_time). Adjust value in hours.

``FOLDER_ID``: Provide a Google Drive folder ID where all the incoming photos will be uploaded (You can find ID in the URL address at the end of the link)

``OWNER_ID``: Required for the database security and unwanted filling. This varialbe triggers when /start command called to fill out list of the places by admin. 

Without this variable any user with the bot could add to their own group and adjust places and launch this bot (it's unwanted process so we must ensure that in the group exist admin's ID)

### Texts
#### /start [places]
**Description**: A start command that triggers the bot in the group or Direct Message (DM). Admin that inserted their own ``OWNER_ID`` must provide places as an arguments at the fresh group start (e.g ```/start place1,place2,place3```). Please do not use spaces between places.

``GROUP_START_MESSAGE``: Adjust a start message text for the group (it appears with a video)

``DM_START_MESSAGE``: Adjust a start message text for the Direct Message (DM)

``START_VIDEO_PATH``: Adjust a path for a video that will appear with ``GROUP_START_MESSAGE``

#### /add_place [place_to_add]
**Description**: A command that allows to add new place to the database and use it later in the poll. User must provide a place as an argument.

``ADD_PLACE_ERR``: A place error message that caused by user.

``ADD_PLACE_DIGIT_ERR``: A place digit error message that caused by user (provided digits instead of real placename)

``ADD_PLACE_ARG_ERR``: A place argument error message that caused by user (didn't provide argument)

``ADD_PLACE_EXIST_ERR``: A place error message that caused by user (place already exist in the database)

``ADD_PLACE_CHANGE``: An info message when place has been added successfuly.

``ADD_PLACE_DECLINE``: An info message when place has been voted, but declined.

``ADD_PLACE_QUESTION``: A poll place question text.

#### /remove_place [place_to_remove]
**Description**: A command that allows to remove the place from the database using polls. User must provide a place as an argument.

``RM_PLACE_ERR``: A place error message that caused by user.

``RM_PLACE_DIGIT_ERR``: A place digit error message that caused by user (provided digits instead of real placename)

``RM_PLACE_ARG_ERR``: A place argument error message that caused by user (didn't provide argument)

``RM_PLACE_EXIST_ERR``: A place error message that caused by user (place does 
not exist in the database)

``REMOVE_PLACE_CHANGE``: An info message when place removal has been voted and removed from the database.

``REMOVE_PLACE_DECLINE``: An info message when place removal has been voted, but declined.

``RM_PLACE_QUESTION``: A question text for remove poll.

#### /revote_day [no_args]
**Description**: A command that allows to revote chosen day with a poll and put new day to the database. User must not provide any arguments.

``RV_DAY_ERR``: A revote day error message that caused by user.

``RV_DAY_QUESTION``: A question for the revote poll day.

``RV_DAY_OPTIONS``: A list of options (weekdays) for the revote poll day.

``REVOTE_DAY_CHANGE``: An info message when day has been revoted and changed.

``REVOTE_TIME_CHANGE``: An info message when time has been revoted and changed.

#### /revote_time [no_args]
**Description**: A command that allows to revote chosen time with a poll and put new time to the database. User must not provide any arguments.

``RV_TIME_ERR``: A revote day error message that caused by user.

``RV_TIME_QUESTION``: A question for the revote poll time.

``RV_TIME_OPTIONS``: A list of options (times) for the revote poll time.

``RV_TIME_OPTIONS``: A list of options (times) for the revote poll time.

### Polls (initial start)
An initial polls that starts at the begining of the group.

``POLL_DAY_QUESTION``: A question for the initial day poll.

``POLL_DAY_OPTIONS``: A list of days for the initial day poll.

``POLL_TIME_QUESTION``: A question for the initial time poll.

``POLL_TIME_OPTIONS``: A list of times for the initial time poll.  

### Meeting Cycle (statuses, settings)
#### Statuses

| Status | Description     
| :-------- | :------- 
| `waiting_poll` | Posts the poll 5 days before the meeting. Shuffle the places, exclude the winner if there is one, and send the poll itself. |
| `poll_active` | After posting the poll it reminds to user about the poll 3 days before the meeting. |
| `notifying_users` | Process the poll 1 day before the meeting. Get results and push them right to the database. If there is a tie it pick some random place from the list. |
| `meeting_day` | Status means that the meeting has started. Bot on this status will send the reminder to upload the photo from the meeting (2 hours after event time) |
| `photo_reminder` | Status means that the meeting is finished. Bot on this status will accept incoming images with hashtag and will close the cycle with ```completed``` status in 1 day. |
| `completed` | Status means that the cycle is finished. Meeting number will be increased and next meeting date will be updated accordingly |

#### Settings
```WAITING_POLL_STATUS_DELAY```: Adjusts days to wait before the poll place meeting will be posted (5 days by default)

```POLL_ACTIVE_STATUS_DELAY```: Adjusts days to wait before the poll reminder will be posted (3 days by default)

```NOTIFYING_USERS_STATUS_DELAY```: Adjusts days to wait before the poll results will be calculated and poll will be stopped (1 days by default)

```MEETING_DAY_STATUS_DELAY```: Adjusts hours to wait after meeting starts and bot will send the photo reminder.

```PLACES_LIMIT```: Adjusts place limit to vote.

```PLACE_REMIND_MESSAGE```: Posts a place message reminder.

```PHOTO_REMIND_MESSAGE```: Posts a photo message reminder.

```TIE_MESSAGE```: Posts a tie message.

#### Developer Commands
```/ping```: ping the bot to check status

```/debug```: get debug.log file. This file shows all processes, warnings and some other useful information to debug. Please ensure that you set ```OWNER_ID``` in the ```global_settings.py``` so the bot will send this security sensitive file only for its owner.
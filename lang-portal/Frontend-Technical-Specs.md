# Frontend Technical Specs

## Pages

### Dashboard `/dashboard`

#### Purpose
Purpose of this page is to provide a summary of learning and be the default landing page.

#### Components
This page contains the following sections:
- Last 3 study sessions
  - Study session card
    - Group name
    - Date
    - Score

- Study Progress
  - Study progress card
    - Total words
    - Correct
    - Wrong
    - Percentage

- Quick Stats
  - Quick stats card
    - Total study sessions
    - Active groups
    - Study streak

- Start study session button
  - goes to study activity page

#### Needed API Endpoints
We will make use of the following API endpoints to make this page work
- GET /api/dashboard/last_study_session_id
- GET /api/dashboard/study_progress
- GET /api/dashboard/quick_stats

### Study Activities Index `/study_activities`

#### Purpose

Purpose of this page is to show a collection of study activities with a thumbnail and its name, to launch or view study activity.

#### Components

- Study Activity Card
    - show a thumbnail of study activity
    - name of study activity
    - launch button to take us to launch page
    - view page button to view more info about past study session


#### Needed API Endpoints

- GET /api/study_activities
    - pagination













### Study Activity Show `/study_activities/:id`

#### Purpose
Purpose is to show the details of a study activity and its past study sessions

#### Components
- Name of study activity
- Thumbnail of study activity
- Description of study activity
- Launch button
- Study Activities Paginated List
    - id
    - activity name
    - group name
    - start time
    - end time (inferred by the last word_review_item submitted)
    - number of review items

#### Needed API Endpoints
- GET /api/study_activities/:id
- GET /api/study_activities/:id/study_sessions


### Study Activities Launch `/study_activities/:id/launch`

#### Purpose
Purpose of this page is to launch a study activity

#### Components
- Name of study activity
- Launch form
    - select field for group
    - launch now button
After the form is submitted the page will redirect to the study session show page.

#### Needed API Endpoints
- POST /api/study_activities



### Words Index `/words`

#### Purpose
Purpose of this page is to show all words in our database.
#### Components
- Paginated Word List
    - Columns
        - Japanese
        - Romaji
        - English
        - Correct Count
        - Incorrect Count
    - Pagination 100 items per page
    - Clicking the Japanese word will take us to the word show page

#### Needed API Endpoints
- GET /api/words


### Word Show `/words/:id`

#### Purpose
Purpose of this page is to show information about a specific word.

#### Components
- Japanese
- Romaji
- English
- Study Statistics
    - Correct Count
    - Incorrect Count
- Word Groups
    - shown as a series of tags
    - when group name is clicked it will take us to the group show page

#### Needed API Endpoints
- GET /api/words


### Word Groups Index `/groups`


#### Purpose
Purpose of this page is to show a list of groups in our database.

#### Components
- Paginated Group List
    - Columns
        - Group Name
        - Word Count
    - Clicking the group will take us to the group show page

#### Needed API Endpoints
- GET /api/groups



### Group Show `/groups/:id`

#### Purpose
Purpose of this page is to show information about a specific group.

#### Components
- Group Name
- Group Statistics
    - Total word count
- Words in Group (Paginated List of words)
    - Columns
        - Japanese
        - Romaji
        - English
        - Correct Count
        - Incorrect Count
- Study Sessions (Paginated List of study sessions)
    - Columns
        - Id
        - Activity Name
        - Group Name
        - Start Time
        - End Time
        - Number of Review Items

#### Needed API Endpoints
- GET /api/groups/:id (the name and group statistics)
- GET /api/groups/:id/words
- GET /api/groups/:id/study_sessions

### Study Sessions Index `/study_sessions`

#### Purpose
Purpose of this page is to show a list of study sessions in our database.

#### Components
- Paginated Study Session List
    - Columns
        - Id
        - Activity Name
        - Group Name
        - Start Time
        - End Time
        - Number of Review Items
    - Clicking the study session id will take us to the study session show page

#### Needed API Endpoints
- GET /api/study_sessions


### Study Sessions Show `/study_sessions/:id`

#### Purpose
Purpose of this page is to show information about a specific study session

#### Components
- Study Session details
    - Activity Name
    - Group Name
    - Start Time
    - End TIme
    - Number of review items
- Words Reviewed
    - Columns
        - Japanese
        - Romaji
        - English
        - Correct Count
        - Incorrect Count

#### Needed API Endpoints
- GET /api/study_sessions/:id/
- GET /api/study_sessions/:id/words


### Settings Page `/setings`

#### Purpose
Purpose of this page is to make configuration changes to the study portal

#### Components
- Theme Selection
    - this will allow you to select a theme. eg. light, dark themes
- Language Selection Button
    - this will allow you select the language you want to study in the study portal. eg Japanese, french, Twi, Spanish
- Reset History Button
    - this will allow you to delete all study sessions and word review items.
- Full Reset Button
    - this will drop all tables and re-create with seed data

#### Needed API Endpoints
- POST /api/reset_history
- POST /api/full_reset
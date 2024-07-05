# Pick-the-Winners Proposal

This will be a website where sports fans can test their mettle and pick which teams will win in professional sports games.  After signup, users are shown a list of upcoming games so they can choose who they think will win for the next day or week.  After some games are finished, they could log in and see how they're doing.  A leaderboard page will show a top 20 list of the users with the best record of correct picks in the time period.  A cool stretch goal would be to add a statistics page showing correct percentages broken down by sport, league, month, etc.

**Technologies:** Python/Flask, Jinja, WTForms, SQLAlchemy, PostgreSQL, RESTful APIs, HTML, CSS, JavaScript.  Hosted on Render and ElephantSQL.

**Demographic:** Anyone who loves watching professional sports.

**Data Source:** This will use the API at TheSportsDB.com to collect info about upcoming games and update game scores.

## Database Schema

- User accounts
  - Username
  - Hashed password
- Sports (football, baseball, basketball)
  - API ID
  - Name
- Leagues (NFL, MLB, FIFA, college basketball)
  - API ID
  - Name
  - Abbreviation
  - Sport -> Sports
- Teams playing the games
  - API ID
  - Name
  - Location
  - Abbreviation
  - League -> Leagues
- Seasons
  - Name
  - Year
  - League -> Leagues
- Subseasons
  - Name
  - Type (regular, postseason, etc)
  - Start Date
  - End Date
  - Season -> Seasons
- Games to be picked and their current scores
  - API ID
  - Start Time
  - Status (not started, final, postponed, etc.)
  - Home team -> Teams
  - Away team -> Teams
  - Home score
  - Away score
  - Subseason -> Subseasons
- User's game picks
  - User -> Users
  - Game -> Games
  - Picked Team -> Teams

## Tasks

- [x] User account signup/login

- [x] Welcome screen with a Make Picks button or if picks are already made, a list of picks with current game scores.

- [x] Make Your Picks page with a list of games for users to choose which teams they think will win.  The listed games can be games from several sports happening over the next day, week or some time period that includes a reasonably long list of games.

- [ ] Group the list by sport, then league, then day (if time period covers more than one day).

- [x] Leaderboard page showing the current list of users with the most correct picks for the time period.

- [x] Create a background process to
  - [x] Fetch current scores and update the Games table.

## Stretch Goals

- [ ] Statistics page showing percentage of correct picks over time broken down by sport, league, involving a certain team, month/year, home or away team picked, etc.

- [ ] Ability to change picks for games that haven't started yet.

- [x] Show a list of user's past pick sheets.

- [ ] Allow users to pick only the sports and leagues they like.

- [ ] Single-game mode with picks like which team scores first, most points per quarter, who wins the coin toss, etc.  Depends on what stats are available in the API.  Most fun for special games like championship or all-star games.

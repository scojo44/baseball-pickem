Baseball Pickem
===============

Think you know baseball?  Try your hand at picking the winners of Major League Baseball games by playing [Baseball Pickem](https://baseball-pickem.onrender.com/)!  Once you make your picks, come back and see how many points you earned for correctly picked games and compare your totals with other baseball fans!

It's hosted at Render.com on their free tier so expect a long delay as the server starts the app from sleep mode.  Render puts free-tier apps to sleep if there hasn't been a request in a whlie.

How to Play
-----------
This is set up as Fun Part First.  From the landing page, hit the Play Now button and make your picks.  From there, sign up or log in to save your picks then come back to check on them later after some games have been played.  Correct picks will earn one point each.  Once logged in, your picks are shown on the My Picks page.  See who earned the most points on the Leaderboard page by day and the season overall.  Browse scores of past gamews and the schedule for future games on the Scoreboard page.

Game scores are updated every 20 minutes since the all-sports.io API free tier allows only 100 requests per day.

Under the Hood
--------------
The site is coded in Python using Flask and SQLAlchemy with data stored in a PostgreSQL database.
- APScheduler handles the scoring updates
- Bcrypt hashes user passwords
- WTForms handles form generation and submission.

A pattern I'd like to highlight is the games are loaded with JavaScript API calls using axios after Flask returns the HTML for the Scoreboard and My Picks pages.  This also happens for games on the Make Picks page and users on the Leaderboard.  This saves bandwidth and feels snappier on a fast connection.  The scores and user list are dimmed while the API is loading the data.

APIs
----
I use these MLB baseball APIs:
- [api-sports.io](https://api-sports.io/)
  - Free tier allows 100 requests per day
- [ESPN's hidden API endpoints](https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b)

I may have to switch to just using ESPN's API for this.  api-sports.io still hasn't updated the name of the Cleveland Guardians, still calling them the Indians and the game schedule returned is incomplete, seems to fizzle out in September.  I hope they will fill in the remaining games by then!

Running Tests
-------------

From the pickem directory, run all tests with

    python3 -m unittest

Run a specific test with 

    python3 -m unittest tests/test_thing.py

The test files will have the app load its config from the config_test.toml file.

Running on a Development Machine
--------------------------------

Start Flask at the command line with

    flask --debug run

Deploying on Render
-------------------
- Gunicorn command: `gunicorn --bind=0.0.0.0:$PORT wsgi:app`
  - The app will load its config from the config_live.toml file in production
  - Render sets the port they want you to use in the PORT environment variable

- Set environment variables:
  - `FLASK_SQLALCHEMY_DATABASE_URI` Start URI with `postgrsql://`
  - `FLASK_SECRET_KEY` for secure Flask session cookies.  Set to anything and don't tell anyone.
  - `SPORTS_IO_API_KEY` Get one for baseball at api-sports.io

- Set Postgres timezone to Pacific time
  - On Aiven, go to Service Settings, advanced configuration, add config option: pg.timezone
  - Otherwise, all times are UTC and some games may appear on the Scoreboard under the wrong day.

Future Enhancements
-------------------

- [ ] Add pick statistics page (% of correct picks broken down by home/away team, specific team, etc.)
- [ ] Allow changing pick before the game starts
- [x] Show loading UI when switching scoreboard days
- [ ] Better logging system

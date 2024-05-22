Baseball Pickem
===============

Play [Baseball Pickem](https://baseball-pickem.onrender.com/), hosted at Render.com

How to Play
-----------
This is set up as "do the fun part first."  From the landing page, hit Play Now and make your picks.  From there, sign up or log in to save your picks and check on them later.  Correct picks will earn one point each.  Once logged in, your picks are shown on the My Picks page and you can see who earned the most points on the Leaderboard page by day and the season overall.

Game scores are updated every 20 minutes since the all-sports.io API free tier allows only 100 requests per day.

Under the Hood
--------------
The site is coded in Python using Flask, SQLAlchemy with data stored in a PostgreSQL database.

A feature I'd like to highlight is the games are loaded with JavaScript API calls after Flask returns the HTML for the Scoreboard and My Picks pages.  This also happens for the games on the Make Picks page and the users on the Leaderboard.  This saves bandwidth and feels snappier on a fast connection, though loading and disabling UI would be good to add.

APIs
----
I use these MLB baseball APIs:
- [api-sports.io](https://api-sports.io/)
  - Free tier allows 100 requests per day
- [ESPN's hidden API endpoints](https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b)

I may switch to just using ESPN's API for this, api-sports.io still hasn't updated the name of the Cleveland Guardians, still calling them the Indians and the game schedule returned is incomplete, seems to fizzle out in September.  I hope they will fill in the remaining games by then!

Deploying on Render
-------------------
- Gunicorn command: `gunicorn --bind=0.0.0.0:$PORT app:create_app\(\'config_live\'\)`
  - Have to escape the () and quotes since Render uses bash to run this.  Might be a security issue on their part!
  - Render sets the port they want you to use in the PORT environment variable

- Set environment variables:
  - `FLASK_SQLALCHEMY_DATABASE_URI` Start URI with postgrsql://
  - `FLASK_SECRET_KEY` for secure Flask session cookies.  Set to anything and don't tell anyone.
  - `SPORTS_IO_API_KEY` Get one for baseball at api-sports.io

- Set Postgres timezone to Pacific time
  - On Aiven, go to Service Settings, advanced configuration, add config option: pg.timezone
  - Otherwise, all times are UTC and some games may appear on the Scoreboard under the wrong day.

Future Enhancements
-------------------

- [ ] Add pick statistics page (% of correct picks broken down by home/away team, specific team, etc.)
- [ ] Allow changing pick before the game starts
- [ ] Show loading UI when switching scoreboard days
- [ ] Better logging system
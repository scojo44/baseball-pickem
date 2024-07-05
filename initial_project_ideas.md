Capstone 1 - Project Ideas
=========================

## Geocaching Statistics

For the first idea, this would take a list of geocaches a geocacher has recorded as found on Geocaching.com (often called a "find") and show some statistics and visualizations.

For the data source I would use the MyFinds GPX file that is manually downloaded from the site.  They have an official API but one must apply and get approved to use it.  The MyFinds GPX file has all the data I need.

As an avid geocacher, I would love to do this, capstone or otherwise.  However, interest would be limited to fellow hard-core geocachers.

__What's Geocaching?__  You've seen those guestbooks you're asked to sign when you walk into a building such as a museum or a park's visitor's center?  Now imagine they tell you the guestbook is hidden somewhere outside in the landscaping!  For the official explanation, see [Geocaching 101](https://www.geocaching.com/sites/education/en/) at Geocaching.com.

## Pick-The-Winners Game

My second idea is a site where people can guess which team will win upcoming games in professional sports.  After signup, users are shown a list of upcoming games so they can choose who they think will win for the current day or week.  After some games are finished, they could log in and see how they're doing.  There would also be a leaderboard showing who picked the most games correctly in the time period.

For the data, I could simply poll some JSON URLs at ESPN.com for upcoming games and current scores.  For more in-depth data, thesportsdb.com has quite the comprehensive API for this and other cool possibilities.

While I wouldn't say I'm the biggest sports fan, I've worked with a similar site in the past.  This would be a fun one to do and would appeal to more people.

## Rest Area Finder

A great feature of the old-fashioned paper maps is it's easy to see how far it is to the next rest stop when on a road trip.  In my experience, mapping apps just don't compare.

This idea would be a list of highway rest areas in the USA with the ability to plot them on a map.  Some might be no more than a parking area so it could be helpful to see what features are available, such as:

- Restrooms
- Drinking fountains
- Picnic tables
- Truck parking
- Overnight parking prohibited
- RV dump station

I haven't found an API or dataset of rest stops covering the entire USA, so I would have to collect the data from each of the 50 states.  Each state may have their own dataset so there's going to be a variety of formats.  Worst case is I'd have to look over a paper map and find them myself.  For the capstone, I could limit it to just one or two states with good datasets.

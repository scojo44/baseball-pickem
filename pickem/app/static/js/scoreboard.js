/** List of games for the Scoreboard and My Picks pages */
class ScoreboardList extends DatedList {
  /** Creates a new Scoreboard game list
   * @param {string} initialDate - Optional isoformat date string to load games
   * from a different day than today
   */
  constructor(initialDate = '') {
    super('scoreboard', 'games', initialDate);
  }

  /** Generates an HTML list item for each game
   * @param {Object} game - A user on the leaderboard
   * @returns {Object} <li> element for the game
   */
  processListItem(game) {
    const awayTeamWon = game.winTeamID === game.awayTeam.id;
    const homeTeamWon = game.winTeamID === game.homeTeam.id;
    const tieGame = game.awayTeam.score === game.homeTeam.score;
    let awayPickClass = '';
    let homePickClass = '';
  
    const li = document.createElement('li');
    li.classList.add('game');
  
    // Show the user's picks
    if(game.pick) {
      let pickedAwayTeam = game.pick.teamID === game.awayTeam.id;
      let pickedHomeTeam = game.pick.teamID === game.homeTeam.id;
  
      if(pickedAwayTeam && awayTeamWon || pickedHomeTeam && homeTeamWon)
        li.classList.add('pick-correct');
      else if(game.status === 'Final' && !tieGame)
        li.classList.add('pick-incorrect');
      else
        li.classList.add('pick-pending');
  
      awayPickClass = pickedAwayTeam? 'user-pick':'';
      homePickClass = pickedHomeTeam? 'user-pick':'';
    }
  
    li.innerHTML = this.getGameHTML(game, awayTeamWon, homeTeamWon, awayPickClass, homePickClass);
    return li;
  }
  
  /** Generates an HTML table for each game's info
   * @param {Object} game - A game to display
   * @returns {Object} <table> element for the game
   */
  getGameHTML(game, awayTeamWon, homeTeamWon, awayPickClass, homePickClass) {
    const gameLocalTime = new Date(game.startTime).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit"
    });
    const gameTime = `<time datetime="${game.startTime}">${gameLocalTime}</time>`;
    const gameStatus = game.status === 'Not Started'? gameTime : game.status;

    return `<table>
      <tr>
        <th class="col-9">${gameStatus}</th>
        <th class="runs">R</th>
        <th class="hits">H</th>
        <th class="errors">E</th>
      </tr>
      ${this.getTeamHTML(game.awayTeam, awayTeamWon, game.winTeamID != null, awayPickClass)}
      ${this.getTeamHTML(game.homeTeam, homeTeamWon, game.winTeamID != null, homePickClass)}
    </table>`;
  }
  
  /** Generates an HTML table row for a team's stats
   * @param {Object} team - A team that played the game
   * @param {boolean} isWinner - True if the team won the game
   * @param {boolean} isGameOver - True if the game is over
   * @param {boolean} pickClass - CSS class to style the team name
   * @returns {Object} <tr> element for the team
   */
  getTeamHTML(team, isWinner, isGameOver, pickClass) {
    let loserClass = isGameOver? 'loser':'';
    return `<tr>
      <td class="${isWinner? 'winner' : loserClass} ${pickClass}">
        <img src="${team.logoURL}"> ${team.name}</td>
      <td class="runs">${team.score}</td>
      <td class="hits">${team.hits}</td>
      <td class="errors">${team.errors}</td>
    </tr>`;
  }
  
  /** Shows a message when there's no games returned from the API */
  showNoItemsMsg() {
    this.board.innerHTML = '';
    const li = document.createElement('li');
    li.innerHTML = 'No games on this date';
    this.board.append(li);
  }
}

// Get the list of games on page load
// The My Picks page will have its chosen intial date stored in a data attribute
document.addEventListener('DOMContentLoaded', e => {
  const initialDate = document.getElementById('scoreboard').dataset.initialDate;  // For My Picks page
  new ScoreboardList(initialDate);
});

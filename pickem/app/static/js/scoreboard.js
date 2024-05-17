class ScoreboardList extends DatedList {
  constructor(initialDate = '') {
    super('scoreboard', 'games', initialDate);
  }

  processItem(game) {
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
  
  getGameHTML(game, awayTeamWon, homeTeamWon, awayPickClass, homePickClass) {
    let gameStatus = game.status === 'Not Started'? game.startTime : game.status;

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
}

document.addEventListener('DOMContentLoaded', e => {
  initialDate = document.getElementById('scoreboard').dataset.initialDate;  // For My Picks page
  new ScoreboardList();
});

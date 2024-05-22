document.addEventListener('DOMContentLoaded', async e => {
  const gamesSection = document.getElementById('games-to-pick');
  let gamesToPick;

  try {
    const res = await axios.get('/picksheet/games');
    gamesToPick = res.data.gamesToPick;
  }
  catch(e) {
    console.log('Error fetching games to pick:', e);
    gamesSection.innerHTML = 'No games available';
    return;
  }

  if(gamesToPick[0].games.length == 0 && gamesToPick[1].games.length == 0) {
    gamesSection.innerHTML = 'No games available';
    gamesSection.style.textAlign = 'center';
  }

  for(let list of gamesToPick) {
    processList(list, gamesSection);
  }

  document.getElementById('save-button').addEventListener('click', e => {
    const picksField = document.getElementById('picks');
    const form = document.getElementById('pick-form');
    const radios = document.querySelectorAll('input:checked');
    const picks = [];

    // Collect game selections
    for(let r of radios)
      picks.push({game: r.name, team: r.value});

    picksField.value = JSON.stringify(picks);
    form.submit();
  });
});

function processList(list, gamesSection) {
  if(list.games.length === 0)
    return;

  const dayH5 = document.createElement('h5');
  dayH5.classList.add('date-heading');
  dayH5.innerHTML = list.date;

  const dayUL = document.createElement('ul');
  dayUL.classList.add('games-list');

  for(let game of list.games) {
    const gameLI = document.createElement('li');
    gameLI.classList.add('game');
    gameLI.innerHTML = getGameHTML(game);
    dayUL.append(gameLI);
  }

  gamesSection.append(dayH5);
  gamesSection.append(dayUL);
}

function getGameHTML(game) {
  const gameLocalTime = new Date(game.startTime).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit"
  });

  return `<h6 class="game-heading"><time datetime="${game.startTime}">${gameLocalTime}</time></h6>
  <input type="radio" id="g${game.id}-t${game.awayTeam.id}" name="${game.id}" value="${game.awayTeam.id}">
  <label for="g${game.id}-t${game.awayTeam.id}">
    <img src="${game.awayTeam.logoURL}">
    ${game.awayTeam.location} ${game.awayTeam.name}
  </label>
  <input type="radio" id="g${game.id}-t${game.homeTeam.id}" name="${game.id}" value="${game.homeTeam.id}">
  <label for="g${game.id}-t${game.homeTeam.id}">
    <img src="${game.homeTeam.logoURL}">
    ${game.homeTeam.location} ${game.homeTeam.name}
  </label>`;
}

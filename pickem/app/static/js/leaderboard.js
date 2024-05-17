class Leaderboard extends DatedList {
  constructor() {
    super('leaderboard', 'users');
  }

  processItem(user) {
    const row = document.createElement('tr');
    row.classList.add('user');

    row.innerHTML = this.getUserHTML(user);
    return row;
  }

  getUserHTML(user) {
    return `<td>${user.name}</td>
        <td>${user.points}</td>`;
  }

  showNoItemsMsg() {
    this.board.innerHTML = '';
    const row = document.createElement('tr');
    row.innerHTML = '<td>No users with picks for games on this date.</td>';
    this.board.append(row);
  }
}

document.addEventListener('DOMContentLoaded', e => {
  new Leaderboard();
});

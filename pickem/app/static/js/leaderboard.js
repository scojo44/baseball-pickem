/** List of users for the Leaderboard page */
class Leaderboard extends DatedList {
  /** Creates a new Leaderboard user list */
  constructor() {
    super('leaderboard', 'users');
  }

  /** Generates an HTML table row for each user
   * @param {Object} user - A user on the leaderboard
   * @returns {Object} <tr> element for the user
   */
  processListItem(user) {
    const row = document.createElement('tr');
    row.classList.add('user');
    row.innerHTML = `<td>${user.name}</td><td>${user.points}</td>`;
    return row;
  }

  /** Shows a message when there's no users returned from the API */
  showNoItemsMsg() {
    this.board.innerHTML = '';
    const row = document.createElement('tr');
    row.innerHTML = '<td>No users with picks for games on this date.</td>';
    this.board.append(row);
  }
}

// Get the list of leaderboard users on page load
document.addEventListener('DOMContentLoaded', e => {
  new Leaderboard();
});

/** Base class for getting game and user list data from an API.
 *  The lists can be limted to a single date. */
class DatedList {
  /** Creates a new list
   * @param {string} route - The base API route
   * @param {string} listName - The name of the endpoint and JSON data
   * @param {string} initialDate - The date string in isoformat to initialize the list.  Defaults to today.
   */
  constructor(route, listName, initialDate = '') {
    if(this.constructor == DatedList) {
      throw new Error("Derive a class from DatedList to instantiate.");
    }

    this.route = route;
    this.board = document.getElementById(route);
    this.listName = listName;
    this.initialDate = initialDate;
    this.setupListHeader();

    // Set up the next/previous date links
    for(let link of document.getElementsByClassName('date-link'))
      link.addEventListener('click', async e => {
        e.preventDefault();
        await this.loadFromAPI(link.dataset.date);
      });

    // Use setTimeout to call an awaitable function from the constructor.
    setTimeout(async () => {
      await this.loadFromAPI(initialDate);
    }, 1);
  }

  /** Check if using the date picker widget
   * @returns {boolean} True if using the date picker
   */
  usingDatePicker() {
    return !!document.getElementById('date-picker');
  }

  /** Sets up the date picker heading */
  setupListHeader() {
    if(!this.usingDatePicker()) return;

    document.getElementById('date-label').addEventListener('click', e => {
      document.getElementById('date-picker').showPicker();
    });

    document.getElementById('date-picker').addEventListener('change', async e => {
      await this.loadFromAPI(e.target.value);
    });
  }

  /** Updates the date picker heading
   * @param {object} data - The data from the API response 
   * @param {string} data.nextDay - isoformat date string for the next day button
   * @param {string} data.prevDay - isoformat date string for the previous day button
   * @param {number} data.userPoints - The user's points earned for that current day
   */
  updateListHeader({nextDay, prevDay, userPoints}) {
    if(!this.usingDatePicker()) return;

    const nextLink = document.getElementById('next-date-link');
    const prevLink = document.getElementById('prev-date-link');

    nextLink.dataset.date = nextDay;
    prevLink.dataset.date = prevDay;

    if(userPoints !== undefined)
      document.querySelector('#user-points span').innerHTML = userPoints;
  }

  /** Calls the API to get the list data
   * @param {string} date - Filter data to this date in isoformat (optional)
   */
  async loadFromAPI(date) {
    let items;

    // Add the path seperator if given a date
    if(date)
      date = '/' + date;

    this.toggleLoadingUI();

    // Get the games and scores or users from the API
    try {
      const res = await axios.get(this.route + '/' + this.listName + date);
      items = res.data[this.listName];
      document.getElementById('date-label-text').innerHTML = res.data.dayDisplay;
      this.updateListHeader(res.data);
    }
    catch(e) {
      console.log(`Error fetching ${this.listName} to pick:`, e);
      this.showNoItemsMsg();
      return;
    }
    finally {
      this.toggleLoadingUI();
    }

    if(items.length === 0) {
      this.showNoItemsMsg();
      return;
    }

    // Clear the board
    this.board.innerHTML = '';

    for(let item of items)
      this.board.append(this.processListItem(item));
  }

  toggleLoadingUI() {
    document.querySelectorAll('.block-input').forEach(e => e.classList.toggle('hide'));
  }

  /** Abstract function for subclasses to process list items
   * @param {Object} item - Item in the list to process
   */
  processListItem(item) {
    throw new Error("Method 'processListItem()' must be implemented.");
  }
  
  /** Abstract function to show a message when there's no items returned from the API */
  showNoItemsMsg() {
    throw new Error("Method 'showNoItemsMsg()' must be implemented.");
  }
}

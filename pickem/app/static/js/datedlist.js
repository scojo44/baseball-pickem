class DatedList {
  constructor(page, listName, initialDate = '') {
    if (this.constructor == DatedList) {
      throw new Error("Derive a class from DatedList to instantiate.");
    }

    this.page = page;
    this.board = document.getElementById(page);
    this.listName = listName;
    this.initialDate = initialDate;

    if(this.hasDatePicker())
      this.setupHeading();

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

  hasDatePicker() {
    return !!document.getElementById('date-picker');
  }

  setupHeading() {
    document.getElementById('date-label').addEventListener('click', e => {
      document.getElementById('date-picker').showPicker();
    });

    document.getElementById('date-picker').addEventListener('change', async e => {
      await this.loadFromAPI(e.target.value);
    });
  }

  updateHeading(res) {
    const nextLink = document.getElementById('next-date-link');
    const prevLink = document.getElementById('prev-date-link');

    nextLink.dataset.date = res.data.nextDay;
    prevLink.dataset.date = res.data.prevDay;

    if(res.data.userPoints)
      document.querySelector('#user-points span').innerHTML = res.data.userPoints;
  }

  async loadFromAPI(date) {
    let items;

    if(date)
      date = '/' + date;

    // Get the games and scores or users from the API
    try {
      const res = await axios.get(this.page + '/' + this.listName + date);
      items = res.data[this.listName];

      document.getElementById('date-label-text').innerHTML = res.data.dayDisplay;

      if(this.hasDatePicker())
        this.updateHeading(res);
    }
    catch(e) {
      console.log(`Error fetching ${this.listName} to pick:`, e);
      this.showNoItemsMsg();
      return;
    }

    if(items.length === 0) {
      this.showNoItemsMsg();
      return;
    }

    // Clear the board
    this.board.innerHTML = '';

    for(let item of items)
      this.board.append(this.processItem(item));
  }

  processItem(item) {
    throw new Error("Method 'processItem()' must be implemented.");
  }
  
  showNoItemsMsg() {
    this.board.innerHTML = '';
    const li = document.createElement('li');
    li.innerHTML = 'No games on this date';
    this.board.append(li);
  }
}
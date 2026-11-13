(() => {
    const bell = document.querySelector('#workspace-sidebar .notification-bell');
    if(!bell){
        return;
    }

    const badge = bell.querySelector('.notification-badge');
    let requestVersion = 0;

    function setCount(count) {
        badge.hidden = count === 0;
        badge.textContent = count > 99 ? '99+' : String(count);
        bell.setAttribute('aria-label', count ? `Notifications, ${count} unread` : 'Notifications');
    }

    async function fetchJSON(url, options) {
        const response = await fetch(url, options);
        if(!response.ok){
            throw new Error(`Notification request failed (${response.status})`);
        }
        return response.json();
    }

    async function refreshBadge() {
        const version = ++requestVersion;
        try{
            const feed = await fetchJSON(bell.dataset.feedUrl);
            if(version === requestVersion){
                setCount(feed.unread_count);
            }
        }

        catch(error){
            // Keep the last known badge if the feed cannot be reached.
        }
    }

    const panel = document.querySelector('#notification-panel');
    if(!panel){
        window.addEventListener('focus', refreshBadge);
        window.addEventListener('pageshow', event => {
            if(event.persisted){
                refreshBadge();
            }
        });
        refreshBadge();
        return;
    }

    const status = panel.querySelector('.notification-status');
    const list = panel.querySelector('.notification-list');
    const moreButton = panel.querySelector('.notification-more');
    const moreStatus = panel.querySelector('.notification-more-status');
    const csrf = panel.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    let nextBefore = null;

    function setStatus(message) {
        status.textContent = message;
        status.hidden = !message;
    }

    function notificationItem(notification) {
        const item = document.createElement('li');
        item.className = 'notification-item';
        const title = document.createElement('h2');
        title.textContent = notification.title;
        const detail = document.createElement('p');
        detail.textContent = notification.detail;
        item.append(title, detail);

        if(notification.unread){
            item.classList.add('is-unread');
            const label = document.createElement('span');
            label.className = 'notification-unread-label';
            label.textContent = ' (unread)';
            title.append(label);
        }

        const date = new Date(notification.created_at);
        if(Number.isFinite(date.getTime())){
            const time = document.createElement('time');
            time.dateTime = notification.created_at;
            time.textContent = dateFormat.format(date);
            item.append(time);
        }

        return item;
    }

    async function loadNotifications() {
        let loaded = false;
        try{
            const feed = await fetchJSON(bell.dataset.feedUrl);
            setCount(feed.unread_count);
            list.replaceChildren(...feed.items.map(notificationItem));
            list.hidden = feed.items.length === 0;
            nextBefore = feed.next_before;
            moreButton.hidden = !nextBefore;
            setStatus(feed.items.length ? '' : 'You have no notifications yet.');
            loaded = true;
            if(feed.unread_count && feed.items.length){
                const result = await fetchJSON(panel.dataset.readUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                    body: JSON.stringify({ through_id: feed.items[0].id }),
                });
                setCount(result.unread_count);
            }
        }

        catch(error){
            setStatus(loaded ? 'Could not update the unread count.' : 'Could not load notifications. Refresh to try again.');
        }
    }

    moreButton.addEventListener('click', async () => {
        if(!nextBefore || moreButton.getAttribute('aria-disabled') === 'true'){
            return;
        }
        const url = new URL(bell.dataset.feedUrl, window.location.href);
        url.searchParams.set('before', nextBefore);
        moreButton.setAttribute('aria-disabled', 'true');
        moreStatus.textContent = 'Loading older notifications…';
        moreStatus.hidden = false;
        try{
            const feed = await fetchJSON(url);
            const items = feed.items.map(notificationItem);
            list.append(...items);
            nextBefore = feed.next_before;
            if(document.activeElement === moreButton){
                const firstNewItem = items[0] || list;
                firstNewItem.tabIndex = -1;
                firstNewItem.focus();
            }
            moreButton.hidden = !nextBefore;
            moreStatus.hidden = true;
        }

        catch(error){
            moreStatus.textContent = 'Could not load older notifications. Try again.';
        }

        finally{
            moreButton.removeAttribute('aria-disabled');
        }
    });

    loadNotifications();
})();

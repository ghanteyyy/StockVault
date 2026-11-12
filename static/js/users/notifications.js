(() => {
    const notifications = document.querySelector('.sv-notifications');
    if(!notifications){
        return;
    }

    const bell = notifications.querySelector('.notification-bell');
    const badge = notifications.querySelector('.notification-badge');
    const panel = notifications.querySelector('.notification-panel');
    const closeButton = notifications.querySelector('.notification-close');
    const status = notifications.querySelector('.notification-status');
    const list = notifications.querySelector('.notification-list');
    const csrf = notifications.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    let requestVersion = 0;

    function setCount(count) {
        badge.hidden = count === 0;
        badge.textContent = count > 99 ? '99+' : String(count);
        bell.setAttribute('aria-label', count ? `Notifications, ${count} unread` : 'Notifications');
    }

    function setStatus(message) {
        status.textContent = message;
        status.hidden = !message;
    }

    function notificationItem(notification) {
        const item = document.createElement('li');
        item.className = 'notification-item';
        const title = document.createElement('h3');
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

    async function fetchJSON(url, options) {
        const response = await fetch(url, options);
        if(!response.ok){
            throw new Error(`Notification request failed (${response.status})`);
        }
        return response.json();
    }

    async function refresh(opening = false) {
        const version = ++requestVersion;
        let loaded = false;
        try{
            const feed = await fetchJSON(notifications.dataset.feedUrl);
            if(version !== requestVersion){
                return;
            }
            setCount(feed.unread_count);
            if(!opening || panel.hidden){
                return;
            }

            list.replaceChildren(...feed.items.map(notificationItem));
            list.hidden = feed.items.length === 0;
            setStatus(feed.items.length ? '' : 'You have no notifications yet.');
            loaded = true;
            if(feed.unread_count && feed.items.length){
                const result = await fetchJSON(notifications.dataset.readUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
                    body: JSON.stringify({ through_id: feed.items[0].id }),
                });
                if(version === requestVersion){
                    setCount(result.unread_count);
                }
            }
        }

        catch(error){
            if(opening && !panel.hidden && version === requestVersion){
                setStatus(loaded ? 'Could not update the unread count.' : 'Could not load notifications.');
            }
        }
    }

    function closePanel(restoreFocus = false) {
        panel.hidden = true;
        bell.setAttribute('aria-expanded', 'false');
        if(restoreFocus){
            bell.focus();
        }
    }

    bell.addEventListener('click', () => {
        if(!panel.hidden){
            closePanel();
            return;
        }
        panel.hidden = false;
        bell.setAttribute('aria-expanded', 'true');
        list.hidden = true;
        setStatus('Loading notifications…');
        refresh(true);
    });
    closeButton.addEventListener('click', () => closePanel(true));

    function dismissOutside(event) {
        if(!panel.hidden && !notifications.contains(event.target)){
            closePanel();
        }
    }

    document.addEventListener('click', dismissOutside);
    document.addEventListener('focusin', dismissOutside);
    document.addEventListener('keydown', event => {
        if(!panel.hidden && !event.defaultPrevented && event.key === 'Escape'){
            event.preventDefault();
            closePanel(true);
        }
    });
    window.addEventListener('focus', () => {
        if(panel.hidden){
            refresh();
        }
    });

    refresh();
})();

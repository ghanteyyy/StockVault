(() => {
    const sidebar = document.querySelector('#workspace-sidebar');
    const panel = sidebar?.querySelector('#notification-panel');
    if(!panel){
        return;
    }

    const bell = sidebar.querySelector('.notification-bell');
    const badge = bell.querySelector('.notification-badge');
    const closeButton = panel.querySelector('.notification-close');
    const status = panel.querySelector('.notification-status');
    const list = panel.querySelector('.notification-list');
    const moreButton = panel.querySelector('.notification-more');
    const moreStatus = panel.querySelector('.notification-more-status');
    const csrf = panel.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    let requestVersion = 0;
    let nextBefore = null;

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
            const feed = await fetchJSON(panel.dataset.feedUrl);
            if(version !== requestVersion){
                return;
            }
            setCount(feed.unread_count);
            if(!opening || panel.hidden){
                return;
            }

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

    moreButton.addEventListener('click', async () => {
        if(!nextBefore || moreButton.getAttribute('aria-disabled') === 'true'){
            return;
        }
        const version = requestVersion;
        const url = new URL(panel.dataset.feedUrl, window.location.href);
        url.searchParams.set('before', nextBefore);
        moreButton.setAttribute('aria-disabled', 'true');
        moreStatus.textContent = 'Loading older notifications…';
        moreStatus.hidden = false;
        try{
            const feed = await fetchJSON(url);
            if(version !== requestVersion || panel.hidden){
                return;
            }
            list.append(...feed.items.map(notificationItem));
            nextBefore = feed.next_before;
            if(!nextBefore && document.activeElement === moreButton){
                list.focus({ preventScroll: true });
            }
            moreButton.hidden = !nextBefore;
            moreStatus.hidden = true;
        }

        catch(error){
            if(version === requestVersion && !panel.hidden){
                moreStatus.textContent = 'Could not load older notifications. Try again.';
            }
        }

        finally{
            if(version === requestVersion){
                moreButton.removeAttribute('aria-disabled');
            }
        }
    });

    function closePanel(restoreFocus = false) {
        if(panel.hidden){
            return;
        }
        panel.hidden = true;
        sidebar.classList.remove('notifications-open');
        bell.setAttribute('aria-expanded', 'false');
        if(restoreFocus){
            bell.focus();
        }
    }

    bell.addEventListener('click', () => {
        panel.hidden = false;
        sidebar.classList.add('notifications-open');
        bell.setAttribute('aria-expanded', 'true');
        list.hidden = true;
        moreButton.hidden = true;
        moreButton.removeAttribute('aria-disabled');
        moreStatus.hidden = true;
        nextBefore = null;
        setStatus('Loading notifications…');
        closeButton.focus();
        refresh(true);
    });
    closeButton.addEventListener('click', () => closePanel(true));
    sidebar.addEventListener('stockvault:sidebar-closed', () => closePanel());
    sidebar.addEventListener('keydown', event => {
        if(!panel.hidden && event.key === 'Escape'){
            event.preventDefault();
            event.stopPropagation();
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

(function () {
    const transitionDuration = 170;

    function isNormalClick(event) {
        return event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;
    }

    function shouldTransition(link) {
        if (!link || !link.href || link.target || link.hasAttribute("download")) return false;
        if (link.href.startsWith("javascript:")) return false;

        const nextUrl = new URL(link.href, window.location.href);
        const currentUrl = new URL(window.location.href);

        if (nextUrl.origin !== currentUrl.origin) return false;
        if (nextUrl.pathname === currentUrl.pathname && nextUrl.search === currentUrl.search && nextUrl.hash) return false;

        return true;
    }

    document.addEventListener("click", function (event) {
        const link = event.target.closest("a");

        if (!isNormalClick(event) || !shouldTransition(link)) return;

        event.preventDefault();
        document.body.classList.add("page-leaving");

        window.setTimeout(function () {
            window.location.href = link.href;
        }, transitionDuration);
    });
})();

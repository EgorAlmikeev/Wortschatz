(function () {
    if (!requireAuth()) {
        return;
    }

    const PART_OF_SPEECH = [
        [1, "Существительное"],
        [2, "Глагол"],
        [3, "Прилагательное"],
        [4, "Местоимение"],
        [5, "Наречие"],
        [6, "Предлог"],
        [7, "Числительное"],
        [8, "Артикль"],
        [9, "Союз"],
        [10, "Междометие"],
    ];

    const GENUS_ARTICLE = { 1: "der", 2: "die", 3: "das", 4: "die" };
    const PART_OF_SPEECH_LABEL = Object.fromEntries(PART_OF_SPEECH);

    const PAGE_SIZE = 12;

    const els = {
        searchInput: document.getElementById("search-input"),
        filterToggle: document.getElementById("filter-toggle"),
        filterPanel: document.getElementById("filter-panel"),
        filterPartOfSpeech: document.getElementById("filter-part-of-speech"),
        filterDateFrom: document.getElementById("filter-date-from"),
        filterDateTo: document.getElementById("filter-date-to"),
        filterApply: document.getElementById("filter-apply"),
        filterReset: document.getElementById("filter-reset"),
        resultsCount: document.getElementById("results-count"),
        wordGrid: document.getElementById("word-grid"),
        emptyState: document.getElementById("empty-state"),
        pagination: document.getElementById("pagination"),
        prevPage: document.getElementById("prev-page"),
        nextPage: document.getElementById("next-page"),
        pageIndicator: document.getElementById("page-indicator"),
        cardTemplate: document.getElementById("word-card-template"),
        fab: document.getElementById("add-word-fab"),
        gameBtn: document.getElementById("game-btn"),
        testBtn: document.getElementById("test-btn"),
    };

    const state = {
        page: 1,
        search: "",
        partOfSpeechId: "",
        dateFrom: "",
        dateTo: "",
    };

    const cardsById = new Map();
    let currentWords = [];

    function initPartOfSpeechOptions() {
        for (const [id, label] of PART_OF_SPEECH) {
            const option = document.createElement("option");
            option.value = String(id);
            option.textContent = label;
            els.filterPartOfSpeech.appendChild(option);
        }
    }

    function buildQuery() {
        const params = new URLSearchParams();
        params.set("page", String(state.page));
        params.set("page_size", String(PAGE_SIZE));
        if (state.search) params.set("definition", state.search);
        if (state.partOfSpeechId) params.set("part_of_speech_id", state.partOfSpeechId);
        if (state.dateFrom) params.set("created_date_time_after", state.dateFrom);
        if (state.dateTo) params.set("created_date_time_before", state.dateTo);
        return params.toString();
    }

    function formatDate(isoString) {
        const date = new Date(isoString);
        if (Number.isNaN(date.getTime())) return "";
        return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
    }

    function makePill(text, muted) {
        const span = document.createElement("span");
        span.className = muted ? "pill pill-muted" : "pill pill-mint";
        span.textContent = text;
        return span;
    }

    function fitTranslations(container, translations, totalCount) {
        container.innerHTML = "";
        if (!translations.length) {
            return;
        }

        translations.forEach((text) => container.appendChild(makePill(text)));

        const hasMoreOnServer = totalCount > translations.length;
        const ellipsis = makePill("…", true);

        function isOverflowing() {
            return container.scrollWidth > container.clientWidth + 1;
        }

        if (hasMoreOnServer) {
            container.appendChild(ellipsis);
        }

        while (isOverflowing() && container.children.length > 0) {
            const last = container.lastElementChild;
            if (last === ellipsis) {
                container.removeChild(ellipsis);
            }
            const lastPill = container.lastElementChild;
            if (!lastPill) break;
            container.removeChild(lastPill);
            if (!container.contains(ellipsis)) {
                container.appendChild(ellipsis);
            }
        }

        if (container.children.length === 0 && translations.length > 0) {
            // Not even one pill fits: show the first translation as plain truncated text.
            const fallback = makePill(translations[0]);
            container.appendChild(fallback);
        }
    }

    function buildCard(word) {
        const fragment = els.cardTemplate.content.cloneNode(true);
        const card = fragment.querySelector(".word-card");
        const genusEl = card.querySelector(".word-genus");
        const definitionEl = card.querySelector(".word-definition");
        const translationsEl = card.querySelector(".word-translations");
        const posEl = card.querySelector(".word-pos");
        const dotEl = card.querySelector(".word-dot");
        const dateEl = card.querySelector(".word-date");

        definitionEl.textContent = word.definition;

        const article = GENUS_ARTICLE[word.genus_id];
        if (article) {
            genusEl.textContent = article;
            genusEl.hidden = false;
        }

        const posLabel = PART_OF_SPEECH_LABEL[word.part_of_speech_id] || "";
        posEl.textContent = posLabel;
        dateEl.textContent = formatDate(word.created_date_time);
        dotEl.hidden = !posLabel;

        fitTranslations(translationsEl, word.translation_previews || [], word.translations_count || 0);

        return card;
    }

    function renderWords(words) {
        currentWords = words;
        cardsById.clear();
        els.wordGrid.innerHTML = "";

        words.forEach((word) => {
            const card = buildCard(word);
            cardsById.set(word.id, card);
            els.wordGrid.appendChild(card);
        });
    }

    function refitAllTranslations() {
        currentWords.forEach((word) => {
            const card = cardsById.get(word.id);
            if (!card) return;
            const translationsEl = card.querySelector(".word-translations");
            fitTranslations(translationsEl, word.translation_previews || [], word.translations_count || 0);
        });
    }

    let resizeTimer = null;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(refitAllTranslations, 150);
    });

    async function loadWords() {
        els.resultsCount.textContent = "Загрузка…";

        try {
            const response = await apiFetch(`/api/words/?${buildQuery()}`);
            if (!response.ok) {
                els.resultsCount.textContent = "Не удалось загрузить слова";
                return;
            }

            const data = await response.json();
            renderWords(data.results);

            els.resultsCount.textContent = `Найдено слов: ${data.count}`;
            els.emptyState.hidden = data.count !== 0;
            els.wordGrid.hidden = data.count === 0;

            const totalPages = Math.max(1, Math.ceil(data.count / PAGE_SIZE));
            els.pagination.hidden = totalPages <= 1;
            els.pageIndicator.textContent = `Страница ${state.page} из ${totalPages}`;
            els.prevPage.disabled = !data.previous;
            els.nextPage.disabled = !data.next;

            requestAnimationFrame(refitAllTranslations);
        } catch (err) {
            els.resultsCount.textContent = "Не удалось загрузить слова";
        }
    }

    let searchTimer = null;
    els.searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            state.search = els.searchInput.value.trim();
            state.page = 1;
            loadWords();
        }, 300);
    });

    els.filterToggle.addEventListener("click", () => {
        const isHidden = els.filterPanel.hidden;
        els.filterPanel.hidden = !isHidden;
        els.filterToggle.classList.toggle("is-active", isHidden);
    });

    els.filterApply.addEventListener("click", () => {
        state.partOfSpeechId = els.filterPartOfSpeech.value;
        state.dateFrom = els.filterDateFrom.value;
        state.dateTo = els.filterDateTo.value;
        state.page = 1;
        loadWords();
    });

    els.filterReset.addEventListener("click", () => {
        els.filterPartOfSpeech.value = "";
        els.filterDateFrom.value = "";
        els.filterDateTo.value = "";
        state.partOfSpeechId = "";
        state.dateFrom = "";
        state.dateTo = "";
        state.page = 1;
        loadWords();
    });

    els.prevPage.addEventListener("click", () => {
        if (state.page > 1) {
            state.page -= 1;
            loadWords();
        }
    });

    els.nextPage.addEventListener("click", () => {
        state.page += 1;
        loadWords();
    });

    function comingSoon() {
        showToast("Скоро будет доступно");
    }

    els.gameBtn.addEventListener("click", comingSoon);
    els.testBtn.addEventListener("click", comingSoon);
    els.fab.addEventListener("click", comingSoon);

    document.querySelectorAll('[data-nav="collections"], [data-nav="profile"]').forEach((btn) => {
        btn.addEventListener("click", comingSoon);
    });

    document.getElementById("logout-desktop").addEventListener("click", () => Auth.logout());
    document.getElementById("logout-mobile").addEventListener("click", () => Auth.logout());

    initPartOfSpeechOptions();
    loadWords();
})();

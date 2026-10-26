/**
 * Shared word-grid page logic: search, filters, pagination and the word
 * detail modal. Used as-is by the home page ("Мои слова") and, scoped to a
 * single collection via `collectionId`, by the collection detail page — so
 * both stay in sync without duplicating this logic.
 */
const WordList = (function () {
    const PAGE_SIZE = 12;

    function init(options) {
        options = options || {};
        const collectionId = options.collectionId || null;

        if (!requireAuth()) {
            return;
        }

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
            modalOverlay: document.getElementById("word-modal-overlay"),
            modalDialog: document.getElementById("word-modal"),
            modalBack: document.getElementById("modal-back"),
            modalClose: document.getElementById("modal-close"),
            modalEdit: document.getElementById("modal-edit"),
            modalGenus: document.getElementById("modal-genus"),
            modalDefinition: document.getElementById("modal-definition"),
            modalPos: document.getElementById("modal-pos"),
            modalLoading: document.getElementById("modal-loading"),
            modalSections: document.getElementById("modal-sections"),
            modalEmpty: document.getElementById("modal-empty"),
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
        let currentModalWord = null;

        function initPartOfSpeechOptions() {
            for (const [id, label] of WordDetail.PART_OF_SPEECH) {
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
            if (collectionId) params.set("collection_id", collectionId);
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

            const article = WordDetail.genusArticle(word.genus_id);
            if (article) {
                genusEl.textContent = article;
                genusEl.hidden = false;
            }

            const posLabel = WordDetail.posLabel(word.part_of_speech_id);
            posEl.textContent = posLabel;
            dateEl.textContent = formatDate(word.created_date_time);
            dotEl.hidden = !posLabel;

            fitTranslations(translationsEl, word.translation_previews || [], word.translations_count || 0);

            card.tabIndex = 0;
            card.setAttribute("role", "button");
            card.addEventListener("click", () => openWordModal(word.id));
            card.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    openWordModal(word.id);
                }
            });

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

        function closeWordModal() {
            els.modalOverlay.classList.remove("is-open");
            document.body.style.overflow = "";
            setTimeout(() => {
                els.modalOverlay.hidden = true;
            }, 200);
        }

        async function openWordModal(wordId) {
            els.modalOverlay.hidden = false;
            document.body.style.overflow = "hidden";
            requestAnimationFrame(() => els.modalOverlay.classList.add("is-open"));

            els.modalLoading.hidden = false;
            els.modalSections.hidden = true;
            els.modalEmpty.hidden = true;
            els.modalSections.innerHTML = "";
            els.modalDefinition.textContent = "";
            els.modalPos.textContent = "";
            els.modalGenus.hidden = true;
            currentModalWord = null;

            try {
                const response = await apiFetch(`/api/words/${wordId}/`);
                if (!response.ok) {
                    closeWordModal();
                    showToast("Не удалось загрузить слово");
                    return;
                }
                const word = await response.json();
                currentModalWord = word;

                els.modalDefinition.textContent = word.definition;
                const article = WordDetail.genusArticle(word.genus_id);
                if (article) {
                    els.modalGenus.textContent = article;
                    els.modalGenus.hidden = false;
                }
                els.modalPos.textContent = WordDetail.posLabel(word.part_of_speech_id);

                const sections = WordDetail.buildSections(word);

                els.modalLoading.hidden = true;

                if (sections.length === 0) {
                    els.modalEmpty.hidden = false;
                    return;
                }

                sections.forEach((section) => els.modalSections.appendChild(section));
                els.modalSections.hidden = false;
            } catch (err) {
                closeWordModal();
                showToast("Не удалось загрузить слово");
            }
        }

        els.modalBack.addEventListener("click", closeWordModal);
        els.modalClose.addEventListener("click", closeWordModal);
        els.modalEdit.addEventListener("click", () => {
            if (!currentModalWord) {
                return;
            }
            const wordToEdit = currentModalWord;
            closeWordModal();
            AddWord.openForEdit(wordToEdit, () => loadWords());
        });
        els.modalOverlay.addEventListener("click", (event) => {
            if (event.target === els.modalOverlay) {
                closeWordModal();
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !els.modalOverlay.hidden) {
                closeWordModal();
            }
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
        els.fab.addEventListener("click", () => AddWord.open(() => loadWords()));

        document.querySelectorAll('[data-nav="home"]').forEach((btn) => {
            btn.addEventListener("click", () => {
                if (window.location.pathname !== "/") {
                    window.location.href = "/";
                }
            });
        });

        document.querySelectorAll('[data-nav="collections"]').forEach((btn) => {
            btn.addEventListener("click", () => {
                window.location.href = "/collections/";
            });
        });

        document.querySelectorAll('[data-nav="profile"]').forEach((btn) => {
            btn.addEventListener("click", () => {
                window.location.href = "/profile/";
            });
        });

        AddWord.init({ collectionId });

        initPartOfSpeechOptions();
        loadWords();
    }

    return { init };
})();

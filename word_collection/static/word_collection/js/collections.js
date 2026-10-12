(function () {
    if (!requireAuth()) {
        return;
    }

    const MAX_VISIBLE_TAGS = 2;

    const els = {
        searchInput: document.getElementById("search-input"),
        filterToggle: document.getElementById("filter-toggle"),
        filterPanel: document.getElementById("filter-panel"),
        categoryChips: document.getElementById("category-chips"),
        filterApply: document.getElementById("filter-apply"),
        filterReset: document.getElementById("filter-reset"),
        collectionGrid: document.getElementById("collection-grid"),
        emptyState: document.getElementById("empty-state"),
        cardTemplate: document.getElementById("collection-card-template"),
        fab: document.getElementById("add-collection-fab"),
    };

    const state = {
        search: "",
        tagIds: [],
    };

    function buildQuery() {
        const params = new URLSearchParams();
        if (state.search) params.set("name", state.search);
        if (state.tagIds.length) params.set("tag_id", state.tagIds.join(","));
        return params.toString();
    }

    function makeOverlayChip(text) {
        const span = document.createElement("span");
        span.className = "chip-overlay";
        span.textContent = text;
        return span;
    }

    function buildCard(collection) {
        const fragment = els.cardTemplate.content.cloneNode(true);
        const card = fragment.querySelector(".collection-card");
        const media = card.querySelector(".collection-card-media");
        const titleEl = card.querySelector(".collection-card-title");
        const descriptionEl = card.querySelector(".collection-card-description");
        const tagsEl = card.querySelector(".collection-card-tags");
        const countEl = card.querySelector(".collection-card-count");

        media.style.background = collection.background_color
            ? collection.background_color
            : "linear-gradient(135deg, var(--lavender) 0%, var(--mint) 100%)";

        titleEl.textContent = collection.name;
        descriptionEl.textContent = collection.description || "";
        descriptionEl.hidden = !collection.description;

        const tags = collection.tags || [];
        tags.slice(0, MAX_VISIBLE_TAGS).forEach((tag) => {
            tagsEl.appendChild(makeOverlayChip(tag.name));
        });
        if (tags.length > MAX_VISIBLE_TAGS) {
            tagsEl.appendChild(makeOverlayChip(`+${tags.length - MAX_VISIBLE_TAGS}`));
        }

        const wordCount = (collection.words || []).length;
        countEl.textContent = `${wordCount} ${pluralizeRu(wordCount, ["слово", "слова", "слов"])}`;

        card.tabIndex = 0;
        card.setAttribute("role", "button");
        const openCollection = () => {
            window.location.href = `/collections/${collection.id}/`;
        };
        card.addEventListener("click", openCollection);
        card.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openCollection();
            }
        });

        return card;
    }

    function renderCollections(collections) {
        els.collectionGrid.innerHTML = "";
        collections.forEach((collection) => {
            els.collectionGrid.appendChild(buildCard(collection));
        });
        els.emptyState.hidden = collections.length !== 0;
        els.collectionGrid.hidden = collections.length === 0;
    }

    async function loadCollections() {
        try {
            const response = await apiFetch(`/api/collections/?${buildQuery()}`);
            if (!response.ok) {
                showToast("Не удалось загрузить коллекции");
                return;
            }
            const collections = await response.json();
            renderCollections(collections);
        } catch (err) {
            showToast("Не удалось загрузить коллекции");
        }
    }

    async function loadCategoryChips() {
        try {
            const response = await apiFetch("/api/tags/");
            if (!response.ok) return;
            const tags = await response.json();
            els.categoryChips.innerHTML = "";
            tags.forEach((tag) => {
                const chip = document.createElement("button");
                chip.type = "button";
                chip.className = "category-chip";
                chip.textContent = tag.name;
                chip.dataset.tagId = String(tag.id);
                chip.addEventListener("click", () => {
                    chip.classList.toggle("is-selected");
                });
                els.categoryChips.appendChild(chip);
            });
        } catch (err) {
            // Filter panel just stays empty; search/list still work.
        }
    }

    let searchTimer = null;
    els.searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
            state.search = els.searchInput.value.trim();
            loadCollections();
        }, 300);
    });

    els.filterToggle.addEventListener("click", () => {
        const isHidden = els.filterPanel.hidden;
        els.filterPanel.hidden = !isHidden;
        els.filterToggle.classList.toggle("is-active", isHidden);
    });

    els.filterApply.addEventListener("click", () => {
        state.tagIds = Array.from(els.categoryChips.querySelectorAll(".category-chip.is-selected")).map(
            (chip) => chip.dataset.tagId
        );
        loadCollections();
    });

    els.filterReset.addEventListener("click", () => {
        els.categoryChips.querySelectorAll(".category-chip.is-selected").forEach((chip) => {
            chip.classList.remove("is-selected");
        });
        state.tagIds = [];
        loadCollections();
    });

    function comingSoon() {
        showToast("Скоро будет доступно");
    }

    els.fab.addEventListener("click", comingSoon);

    document.querySelectorAll('[data-nav="home"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.href = "/";
        });
    });

    document.querySelectorAll('[data-nav="profile"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.href = "/profile/";
        });
    });

    loadCategoryChips();
    loadCollections();
})();

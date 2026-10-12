(function () {
    if (!requireAuth()) {
        return;
    }

    const heroEl = document.getElementById("collection-hero");
    const collectionId = heroEl.dataset.collectionId;

    const els = {
        back: document.getElementById("hero-back"),
        edit: document.getElementById("hero-edit"),
        title: document.getElementById("hero-title"),
        description: document.getElementById("hero-description"),
        tags: document.getElementById("hero-tags"),
        count: document.getElementById("hero-count"),
    };

    function makeOverlayChip(text) {
        const span = document.createElement("span");
        span.className = "chip-overlay";
        span.textContent = text;
        return span;
    }

    function comingSoon() {
        showToast("Скоро будет доступно");
    }

    els.back.addEventListener("click", () => {
        window.location.href = "/collections/";
    });
    els.edit.addEventListener("click", comingSoon);

    async function loadCollection() {
        try {
            const response = await apiFetch(`/api/collections/${collectionId}/`);
            if (!response.ok) {
                showToast("Коллекция не найдена");
                window.location.href = "/collections/";
                return;
            }
            const collection = await response.json();

            heroEl.style.background = collection.background_color
                ? collection.background_color
                : "linear-gradient(135deg, var(--lavender) 0%, var(--mint) 100%)";

            els.title.textContent = collection.name;
            document.title = `${collection.name} — Wortschatz`;

            if (collection.description) {
                els.description.textContent = collection.description;
                els.description.hidden = false;
            }

            (collection.tags || []).forEach((tag) => {
                els.tags.appendChild(makeOverlayChip(tag.name));
            });

            const wordCount = (collection.words || []).length;
            els.count.textContent = `${wordCount} ${pluralizeRu(wordCount, ["слово", "слова", "слов"])}`;
        } catch (err) {
            showToast("Коллекция не найдена");
            window.location.href = "/collections/";
        }
    }

    loadCollection();
    WordList.init({ collectionId });
})();

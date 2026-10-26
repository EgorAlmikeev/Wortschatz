/**
 * "Add collection" modal, opened from the FAB on the collections page.
 * Creates the collection via POST /api/collections/ (name/description/
 * background_color are plain writable fields), then attaches any selected
 * tags via the dedicated add_tag sub-resource endpoint — collection.tags is
 * read-only on CollectionSerializer, so posting tags directly is ignored.
 *
 * The "Категории" picker doubles as a small tag manager: picking an existing
 * tag just marks it for attachment, but creating a new one (POST /api/tags/)
 * and deleting one (DELETE /api/tags/{id}/) happen immediately against the
 * user's tag library, independent of whether this form ends up submitted.
 */
const AddCollection = (function () {
    const COLOR_SWATCHES = ["#a9e8ce", "#cab9f7", "#ffd2ad", "#f6c9d6", "#b9c6f8", "#f7e39a"];
    // Tag.name: max_length=50
    const TAG_NAME_MAX_LENGTH = 50;

    const TRASH_ICON =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path><path d="M10 11v6"></path><path d="M14 11v6"></path></svg>';

    // Used instead of a text "×" glyph for the pill remove button: a glyph's
    // ink isn't centered within its own line box, so even a perfectly
    // flex-centered box makes it look visually off-center next to the tag
    // name. An SVG has no such metrics quirk.
    const CLOSE_ICON =
        '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>';

    let onSavedCallback = null;
    let els = null;

    let allTags = [];
    let selectedTagIds = new Set();
    let selectedColor = null;
    let initialSnapshot = null;
    let closeConfirmInFlight = false;

    function init() {
        const overlay = document.getElementById("add-collection-modal-overlay");
        if (!overlay) {
            return;
        }

        els = {
            overlay,
            back: document.getElementById("add-collection-back"),
            close: document.getElementById("add-collection-close"),
            submit: document.getElementById("add-collection-submit"),
            error: document.getElementById("add-collection-error"),
            name: document.getElementById("add-collection-name"),
            description: document.getElementById("add-collection-description"),
            tagsToggle: document.getElementById("add-collection-tags-toggle"),
            selectedTags: document.getElementById("add-collection-selected-tags"),
            tagsPanel: document.getElementById("add-collection-tags-panel"),
            tagSearch: document.getElementById("add-collection-tag-search"),
            createTagBtn: document.getElementById("add-collection-create-tag"),
            tagList: document.getElementById("add-collection-tag-list"),
            tagsEmpty: document.getElementById("add-collection-tags-empty"),
            colors: document.getElementById("add-collection-colors"),
        };

        // Collection.name: max_length=100, Collection.description: max_length=200
        wireLengthLimit(els.name);
        wireLengthLimit(els.description);
        wireLengthLimit(els.tagSearch);

        COLOR_SWATCHES.forEach((color) => {
            const swatch = document.createElement("button");
            swatch.type = "button";
            swatch.className = "color-swatch";
            swatch.style.background = color;
            swatch.dataset.color = color;
            swatch.title = color;
            swatch.addEventListener("click", () => {
                selectedColor = selectedColor === color ? null : color;
                renderColors();
            });
            els.colors.appendChild(swatch);
        });

        els.back.addEventListener("click", requestClose);
        els.close.addEventListener("click", requestClose);
        els.overlay.addEventListener("click", (event) => {
            if (event.target === els.overlay) {
                requestClose();
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !els.overlay.hidden) {
                requestClose();
            }
        });

        els.tagsToggle.addEventListener("click", () => {
            els.tagsPanel.hidden = !els.tagsPanel.hidden;
            if (!els.tagsPanel.hidden) {
                els.tagSearch.focus();
            }
        });

        els.tagSearch.addEventListener("input", renderTagList);
        els.createTagBtn.addEventListener("click", openCreateTagDialog);

        els.submit.addEventListener("click", submit);
    }

    function wireLengthLimit(input) {
        const update = () => {
            input.classList.toggle("input-limit-reached", input.value.length >= input.maxLength);
        };
        input.addEventListener("input", update);
        update();
    }

    function renderColors() {
        els.colors.querySelectorAll(".color-swatch").forEach((swatch) => {
            swatch.classList.toggle("is-selected", swatch.dataset.color === selectedColor);
        });
    }

    function renderSelectedTags() {
        els.selectedTags.innerHTML = "";
        allTags
            .filter((tag) => selectedTagIds.has(tag.id))
            .forEach((tag) => {
                const pill = document.createElement("span");
                pill.className = "pill pill-mint tag-pill";

                const label = document.createElement("span");
                label.textContent = tag.name;
                pill.appendChild(label);

                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.className = "tag-pill-remove";
                removeBtn.title = "Убрать";
                removeBtn.innerHTML = CLOSE_ICON;
                removeBtn.addEventListener("click", () => {
                    selectedTagIds.delete(tag.id);
                    renderSelectedTags();
                    renderTagList();
                });
                pill.appendChild(removeBtn);

                els.selectedTags.appendChild(pill);
            });
    }

    function renderTagList() {
        const query = els.tagSearch.value.trim().toLowerCase();
        const filtered = query ? allTags.filter((tag) => tag.name.toLowerCase().includes(query)) : allTags;

        els.tagList.innerHTML = "";
        filtered.forEach((tag) => {
            const row = document.createElement("div");
            row.className = "tag-picker-row";
            row.classList.toggle("is-selected", selectedTagIds.has(tag.id));

            const name = document.createElement("span");
            name.textContent = tag.name;
            row.appendChild(name);

            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "form-repeat-remove";
            deleteBtn.title = "Удалить категорию";
            deleteBtn.innerHTML = TRASH_ICON;
            deleteBtn.addEventListener("click", (event) => {
                event.stopPropagation();
                deleteTag(tag);
            });
            row.appendChild(deleteBtn);

            row.addEventListener("click", () => {
                if (selectedTagIds.has(tag.id)) {
                    selectedTagIds.delete(tag.id);
                } else {
                    selectedTagIds.add(tag.id);
                }
                renderSelectedTags();
                renderTagList();
            });

            els.tagList.appendChild(row);
        });

        els.tagsEmpty.hidden = filtered.length > 0;
    }

    async function openCreateTagDialog() {
        const name = await promptDialog({
            title: "Новая категория",
            label: "Название категории",
            placeholder: "Введите название",
            submitText: "Создать",
            maxLength: TAG_NAME_MAX_LENGTH,
        });
        if (!name) {
            return;
        }

        // Typed name matches an existing tag exactly — just select it
        // instead of creating a duplicate.
        const existing = allTags.find((tag) => tag.name.toLowerCase() === name.toLowerCase());
        if (existing) {
            selectedTagIds.add(existing.id);
            renderSelectedTags();
            renderTagList();
            return;
        }

        try {
            const response = await apiFetch("/api/tags/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name }),
            });
            if (!response.ok) {
                showToast("Не удалось создать категорию");
                return;
            }
            const tag = await response.json();
            allTags.push(tag);
            selectedTagIds.add(tag.id);
            renderSelectedTags();
            renderTagList();
        } catch (err) {
            showToast("Не удалось создать категорию");
        }
    }

    async function deleteTag(tag) {
        const confirmed = await confirmDialog({
            message: `Удалить категорию «${tag.name}»? Она пропадёт из всех коллекций.`,
            confirmText: "Удалить",
            cancelText: "Отмена",
            danger: true,
        });
        if (!confirmed) {
            return;
        }
        try {
            const response = await apiFetch(`/api/tags/${tag.id}/`, { method: "DELETE" });
            if (!response.ok) {
                showToast("Не удалось удалить категорию");
                return;
            }
            allTags = allTags.filter((t) => t.id !== tag.id);
            selectedTagIds.delete(tag.id);
            renderSelectedTags();
            renderTagList();
        } catch (err) {
            showToast("Не удалось удалить категорию");
        }
    }

    async function loadTags() {
        try {
            const response = await apiFetch("/api/tags/");
            allTags = response.ok ? await response.json() : [];
        } catch (err) {
            allTags = [];
        }
        renderSelectedTags();
        renderTagList();
    }

    function getFormSnapshot() {
        return JSON.stringify({
            name: els.name.value.trim(),
            description: els.description.value.trim(),
            color: selectedColor,
            tagIds: Array.from(selectedTagIds).sort((a, b) => a - b),
        });
    }

    function isDirty() {
        return initialSnapshot !== null && getFormSnapshot() !== initialSnapshot;
    }

    function resetForm() {
        els.error.classList.remove("is-visible");
        els.name.value = "";
        els.description.value = "";
        els.tagSearch.value = "";
        els.tagsPanel.hidden = true;
        els.createTagBtn.textContent = "Создать новую категорию";
        selectedTagIds = new Set();
        selectedColor = COLOR_SWATCHES[0];
        renderColors();
    }

    function showError(message) {
        els.error.textContent = message;
        els.error.classList.add("is-visible");
    }

    function showModal() {
        els.overlay.hidden = false;
        document.body.style.overflow = "hidden";
        requestAnimationFrame(() => els.overlay.classList.add("is-open"));
    }

    function hideModal() {
        els.overlay.classList.remove("is-open");
        document.body.style.overflow = "";
        setTimeout(() => {
            els.overlay.hidden = true;
        }, 200);
    }

    function open(onSaved) {
        if (!els) {
            return;
        }
        onSavedCallback = onSaved || null;
        resetForm();
        initialSnapshot = getFormSnapshot();
        showModal();
        loadTags();
    }

    async function requestClose() {
        if (closeConfirmInFlight) {
            return;
        }
        if (!isDirty()) {
            hideModal();
            return;
        }
        closeConfirmInFlight = true;
        const confirmed = await confirmDialog({
            message: "Внесённые изменения будут потеряны. Продолжить?",
            confirmText: "Да",
            cancelText: "Нет",
            danger: true,
        });
        closeConfirmInFlight = false;
        if (confirmed) {
            hideModal();
        }
    }

    async function submit() {
        els.error.classList.remove("is-visible");

        const name = els.name.value.trim();
        if (!name) {
            showError("Укажите название коллекции.");
            return;
        }

        els.submit.disabled = true;

        try {
            const response = await apiFetch("/api/collections/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name,
                    description: els.description.value.trim() || null,
                    background_color: selectedColor,
                }),
            });

            if (!response.ok) {
                showError("Не удалось сохранить коллекцию. Попробуйте ещё раз.");
                return;
            }

            const collection = await response.json();

            await Promise.all(
                Array.from(selectedTagIds).map((tagId) =>
                    apiFetch(`/api/collections/${collection.id}/add_tag/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ tag_id: tagId }),
                    })
                )
            );

            hideModal();
            showToast("Коллекция добавлена");
            if (onSavedCallback) {
                onSavedCallback();
            }
        } catch (err) {
            showError("Не удалось сохранить коллекцию. Попробуйте ещё раз.");
        } finally {
            els.submit.disabled = false;
        }
    }

    return { init, open };
})();

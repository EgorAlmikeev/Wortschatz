/**
 * Shared "add/edit word" modal: opened from the FAB (add mode) or from the
 * "edit" button on the word detail popup (edit mode). Add mode creates the
 * word via POST /api/words/, then fills in its translations/examples/
 * forms/prepositions via the dedicated add_* sub-resource endpoints (the
 * only ones that actually persist nested data — WordDetailSerializer's
 * nested fields are read-only, so posting them directly on /api/words/ is
 * silently ignored). If opened with a collectionId, the new word is also
 * added to that collection.
 *
 * Edit mode PATCHes only the base-word fields that actually changed, and
 * diffs each child list (by the item's original id) against what the word
 * had when the modal opened, issuing only the add/remove sub-resource
 * calls needed to reconcile the two — a changed row is removed and
 * re-added since there is no "update a single child row" endpoint.
 */
const AddWord = (function () {
    const NOUN_ID = 1;
    const VERB_ID = 2;
    const MAX_ROWS = 10;

    const GENUS_OPTIONS = [
        [1, "Мужской (der)"],
        [2, "Женский (die)"],
        [3, "Средний (das)"],
        [4, "Множественное число"],
    ];

    const REMOVE_ICON =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>';

    let collectionId = null;
    let onSavedCallback = null;
    let els = null;

    let mode = "add"; // "add" | "edit"
    let editingWordId = null;
    let originalWord = null;
    let initialSnapshot = null;
    let closeConfirmInFlight = false;

    function init(options) {
        options = options || {};
        collectionId = options.collectionId || null;

        const overlay = document.getElementById("add-word-modal-overlay");
        if (!overlay) {
            return;
        }

        els = {
            overlay,
            title: document.getElementById("add-word-title"),
            back: document.getElementById("add-word-back"),
            close: document.getElementById("add-word-close"),
            submit: document.getElementById("add-word-submit"),
            error: document.getElementById("add-word-error"),
            definition: document.getElementById("add-word-definition"),
            pos: document.getElementById("add-word-pos"),
            genusField: document.getElementById("add-word-genus-field"),
            genus: document.getElementById("add-word-genus"),
            translationsList: document.getElementById("add-word-translations"),
            examplesList: document.getElementById("add-word-examples"),
            formsList: document.getElementById("add-word-forms"),
            prepositionsSection: document.getElementById("add-word-prepositions-section"),
            prepositionsList: document.getElementById("add-word-prepositions"),
            addTranslationBtn: document.getElementById("add-translation-btn"),
            addExampleBtn: document.getElementById("add-example-btn"),
            addFormBtn: document.getElementById("add-form-btn"),
            addPrepositionBtn: document.getElementById("add-preposition-btn"),
        };

        // Word.definition: max_length=100
        wireLengthLimit(els.definition);

        for (const [id, label] of WordDetail.PART_OF_SPEECH) {
            const option = document.createElement("option");
            option.value = String(id);
            option.textContent = label;
            els.pos.appendChild(option);
        }

        for (const [id, label] of GENUS_OPTIONS) {
            const option = document.createElement("option");
            option.value = String(id);
            option.textContent = label;
            els.genus.appendChild(option);
        }

        els.pos.addEventListener("change", () => {
            els.genusField.hidden = els.pos.value !== String(NOUN_ID);
            els.prepositionsSection.hidden = els.pos.value !== String(VERB_ID);
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

        els.addTranslationBtn.addEventListener("click", () => addTranslationRow());
        els.addExampleBtn.addEventListener("click", () => addExampleRow());
        els.addFormBtn.addEventListener("click", () => addFormRow());
        els.addPrepositionBtn.addEventListener("click", () => addPrepositionRow());

        els.submit.addEventListener("click", submit);
    }

    function wireLengthLimit(input) {
        const update = () => {
            input.classList.toggle("input-limit-reached", input.value.length >= input.maxLength);
        };
        input.addEventListener("input", update);
        update();
    }

    function makeInput(placeholder, field, maxLength, value) {
        const input = document.createElement("input");
        input.className = "input";
        input.type = "text";
        input.placeholder = placeholder;
        input.dataset.field = field;
        input.maxLength = maxLength;
        input.value = value || "";
        wireLengthLimit(input);
        return input;
    }

    function makeRemoveButton() {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "form-repeat-remove";
        btn.title = "Удалить";
        btn.innerHTML = REMOVE_ICON;
        return btn;
    }

    function isAtRowLimit(listEl, warningMessage) {
        if (listEl.children.length >= MAX_ROWS) {
            showToast(warningMessage, 2200, "warning");
            return true;
        }
        return false;
    }

    function addTranslationRow(prefill) {
        if (isAtRowLimit(els.translationsList, `Можно добавить не более ${MAX_ROWS} переводов`)) {
            return;
        }
        const row = document.createElement("div");
        row.className = "form-repeat-row";
        if (prefill && prefill.id != null) {
            row.dataset.itemId = String(prefill.id);
        }
        // WordTranslation.translation: max_length=100
        row.appendChild(makeInput("Перевод", "translation", 100, prefill && prefill.translation));
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => row.remove());
        row.appendChild(removeBtn);
        els.translationsList.appendChild(row);
    }

    function addExampleRow(prefill) {
        if (isAtRowLimit(els.examplesList, `Можно добавить не более ${MAX_ROWS} примеров`)) {
            return;
        }
        const card = document.createElement("div");
        card.className = "form-repeat-card";
        if (prefill && prefill.id != null) {
            card.dataset.itemId = String(prefill.id);
        }
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => card.remove());
        card.appendChild(removeBtn);
        // WordExample.sentence / .translation: max_length=200
        card.appendChild(makeInput("Предложение", "sentence", 200, prefill && prefill.sentence));
        card.appendChild(makeInput("Перевод предложения", "translation", 200, prefill && prefill.translation));
        els.examplesList.appendChild(card);
    }

    function addFormRow(prefill) {
        if (isAtRowLimit(els.formsList, `Можно добавить не более ${MAX_ROWS} форм слова`)) {
            return;
        }
        const row = document.createElement("div");
        row.className = "form-repeat-row";
        if (prefill && prefill.id != null) {
            row.dataset.itemId = String(prefill.id);
        }
        // WordForm.name / .form: max_length=100
        row.appendChild(makeInput("Название формы", "name", 100, prefill && prefill.name));
        row.appendChild(makeInput("Форма", "form", 100, prefill && prefill.form));
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => row.remove());
        row.appendChild(removeBtn);
        els.formsList.appendChild(row);
    }

    function addPrepositionRow(prefill) {
        if (isAtRowLimit(els.prepositionsList, `Можно добавить не более ${MAX_ROWS} предлогов с падежами`)) {
            return;
        }
        const card = document.createElement("div");
        card.className = "form-repeat-card";
        if (prefill && prefill.id != null) {
            card.dataset.itemId = String(prefill.id);
        }
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => card.remove());
        card.appendChild(removeBtn);

        // WordPrepositionAndCaseWithTranslation.preposition / .case / .translation: max_length=100
        const topRow = document.createElement("div");
        topRow.className = "form-inline-pair";
        topRow.appendChild(makeInput("Предлог", "preposition", 100, prefill && prefill.preposition));
        topRow.appendChild(makeInput("Падеж", "case", 100, prefill && prefill.case));
        card.appendChild(topRow);

        card.appendChild(makeInput("Перевод (необязательно)", "translation", 100, prefill && prefill.translation));
        // WordPrepositionAndCaseWithTranslation.example: max_length=200
        card.appendChild(makeInput("Пример (необязательно)", "example", 200, prefill && prefill.example));
        els.prepositionsList.appendChild(card);
    }

    function collectRows(listEl, fieldNames) {
        const rows = [];
        listEl.querySelectorAll(".form-repeat-row, .form-repeat-card").forEach((rowEl) => {
            const data = { id: rowEl.dataset.itemId ? Number(rowEl.dataset.itemId) : null };
            fieldNames.forEach((name) => {
                const input = rowEl.querySelector(`[data-field="${name}"]`);
                data[name] = input ? input.value.trim() : "";
            });
            rows.push(data);
        });
        return rows;
    }

    /**
     * Compares the form's current rows for one child list against the rows
     * the word originally had (matched by id) and splits the difference
     * into rows to add and ids to remove. A row whose id still exists but
     * whose fields changed is removed and re-added, since there's no
     * single-row update endpoint.
     */
    function diffRows(currentRows, originalRows, fieldNames) {
        const originalById = new Map(originalRows.map((row) => [row.id, row]));
        const currentIds = new Set(currentRows.filter((row) => row.id != null).map((row) => row.id));

        const toAdd = [];
        const toRemove = [];

        currentRows.forEach((row) => {
            if (row.id != null && originalById.has(row.id)) {
                const original = originalById.get(row.id);
                const changed = fieldNames.some((field) => (row[field] || "") !== (original[field] || ""));
                if (changed) {
                    toRemove.push(row.id);
                    toAdd.push(row);
                }
            } else {
                toAdd.push(row);
            }
        });

        originalRows.forEach((original) => {
            if (!currentIds.has(original.id)) {
                toRemove.push(original.id);
            }
        });

        return { toAdd, toRemove };
    }

    function getFormSnapshot() {
        return JSON.stringify({
            definition: els.definition.value.trim(),
            pos: els.pos.value,
            genus: els.genusField.hidden ? "" : els.genus.value,
            translations: collectRows(els.translationsList, ["translation"]),
            examples: collectRows(els.examplesList, ["sentence", "translation"]),
            forms: collectRows(els.formsList, ["name", "form"]),
            prepositions: els.prepositionsSection.hidden
                ? []
                : collectRows(els.prepositionsList, ["preposition", "case", "translation", "example"]),
        });
    }

    function isDirty() {
        return initialSnapshot !== null && getFormSnapshot() !== initialSnapshot;
    }

    function resetForm() {
        els.error.classList.remove("is-visible");
        els.definition.value = "";
        els.pos.value = "";
        els.genus.value = "";
        els.genusField.hidden = true;
        els.prepositionsSection.hidden = true;
        els.translationsList.innerHTML = "";
        els.examplesList.innerHTML = "";
        els.formsList.innerHTML = "";
        els.prepositionsList.innerHTML = "";
        addTranslationRow();
        addExampleRow();
        addFormRow();
        addPrepositionRow();
    }

    function fillForm(word) {
        els.error.classList.remove("is-visible");
        els.definition.value = word.definition || "";
        els.pos.value = word.part_of_speech_id != null ? String(word.part_of_speech_id) : "";
        els.genus.value = word.genus_id != null ? String(word.genus_id) : "";
        els.genusField.hidden = String(word.part_of_speech_id) !== String(NOUN_ID);
        els.prepositionsSection.hidden = String(word.part_of_speech_id) !== String(VERB_ID);

        els.translationsList.innerHTML = "";
        els.examplesList.innerHTML = "";
        els.formsList.innerHTML = "";
        els.prepositionsList.innerHTML = "";

        (word.translations || []).forEach((t) => addTranslationRow(t));
        (word.examples || []).forEach((e) => addExampleRow(e));
        (word.forms || []).forEach((f) => addFormRow(f));
        (word.prepositions_and_cases_with_translations || []).forEach((p) => addPrepositionRow(p));
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

    function open(onSaved) {
        if (!els) {
            return;
        }
        mode = "add";
        editingWordId = null;
        originalWord = null;
        onSavedCallback = onSaved || null;
        els.title.textContent = "Добавить слово";
        resetForm();
        initialSnapshot = getFormSnapshot();
        showModal();
    }

    function openForEdit(word, onSaved) {
        if (!els) {
            return;
        }
        mode = "edit";
        editingWordId = word.id;
        originalWord = word;
        onSavedCallback = onSaved || null;
        els.title.textContent = "Редактировать слово";
        fillForm(word);
        initialSnapshot = getFormSnapshot();
        showModal();
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

    function hideModal() {
        els.overlay.classList.remove("is-open");
        document.body.style.overflow = "";
        setTimeout(() => {
            els.overlay.hidden = true;
        }, 200);
    }

    function postSubItem(wordId, actionName, body) {
        return apiFetch(`/api/words/${wordId}/${actionName}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    }

    function deleteSubItem(wordId, actionName, itemId) {
        return apiFetch(`/api/words/${wordId}/${actionName}/`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: itemId }),
        });
    }

    function collectFormState() {
        const definition = els.definition.value.trim();
        const partOfSpeechId = els.pos.value;
        const genusId = !els.genusField.hidden && els.genus.value ? Number(els.genus.value) : null;

        const translations = collectRows(els.translationsList, ["translation"]).filter((t) => t.translation);
        const examples = collectRows(els.examplesList, ["sentence", "translation"]).filter(
            (e) => e.sentence && e.translation
        );
        const forms = collectRows(els.formsList, ["name", "form"]).filter((f) => f.name && f.form);
        // Prepositions only make sense for verbs — ignore anything left over
        // in the (hidden) list if the user switched away from "Глагол".
        const prepositions = els.prepositionsSection.hidden
            ? []
            : collectRows(els.prepositionsList, ["preposition", "case", "translation", "example"]).filter(
                (p) => p.preposition && p.case
            );

        return { definition, partOfSpeechId, genusId, translations, examples, forms, prepositions };
    }

    async function submitCreate(state) {
        const response = await apiFetch("/api/words/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                definition: state.definition,
                part_of_speech_id: Number(state.partOfSpeechId),
                genus_id: state.genusId,
            }),
        });

        if (!response.ok) {
            showError("Не удалось сохранить слово. Попробуйте ещё раз.");
            return;
        }

        const word = await response.json();
        const followUps = [];

        state.translations.forEach((t) => {
            followUps.push(postSubItem(word.id, "add_word_translation", { translation: t.translation }));
        });
        state.examples.forEach((e) => {
            followUps.push(
                postSubItem(word.id, "add_word_example", { sentence: e.sentence, translation: e.translation })
            );
        });
        state.forms.forEach((f) => {
            followUps.push(postSubItem(word.id, "add_word_form", { name: f.name, form: f.form }));
        });
        state.prepositions.forEach((p) => {
            followUps.push(
                postSubItem(word.id, "add_word_preposition_and_case_with_translation", {
                    preposition: p.preposition,
                    case: p.case,
                    translation: p.translation || null,
                    example: p.example || null,
                })
            );
        });
        if (collectionId) {
            followUps.push(
                apiFetch(`/api/collections/${collectionId}/add_word/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ word_id: word.id }),
                })
            );
        }

        await Promise.all(followUps);

        hideModal();
        showToast("Слово добавлено");
        if (onSavedCallback) {
            onSavedCallback();
        }
    }

    async function submitEdit(state) {
        const patch = {};
        if (state.definition !== originalWord.definition) {
            patch.definition = state.definition;
        }
        if (Number(state.partOfSpeechId) !== originalWord.part_of_speech_id) {
            patch.part_of_speech_id = Number(state.partOfSpeechId);
        }
        if (state.genusId !== (originalWord.genus_id ?? null)) {
            patch.genus_id = state.genusId;
        }

        if (Object.keys(patch).length > 0) {
            const response = await apiFetch(`/api/words/${editingWordId}/`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(patch),
            });
            if (!response.ok) {
                showError("Не удалось сохранить изменения. Попробуйте ещё раз.");
                return;
            }
        }

        const translationsDiff = diffRows(state.translations, originalWord.translations || [], ["translation"]);
        const examplesDiff = diffRows(state.examples, originalWord.examples || [], ["sentence", "translation"]);
        const formsDiff = diffRows(state.forms, originalWord.forms || [], ["name", "form"]);
        const prepositionsDiff = diffRows(
            state.prepositions,
            originalWord.prepositions_and_cases_with_translations || [],
            ["preposition", "case", "translation", "example"]
        );

        const followUps = [];

        translationsDiff.toRemove.forEach((id) => {
            followUps.push(deleteSubItem(editingWordId, "remove_word_translation", id));
        });
        translationsDiff.toAdd.forEach((t) => {
            followUps.push(postSubItem(editingWordId, "add_word_translation", { translation: t.translation }));
        });

        examplesDiff.toRemove.forEach((id) => {
            followUps.push(deleteSubItem(editingWordId, "remove_word_example", id));
        });
        examplesDiff.toAdd.forEach((e) => {
            followUps.push(
                postSubItem(editingWordId, "add_word_example", { sentence: e.sentence, translation: e.translation })
            );
        });

        formsDiff.toRemove.forEach((id) => {
            followUps.push(deleteSubItem(editingWordId, "remove_word_form", id));
        });
        formsDiff.toAdd.forEach((f) => {
            followUps.push(postSubItem(editingWordId, "add_word_form", { name: f.name, form: f.form }));
        });

        prepositionsDiff.toRemove.forEach((id) => {
            followUps.push(deleteSubItem(editingWordId, "remove_word_preposition_and_case_with_translation", id));
        });
        prepositionsDiff.toAdd.forEach((p) => {
            followUps.push(
                postSubItem(editingWordId, "add_word_preposition_and_case_with_translation", {
                    preposition: p.preposition,
                    case: p.case,
                    translation: p.translation || null,
                    example: p.example || null,
                })
            );
        });

        await Promise.all(followUps);

        hideModal();
        if (Object.keys(patch).length > 0 || followUps.length > 0) {
            showToast("Слово обновлено");
        }
        if (onSavedCallback) {
            onSavedCallback();
        }
    }

    async function submit() {
        els.error.classList.remove("is-visible");

        const state = collectFormState();

        if (!state.definition || !state.partOfSpeechId) {
            showError("Укажите слово и часть речи.");
            return;
        }

        els.submit.disabled = true;

        try {
            if (mode === "edit") {
                await submitEdit(state);
            } else {
                await submitCreate(state);
            }
        } catch (err) {
            showError("Не удалось сохранить слово. Попробуйте ещё раз.");
        } finally {
            els.submit.disabled = false;
        }
    }

    return { init, open, openForEdit };
})();

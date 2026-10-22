/**
 * Shared "add word" modal: opened from the FAB on the home page and on a
 * collection's word list. Creates the word via POST /api/words/, then fills
 * in its translations/examples/forms/prepositions via the dedicated add_*
 * sub-resource endpoints (the only ones that actually persist nested data —
 * WordDetailSerializer's nested fields are read-only, so posting them
 * directly on /api/words/ is silently ignored). If opened with a
 * collectionId, the new word is also added to that collection.
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

    function init(options) {
        options = options || {};
        collectionId = options.collectionId || null;

        const overlay = document.getElementById("add-word-modal-overlay");
        if (!overlay) {
            return;
        }

        els = {
            overlay,
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

        els.back.addEventListener("click", close);
        els.close.addEventListener("click", close);
        els.overlay.addEventListener("click", (event) => {
            if (event.target === els.overlay) {
                close();
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !els.overlay.hidden) {
                close();
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
    }

    function makeInput(placeholder, field, maxLength) {
        const input = document.createElement("input");
        input.className = "input";
        input.type = "text";
        input.placeholder = placeholder;
        input.dataset.field = field;
        input.maxLength = maxLength;
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

    function addTranslationRow() {
        if (isAtRowLimit(els.translationsList, `Можно добавить не более ${MAX_ROWS} переводов`)) {
            return;
        }
        const row = document.createElement("div");
        row.className = "form-repeat-row";
        // WordTranslation.translation: max_length=100
        row.appendChild(makeInput("Перевод", "translation", 100));
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => row.remove());
        row.appendChild(removeBtn);
        els.translationsList.appendChild(row);
    }

    function addExampleRow() {
        if (isAtRowLimit(els.examplesList, `Можно добавить не более ${MAX_ROWS} примеров`)) {
            return;
        }
        const card = document.createElement("div");
        card.className = "form-repeat-card";
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => card.remove());
        card.appendChild(removeBtn);
        // WordExample.sentence / .translation: max_length=200
        card.appendChild(makeInput("Предложение", "sentence", 200));
        card.appendChild(makeInput("Перевод предложения", "translation", 200));
        els.examplesList.appendChild(card);
    }

    function addFormRow() {
        if (isAtRowLimit(els.formsList, `Можно добавить не более ${MAX_ROWS} форм слова`)) {
            return;
        }
        const row = document.createElement("div");
        row.className = "form-repeat-row";
        // WordForm.name / .form: max_length=100
        row.appendChild(makeInput("Название формы", "name", 100));
        row.appendChild(makeInput("Форма", "form", 100));
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => row.remove());
        row.appendChild(removeBtn);
        els.formsList.appendChild(row);
    }

    function addPrepositionRow() {
        if (isAtRowLimit(els.prepositionsList, `Можно добавить не более ${MAX_ROWS} предлогов с падежами`)) {
            return;
        }
        const card = document.createElement("div");
        card.className = "form-repeat-card";
        const removeBtn = makeRemoveButton();
        removeBtn.addEventListener("click", () => card.remove());
        card.appendChild(removeBtn);

        // WordPrepositionAndCaseWithTranslation.preposition / .case / .translation: max_length=100
        const topRow = document.createElement("div");
        topRow.className = "form-inline-pair";
        topRow.appendChild(makeInput("Предлог", "preposition", 100));
        topRow.appendChild(makeInput("Падеж", "case", 100));
        card.appendChild(topRow);

        card.appendChild(makeInput("Перевод (необязательно)", "translation", 100));
        // WordPrepositionAndCaseWithTranslation.example: max_length=200
        card.appendChild(makeInput("Пример (необязательно)", "example", 200));
        els.prepositionsList.appendChild(card);
    }

    function collectRows(listEl, fieldNames) {
        const rows = [];
        listEl.querySelectorAll(".form-repeat-row, .form-repeat-card").forEach((rowEl) => {
            const data = {};
            fieldNames.forEach((name) => {
                const input = rowEl.querySelector(`[data-field="${name}"]`);
                data[name] = input ? input.value.trim() : "";
            });
            rows.push(data);
        });
        return rows;
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

    function showError(message) {
        els.error.textContent = message;
        els.error.classList.add("is-visible");
    }

    function open(onSaved) {
        if (!els) {
            return;
        }
        onSavedCallback = onSaved || null;
        resetForm();
        els.overlay.hidden = false;
        document.body.style.overflow = "hidden";
        requestAnimationFrame(() => els.overlay.classList.add("is-open"));
    }

    function close() {
        els.overlay.classList.remove("is-open");
        document.body.style.overflow = "";
        setTimeout(() => {
            els.overlay.hidden = true;
        }, 200);
    }

    async function submit() {
        els.error.classList.remove("is-visible");

        const definition = els.definition.value.trim();
        const partOfSpeechId = els.pos.value;

        if (!definition || !partOfSpeechId) {
            showError("Укажите слово и часть речи.");
            return;
        }

        const genusId = !els.genusField.hidden && els.genus.value ? Number(els.genus.value) : null;

        const translations = collectRows(els.translationsList, ["translation"]).filter(
            (t) => t.translation
        );
        const examples = collectRows(els.examplesList, ["sentence", "translation"]).filter(
            (e) => e.sentence && e.translation
        );
        const forms = collectRows(els.formsList, ["name", "form"]).filter((f) => f.name && f.form);
        // Prepositions only make sense for verbs — ignore anything left over
        // in the (hidden) list if the user switched away from "Глагол".
        const prepositions = els.prepositionsSection.hidden
            ? []
            : collectRows(els.prepositionsList, ["preposition", "case", "translation", "example"])
                  .filter((p) => p.preposition && p.case)
                  .map((p) => ({
                      preposition: p.preposition,
                      case: p.case,
                      translation: p.translation || null,
                      example: p.example || null,
                  }));

        els.submit.disabled = true;

        try {
            const response = await apiFetch("/api/words/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    definition,
                    part_of_speech_id: Number(partOfSpeechId),
                    genus_id: genusId,
                }),
            });

            if (!response.ok) {
                showError("Не удалось сохранить слово. Попробуйте ещё раз.");
                return;
            }

            const word = await response.json();
            const followUps = [];

            translations.forEach((t) => {
                followUps.push(
                    apiFetch(`/api/words/${word.id}/add_word_translation/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(t),
                    })
                );
            });
            examples.forEach((e) => {
                followUps.push(
                    apiFetch(`/api/words/${word.id}/add_word_example/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(e),
                    })
                );
            });
            forms.forEach((f) => {
                followUps.push(
                    apiFetch(`/api/words/${word.id}/add_word_form/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(f),
                    })
                );
            });
            prepositions.forEach((p) => {
                followUps.push(
                    apiFetch(`/api/words/${word.id}/add_word_preposition_and_case_with_translation/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(p),
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

            close();
            showToast("Слово добавлено");
            if (onSavedCallback) {
                onSavedCallback();
            }
        } catch (err) {
            showError("Не удалось сохранить слово. Попробуйте ещё раз.");
        } finally {
            els.submit.disabled = false;
        }
    }

    return { init, open };
})();

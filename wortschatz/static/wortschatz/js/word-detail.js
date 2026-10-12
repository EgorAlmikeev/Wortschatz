/**
 * Shared word-detail rendering: used by the word modal on the home page and
 * by the word-within-collection view on the collections page, so the two
 * stay visually identical without duplicating the section-building logic.
 */
const WordDetail = (function () {
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

    const PART_OF_SPEECH_LABEL = Object.fromEntries(PART_OF_SPEECH);
    const GENUS_ARTICLE = { 1: "der", 2: "die", 3: "das", 4: "die" };

    const SECTION_ICONS = {
        book: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
        chat: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
        layers: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
    };

    function posLabel(id) {
        return PART_OF_SPEECH_LABEL[id] || "";
    }

    function genusArticle(id) {
        return GENUS_ARTICLE[id];
    }

    function makePill(text) {
        const span = document.createElement("span");
        span.className = "pill pill-muted";
        span.textContent = text;
        return span;
    }

    function buildSection(iconKey, colorClass, title) {
        const section = document.createElement("div");
        section.className = "detail-section";

        const head = document.createElement("div");
        head.className = "detail-section-head";

        const icon = document.createElement("span");
        icon.className = `section-icon ${colorClass}`;
        icon.innerHTML = SECTION_ICONS[iconKey];

        const h3 = document.createElement("h3");
        h3.textContent = title;

        head.appendChild(icon);
        head.appendChild(h3);

        const content = document.createElement("div");

        section.appendChild(head);
        section.appendChild(content);

        return { section, content };
    }

    function buildTranslationsSection(translations) {
        if (!translations.length) return null;
        const { section, content } = buildSection("book", "mint", "Переводы");
        const list = document.createElement("ul");
        list.className = "translation-list";
        translations.forEach((t) => {
            const li = document.createElement("li");
            li.textContent = t.translation;
            list.appendChild(li);
        });
        content.appendChild(list);
        return section;
    }

    function buildExamplesSection(examples) {
        if (!examples.length) return null;
        const { section, content } = buildSection("chat", "peach", "Примеры употребления");
        const list = document.createElement("div");
        list.className = "example-list";
        examples.forEach((ex) => {
            const item = document.createElement("div");
            const sentence = document.createElement("p");
            sentence.className = "example-sentence";
            sentence.textContent = ex.sentence;
            const translation = document.createElement("p");
            translation.className = "example-translation";
            translation.textContent = ex.translation;
            item.appendChild(sentence);
            item.appendChild(translation);
            list.appendChild(item);
        });
        content.appendChild(list);
        return section;
    }

    function buildFormsSection(forms) {
        if (!forms.length) return null;
        const { section, content } = buildSection("layers", "lavender", "Формы слова");
        const list = document.createElement("div");
        list.className = "form-list";
        forms.forEach((f) => {
            const row = document.createElement("div");
            row.className = "form-row";
            const name = document.createElement("span");
            name.className = "form-name";
            name.textContent = f.name;
            const value = document.createElement("span");
            value.className = "form-value";
            value.textContent = f.form;
            row.appendChild(name);
            row.appendChild(value);
            list.appendChild(row);
        });
        content.appendChild(list);
        return section;
    }

    function buildPrepositionsSection(items) {
        if (!items.length) return null;
        const { section, content } = buildSection("book", "rose", "Предлоги с падежами");
        const list = document.createElement("div");
        list.className = "preposition-list";
        items.forEach((p) => {
            const item = document.createElement("div");
            const head = document.createElement("div");
            head.className = "preposition-head";
            head.appendChild(makePill(p.preposition));
            const caseLabel = document.createElement("span");
            caseLabel.className = "form-name";
            caseLabel.textContent = p.case;
            head.appendChild(caseLabel);
            item.appendChild(head);
            if (p.example) {
                const example = document.createElement("p");
                example.className = "preposition-example";
                example.textContent = p.example;
                item.appendChild(example);
            }
            if (p.translation) {
                const translation = document.createElement("p");
                translation.className = "preposition-translation";
                translation.textContent = p.translation;
                item.appendChild(translation);
            }
            list.appendChild(item);
        });
        content.appendChild(list);
        return section;
    }

    function buildSections(word) {
        return [
            buildTranslationsSection(word.translations || []),
            buildExamplesSection(word.examples || []),
            buildFormsSection(word.forms || []),
            buildPrepositionsSection(word.prepositions_and_cases_with_translations || []),
        ].filter(Boolean);
    }

    return {
        PART_OF_SPEECH,
        posLabel,
        genusArticle,
        buildSections,
    };
})();

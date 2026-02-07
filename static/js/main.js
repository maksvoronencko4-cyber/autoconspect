// ═══════════════════════════════════════════
//  АвтоКонспект Web + Wikipedia — JavaScript
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function () {

    // ── Элементы ──
    const menuBtns       = document.querySelectorAll('.menu-btn');
    const modeTitle      = document.getElementById('mode-title');
    const modeSubtitle   = document.getElementById('mode-subtitle');
    const inputLabel     = document.getElementById('input-label');
    const authorSection  = document.getElementById('author-section');
    const topicInput     = document.getElementById('topic-input');
    const volumeSelect   = document.getElementById('volume');
    const styleSelect    = document.getElementById('style');
    const generateBtn    = document.getElementById('generate-btn');
    const clearBtn       = document.getElementById('clear-btn');
    const copyBtn        = document.getElementById('copy-btn');
    const downloadBtn    = document.getElementById('download-btn');
    const resultDiv      = document.getElementById('result');
    const loadingDiv     = document.getElementById('loading');
    const loadingSub     = document.getElementById('loading-sub');
    const statsSpan      = document.getElementById('stats');

    // Wikipedia элементы
    const useWikiCheck   = document.getElementById('use-wiki');
    const wikiBody       = document.getElementById('wiki-body');
    const wikiQueryInput = document.getElementById('wiki-query');
    const wikiLangSelect = document.getElementById('wiki-lang');
    const wikiSearchBtn  = document.getElementById('wiki-search-btn');
    const wikiLoading    = document.getElementById('wiki-loading');
    const wikiResults    = document.getElementById('wiki-results');
    const wikiSelectedBar = document.getElementById('wiki-selected-bar');
    const wikiCountSpan  = document.getElementById('wiki-count');
    const wikiBadge      = document.getElementById('wiki-badge');
    const wikiBadgeCount = document.getElementById('wiki-badge-count');

    let currentMode = 'referat';

    // ── Информация о режимах ──
    const modeInfo = {
        referat:  { title: '📄 Генератор рефератов',  subtitle: 'Введите тему и получите готовый реферат',           inputLabel: '📝 Тема реферата:',    showAuthor: true  },
        conspect: { title: '📝 Генератор конспектов',  subtitle: 'Введите тему или вставьте текст',                  inputLabel: '📝 Тема или текст:',   showAuthor: false },
        doklad:   { title: '📊 План доклада',          subtitle: 'Получите структурированный план выступления',      inputLabel: '📝 Тема доклада:',     showAuthor: true  },
        question: { title: '❓ Ответ на вопрос',       subtitle: 'Задайте вопрос и получите развёрнутый ответ',      inputLabel: '📝 Ваш вопрос:',      showAuthor: false },
        retell:   { title: '📖 Пересказ текста',       subtitle: 'Вставьте текст для краткого пересказа',            inputLabel: '📝 Текст для пересказа:', showAuthor: false },
        essay:    { title: '✍️ Генератор эссе',        subtitle: 'Создание творческих работ и сочинений',            inputLabel: '📝 Тема эссе:',       showAuthor: true  }
    };

    // ══════════════════════════════════════
    //  ПЕРЕКЛЮЧЕНИЕ РЕЖИМОВ
    // ══════════════════════════════════════
    menuBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            menuBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            currentMode = this.dataset.mode;
            const info = modeInfo[currentMode];

            modeTitle.textContent    = info.title;
            modeSubtitle.textContent = info.subtitle;
            inputLabel.textContent   = info.inputLabel;
            authorSection.style.display = info.showAuthor ? 'block' : 'none';
        });
    });

    // ══════════════════════════════════════
    //  WIKIPEDIA — TOGGLE
    // ══════════════════════════════════════
    useWikiCheck.addEventListener('change', function () {
        wikiBody.style.display = this.checked ? 'block' : 'none';
    });

    // ══════════════════════════════════════
    //  WIKIPEDIA — ПОИСК
    // ══════════════════════════════════════
    wikiSearchBtn.addEventListener('click', doWikiSearch);
    wikiQueryInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); doWikiSearch(); }
    });

    async function doWikiSearch() {
        // Берём запрос из wiki-input, если пуст — из topic-input
        let query = wikiQueryInput.value.trim();
        if (!query) query = topicInput.value.trim();
        if (!query) { alert('Введите тему или поисковый запрос!'); return; }

        const lang = wikiLangSelect.value;

        wikiSearchBtn.disabled = true;
        wikiSearchBtn.textContent = '⏳…';
        wikiLoading.classList.remove('hidden');
        wikiResults.innerHTML = '';

        try {
            const resp = await fetch('/wiki/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, lang })
            });
            const data = await resp.json();

            if (data.success && data.results.length > 0) {
                renderWikiResults(data.results);
            } else {
                wikiResults.innerHTML =
                    '<p class="wiki-empty">🔍 Ничего не найдено. Попробуйте другой запрос или язык.</p>';
            }
        } catch (err) {
            wikiResults.innerHTML =
                '<p class="wiki-error">❌ Ошибка соединения с Википедией</p>';
        }

        wikiLoading.classList.add('hidden');
        wikiSearchBtn.disabled = false;
        wikiSearchBtn.textContent = '🔍 Найти';
    }

    // ── Отрисовка результатов ──
    function renderWikiResults(results) {
        wikiResults.innerHTML = results.map(r => {
            const words = r.wordcount ? r.wordcount.toLocaleString('ru') + ' сл.' : '';
            return `
            <label class="wiki-card">
                <input type="checkbox" class="wiki-cb" value="${escapeHtml(r.title)}">
                <div class="wiki-card-body">
                    <span class="wiki-card-title">${escapeHtml(r.title)}</span>
                    <span class="wiki-card-snippet">${escapeHtml(r.snippet)}</span>
                    <span class="wiki-card-meta">${words}</span>
                </div>
            </label>`;
        }).join('');

        // Слушатели на чекбоксы
        document.querySelectorAll('.wiki-cb').forEach(cb => {
            cb.addEventListener('change', updateWikiCount);
        });

        updateWikiCount();
    }

    function updateWikiCount() {
        const checked = document.querySelectorAll('.wiki-cb:checked');
        wikiCountSpan.textContent = checked.length;

        if (checked.length > 0) {
            wikiSelectedBar.classList.remove('hidden');
        } else {
            wikiSelectedBar.classList.add('hidden');
        }

        // Ограничиваем выбор до 5
        if (checked.length >= 5) {
            document.querySelectorAll('.wiki-cb:not(:checked)')
                .forEach(cb => cb.disabled = true);
        } else {
            document.querySelectorAll('.wiki-cb')
                .forEach(cb => cb.disabled = false);
        }
    }

    function getSelectedWikiTitles() {
        return Array.from(document.querySelectorAll('.wiki-cb:checked'))
            .map(cb => cb.value);
    }

    function escapeHtml(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    // ══════════════════════════════════════
    //  ГЕНЕРАЦИЯ
    // ══════════════════════════════════════
    generateBtn.addEventListener('click', async function () {
        const topic = topicInput.value.trim();
        if (!topic) { alert('Введите тему или текст!'); return; }

        // Собираем Wikipedia
        const useWiki    = useWikiCheck.checked;
        const wikiTitles = useWiki ? getSelectedWikiTitles() : [];
        const wikiLang   = wikiLangSelect.value;

        // UI — загрузка
        resultDiv.style.display = 'none';
        wikiBadge.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        generateBtn.disabled = true;

        if (wikiTitles.length > 0) {
            

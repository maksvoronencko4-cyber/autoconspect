// АвтоКонспект Web + Wikipedia — JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== ЭЛЕМЕНТЫ =====
    const menuBtns = document.querySelectorAll('.menu-btn');
    const modeTitle = document.getElementById('mode-title');
    const modeSubtitle = document.getElementById('mode-subtitle');
    const inputLabel = document.getElementById('input-label');
    const authorSection = document.getElementById('author-section');
    const topicInput = document.getElementById('topic-input');
    const volumeSelect = document.getElementById('volume');
    const styleSelect = document.getElementById('style');
    const generateBtn = document.getElementById('generate-btn');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');
    const statsSpan = document.getElementById('stats');
    
    // Wikipedia элементы
    const useWikipediaCheckbox = document.getElementById('use-wikipedia');
    const wikiSection = document.getElementById('wiki-section');
    const wikiSearchInput = document.getElementById('wiki-search-input');
    const wikiSearchBtn = document.getElementById('wiki-search-btn');
    const wikiResults = document.getElementById('wiki-results');
    const wikiSelected = document.getElementById('wiki-selected');
    const selectedWikiTitle = document.getElementById('selected-wiki-title');
    const clearWikiBtn = document.getElementById('clear-wiki-btn');
    const wikiStatus = document.getElementById('wiki-status');
    
    // ===== СОСТОЯНИЕ =====
    let currentMode = 'referat';
    let selectedWikiArticle = null;
    
    // ===== ИНФОРМАЦИЯ О РЕЖИМАХ =====
    const modeInfo = {
        referat: {
            title: '📄 Генератор рефератов',
            subtitle: 'Данные из Википедии → AI создаёт реферат',
            inputLabel: '📝 Тема реферата:',
            showAuthor: true
        },
        conspect: {
            title: '📝 Генератор конспектов',
            subtitle: 'Структурированный конспект на основе Википедии',
            inputLabel: '📝 Тема конспекта:',
            showAuthor: false
        },
        doklad: {
            title: '📊 Генератор докладов',
            subtitle: 'Текст для выступления с фактами из Википедии',
            inputLabel: '📝 Тема доклада:',
            showAuthor: true
        },
        question: {
            title: '❓ Ответ на вопрос',
            subtitle: 'Развёрнутый ответ на основе Википедии',
            inputLabel: '📝 Ваш вопрос:',
            showAuthor: false
        },
        retell: {
            title: '📖 Пересказ',
            subtitle: 'Пересказ материала из Википедии',
            inputLabel: '📝 Тема для пересказа:',
            showAuthor: false
        },
        essay: {
            title: '✍️ Генератор эссе',
            subtitle: 'Эссе с опорой на факты из Википедии',
            inputLabel: '📝 Тема эссе:',
            showAuthor: true
        }
    };
    
    // ===== ПЕРЕКЛЮЧЕНИЕ РЕЖИМА =====
    menuBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            menuBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            currentMode = this.dataset.mode;
            const info = modeInfo[currentMode];
            
            modeTitle.textContent = info.title;
            modeSubtitle.textContent = info.subtitle;
            inputLabel.textContent = info.inputLabel;
            
            authorSection.style.display = info.showAuthor ? 'block' : 'none';
        });
    });
    
    // ===== WIKIPEDIA TOGGLE =====
    useWikipediaCheckbox.addEventListener('change', function() {
        if (this.checked) {
            wikiSection.style.display = 'block';
            wikiSection.classList.add('wiki-active');
        } else {
            wikiSection.style.display = 'none';
            wikiSection.classList.remove('wiki-active');
            clearWikiSelection();
        }
    });
    
    // ===== ПОИСК В WIKIPEDIA =====
    wikiSearchBtn.addEventListener('click', searchWikipedia);
    wikiSearchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchWikipedia();
        }
    });
    
    async function searchWikipedia() {
        const query = wikiSearchInput.value.trim();
        
        if (!query) {
            alert('Введите поисковый запрос!');
            return;
        }
        
        wikiStatus.textContent = '🔍 Поиск...';
        wikiStatus.className = 'wiki-status searching';
        wikiResults.innerHTML = '<div class="wiki-loading">Поиск статей...</div>';
        
        try {
            const response = await fetch('/wiki/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (data.success && data.results.length > 0) {
                displayWikiResults(data.results);
                wikiStatus.textContent = `✅ Найдено: ${data.results.length}`;
                wikiStatus.className = 'wiki-status success';
            } else {
                wikiResults.innerHTML = '<div class="wiki-no-results">Статьи не найдены. Попробуйте другой запрос.</div>';
                wikiStatus.textContent = '❌ Не найдено';
                wikiStatus.className = 'wiki-status error';
            }
            
        } catch (error) {
            wikiResults.innerHTML = `<div class="wiki-error">Ошибка поиска: ${error.message}</div>`;
            wikiStatus.textContent = '❌ Ошибка';
            wikiStatus.className = 'wiki-status error';
        }
    }
    
    function displayWikiResults(results) {
        wikiResults.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'wiki-result-item';
            item.innerHTML = `
                <div class="wiki-result-title">${result.title}</div>
                <div class="wiki-result-desc">${result.description || 'Нет описания'}</div>
            `;
            
            item.addEventListener('click', () => selectWikiArticle(result));
            wikiResults.appendChild(item);
        });
    }
    
    function selectWikiArticle(article) {
        selectedWikiArticle = article.title;
        
        // Обновляем UI
        selectedWikiTitle.textContent = article.title;
        wikiSelected.style.display = 'block';
        wikiResults.innerHTML = '';
        
        // Автозаполнение темы
        if (!topicInput.value.trim()) {
            topicInput.value = article.title;
        }
        
        wikiStatus.textContent = '📌 Статья выбрана';
        wikiStatus.className = 'wiki-status selected';
        
        // Подсветка выбранной статьи
        wikiSelected.classList.add('pulse');
        setTimeout(() => wikiSelected.classList.remove('pulse'), 500);
    }
    
    function clearWikiSelection() {
        selectedWikiArticle = null;
        wikiSelected.style.display = 'none';
        selectedWikiTitle.textContent = '';
        wikiStatus.textContent = 'Готов к поиску';
        wikiStatus.className = 'wiki-status';
    }
    
    clearWikiBtn.addEventListener('click', clearWikiSelection);
    
    // ===== ГЕНЕРАЦИЯ =====
    generateBtn.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        
        if (!topic) {
            alert('Введите тему!');
            return;
        }
        
        // Показываем загрузку
        resultDiv.style.display = 'none';
        loadingDiv.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ Генерация...';
        
        // Обновляем текст загрузки
        const useWiki = useWikipediaCheckbox.checked;
        if (useWiki) {
            loadingText.textContent = '📖 Получаем данные из Википедии...';
            setTimeout(() => {
                loadingText.textContent = '✨ AI обрабатывает информацию...';
            }, 2000);
        } else {
            loadingText.textContent = '✨ Генерация текста...';
        }
        
        // Собираем данные
        const data = {
            mode: currentMode,
            topic: topic,
            volume: volumeSelect.value,
            style: styleSelect.value,
            use_wikipedia: useWiki,
            wiki_article_title: selectedWikiArticle,
            author_info: {
                name: document.getElementById('author-name').value,
                edu_type: document.getElementById('edu-type').value,
                grade: document.getElementById('grade').value,
                institution: document.getElementById('institution').value,
                group: document.getElementById('group').value,
                teacher: document.getElementById('teacher').value,
                include_title: document.getElementById('include-title').checked
            }
        };
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                resultDiv.textContent = result.result;
                statsSpan.textContent = `📊 ${result.stats.words} слов | ${result.stats.chars} символов | ~${result.stats.pages} стр.`;
            } else {
                resultDiv.textContent = 'Ошибка: ' + result.error;
            }
            
        } catch (error) {
            resultDiv.textContent = 'Ошибка соединения: ' + error.message;
        }
        
        // Скрываем загрузку
        loadingDiv.classList.add('hidden');
        resultDiv.style.display = 'block';
        generateBtn.disabled = false;
        generateBtn.textContent = '✨ Сгенерировать';
    });
    
    // ===== ОЧИСТКА =====
    clearBtn.addEventListener('click', function() {
        topicInput.value = '';
        resultDiv.textContent = '';
        statsSpan.textContent = '';
        clearWikiSelection();
        wikiSearchInput.value = '';
        wikiResults.innerHTML = '';
    });
    
    // ===== КОПИРОВАНИЕ =====
    copyBtn.addEventListener('click', function() {
        const text = resultDiv.textContent;
        
        if (!text) {
            alert('Нет текста для копирования!');
            return;
        }
        
        navigator.clipboard.writeText(text).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✅ Скопировано!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });
    
    // ===== СКАЧИВАНИЕ =====
    downloadBtn.addEventListener('click', function() {
        const text = resultDiv.textContent;
        
        if (!text) {
            alert('Нет текста для скачивания!');
            return;
        }
        
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentMode}_${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    });
    
    // ===== АВТОПОИСК ПРИ ВВОДЕ ТЕМЫ =====
    let searchTimeout;
    topicInput.addEventListener('input', function() {
        if (!useWikipediaCheckbox.checked) return;
        
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 3) {
            searchTimeout = setTimeout(() => {
                wikiSearchInput.value = query;
                // Не запускаем автопоиск, только заполняем поле
            }, 500);
        }
    });
    
});

// АвтоКонспект Web — JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Элементы
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
    const statsSpan = document.getElementById('stats');
    
    // Текущий режим
    let currentMode = 'referat';
    
    // Информация о режимах
    const modeInfo = {
        referat: {
            title: '📄 Генератор рефератов',
            subtitle: 'Введите тему и получите готовый реферат',
            inputLabel: '📝 Тема реферата:',
            showAuthor: true
        },
        conspect: {
            title: '📝 Генератор конспектов',
            subtitle: 'Введите тему или вставьте текст',
            inputLabel: '📝 Тема или текст:',
            showAuthor: false
        },
        doklad: {
            title: '📊 План доклада',
            subtitle: 'Получите структурированный план выступления',
            inputLabel: '📝 Тема доклада:',
            showAuthor: true
        },
        question: {
            title: '❓ Ответ на вопрос',
            subtitle: 'Задайте вопрос и получите развёрнутый ответ',
            inputLabel: '📝 Ваш вопрос:',
            showAuthor: false
        },
        retell: {
            title: '📖 Пересказ текста',
            subtitle: 'Вставьте текст для краткого пересказа',
            inputLabel: '📝 Текст для пересказа:',
            showAuthor: false
        },
        essay: {
            title: '✍️ Генератор эссе',
            subtitle: 'Создание творческих работ и сочинений',
            inputLabel: '📝 Тема эссе:',
            showAuthor: true
        }
    };
    
    // Переключение режима
    menuBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Убираем active у всех
            menuBtns.forEach(b => b.classList.remove('active'));
            // Добавляем active текущей
            this.classList.add('active');
            
            // Меняем режим
            currentMode = this.dataset.mode;
            const info = modeInfo[currentMode];
            
            modeTitle.textContent = info.title;
            modeSubtitle.textContent = info.subtitle;
            inputLabel.textContent = info.inputLabel;
            
            // Показываем/скрываем секцию автора
            if (info.showAuthor) {
                authorSection.style.display = 'block';
            } else {
                authorSection.style.display = 'none';
            }
        });
    });
    
    // Генерация
    generateBtn.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        
        if (!topic) {
            alert('Введите тему или текст!');
            return;
        }
        
        // Показываем загрузку
        resultDiv.style.display = 'none';
        loadingDiv.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ Генерация...';
        
        // Собираем данные
        const data = {
            mode: currentMode,
            topic: topic,
            volume: volumeSelect.value,
            style: styleSelect.value,
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
                headers: {
                    'Content-Type': 'application/json'
                },
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
    
    // Очистка
    clearBtn.addEventListener('click', function() {
        topicInput.value = '';
        resultDiv.textContent = '';
        statsSpan.textContent = '';
    });
    
    // Копирование
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
    
    // Скачивание
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
    
});
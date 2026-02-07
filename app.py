"""
АвтоКонспект Web — Сервер с AI + Wikipedia
"""

import os
from flask import Flask, render_template, request, jsonify

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

from generator.ai_generator import AIGenerator
from generator.wiki_source import WikiSource

app = Flask(__name__)
generator = AIGenerator(GEMINI_API_KEY)

# Источники Википедии (RU и EN)
wiki_sources = {
    'ru': WikiSource('ru'),
    'en': WikiSource('en'),
}


# ─── Страницы ────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ─── Wikipedia API ───────────────────────────────
@app.route('/wiki/search', methods=['POST'])
def wiki_search():
    """Поиск статей в Википедии"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        lang = data.get('lang', 'ru')

        if not query:
            return jsonify({'error': 'Введите запрос для поиска'}), 400

        wiki = wiki_sources.get(lang, wiki_sources['ru'])
        results = wiki.search(query, limit=8)

        return jsonify({
            'success': True,
            'results': results,
            'lang': lang,
            'query': query
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Генерация текста ────────────────────────────
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json

        mode = data.get('mode', 'referat')
        topic = data.get('topic', '')
        volume = data.get('volume', 'medium')
        style = data.get('style', 'scientific')
        author_info = data.get('author_info', {})

        # Wikipedia
        wiki_titles = data.get('wiki_titles', [])
        wiki_lang = data.get('wiki_lang', 'ru')

        if not topic:
            return jsonify({'error': 'Введите тему!'}), 400

        # Загружаем статьи из Википедии (если выбраны)
        wiki_data = []
        if wiki_titles:
            wiki = wiki_sources.get(wiki_lang, wiki_sources['ru'])
            wiki_data = wiki.get_multiple(wiki_titles)

        result = generator.generate(
            mode=mode,
            topic=topic,
            volume=volume,
            style=style,
            author_info=author_info,
            wiki_data=wiki_data
        )

        words = len(result.split())
        chars = len(result)
        pages = round(chars / 1800, 1)

        return jsonify({
            'success': True,
            'result': result,
            'stats': {
                'words': words,
                'chars': chars,
                'pages': pages
            },
            'wiki_sources_used': len(wiki_data)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def status():
    return jsonify({
        'api_ready': generator.is_ready,
        'model': generator.model_name
    })


if __name__ == '__main__':
    print("=" * 50)
    print("📚 АвтоКонспект Web + Wikipedia")
    print(f"API готов: {generator.is_ready}")
    print(f"Модель: {generator.model_name}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

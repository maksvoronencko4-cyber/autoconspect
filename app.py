"""
АвтоКонспект Web — Wikipedia + Gemini
"""

import os
from flask import Flask, render_template, request, jsonify

# Получаем ключ
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Логируем для отладки (без показа самого ключа)
print(f"🔑 GEMINI_API_KEY найден: {'Да' if GEMINI_API_KEY else 'Нет'}")
print(f"🔑 Длина ключа: {len(GEMINI_API_KEY)} символов")

from generator.ai_generator import AIGenerator

app = Flask(__name__)
generator = AIGenerator(GEMINI_API_KEY)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        
        mode = data.get('mode', 'referat')
        topic = data.get('topic', '')
        volume = data.get('volume', 'medium')
        style = data.get('style', 'scientific')
        author_info = data.get('author_info', {})
        
        if not topic:
            return jsonify({'error': 'Введите тему!'}), 400
        
        result = generator.generate(
            mode=mode,
            topic=topic,
            volume=volume,
            style=style,
            author_info=author_info
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
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def status():
    return jsonify({
        'api_ready': generator.is_ready,
        'model': generator.model_name,
        'key_exists': bool(GEMINI_API_KEY),
        'key_length': len(GEMINI_API_KEY)
    })


if __name__ == '__main__':
    print("=" * 50)
    print("📚 АвтоКонспект Web")
    print(f"✅ Gemini: {generator.is_ready}")
    print(f"✅ Модель: {generator.model_name}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

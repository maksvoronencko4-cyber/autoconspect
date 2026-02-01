"""
АвтоКонспект Web — Главный сервер
"""

from flask import Flask, render_template, request, jsonify
from generator.text_generator import TextGenerator

app = Flask(__name__)
generator = TextGenerator()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """API для генерации текста"""
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
        
        # Статистика
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


if __name__ == '__main__':
    print("=" * 50)
    print("📚 АвтоКонспект Web")
    print("=" * 50)
    print("Открой в браузере: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
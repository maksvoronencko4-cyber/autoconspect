"""
Wikipedia API — получение данных из Википедии
"""

import requests
import re


class WikiSource:
    """Поиск и получение статей из Википедии"""

    def __init__(self, lang='ru'):
        self.lang = lang
        self.base_url = f'https://{lang}.wikipedia.org/w/api.php'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AutoConspect/2.0 (Educational Tool; Python)'
        })

    def search(self, query, limit=8):
        """Поиск статей по запросу"""
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'format': 'json',
                'utf8': 1,
                'srprop': 'snippet|size|wordcount'
            }

            resp = self.session.get(self.base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get('query', {}).get('search', []):
                # Убираем HTML-теги из сниппета
                snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                snippet = (snippet
                           .replace('&quot;', '"')
                           .replace('&amp;', '&')
                           .replace('&lt;', '<')
                           .replace('&gt;', '>')
                           .replace('&nbsp;', ' '))

                results.append({
                    'title': item['title'],
                    'snippet': snippet,
                    'wordcount': item.get('wordcount', 0),
                    'pageid': item['pageid']
                })

            return results

        except Exception as e:
            print(f"[WikiSource] Ошибка поиска: {e}")
            return []

    def get_content(self, title, max_chars=8000):
        """Получение полного текста статьи"""
        try:
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'extracts|info',
                'explaintext': True,
                'inprop': 'url',
                'format': 'json',
                'utf8': 1
            }

            resp = self.session.get(self.base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id == '-1':
                    return None

                content = page_data.get('extract', '')
                if not content:
                    return None

                # Обрезаем слишком длинные статьи
                if len(content) > max_chars:
                    content = content[:max_chars]
                    last_dot = content.rfind('.')
                    if last_dot > max_chars * 0.6:
                        content = content[:last_dot + 1]
                    content += '\n\n[…текст сокращён…]'

                url = page_data.get('fullurl',
                    f'https://{self.lang}.wikipedia.org/wiki/{title.replace(" ", "_")}')

                return {
                    'title': page_data.get('title', title),
                    'content': content,
                    'url': url,
                    'length': len(content)
                }

            return None

        except Exception as e:
            print(f"[WikiSource] Ошибка получения '{title}': {e}")
            return None

    def get_multiple(self, titles, max_total_chars=25000):
        """Получение нескольких статей с балансировкой объёма"""
        if not titles:
            return []

        titles = titles[:5]  # Максимум 5 статей
        max_per_article = max_total_chars // len(titles)

        articles = []
        for title in titles:
            article = self.get_content(title, max_chars=max_per_article)
            if article:
                articles.append(article)

        return articles

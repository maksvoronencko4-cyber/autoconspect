"""
Модуль для получения данных из Википедии
"""

import requests
from typing import Optional, Dict, List


class WikipediaSource:
    """Класс для работы с Wikipedia API"""
    
    def __init__(self, language: str = 'ru'):
        self.language = language
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
    
    def search(self, query: str, limit: int = 3) -> List[str]:
        """Поиск статей по запросу"""
        try:
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': limit,
                'namespace': 0,
                'format': 'json'
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) >= 2:
                return data[1]  # Список названий статей
            return []
            
        except Exception as e:
            print(f"Ошибка поиска Wikipedia: {e}")
            return []
    
    def get_article(self, title: str) -> Optional[Dict]:
        """Получить статью по названию"""
        try:
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'extracts|info',
                'exintro': False,
                'explaintext': True,
                'inprop': 'url',
                'format': 'json'
            }
            
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if page_id == '-1':
                    return None
                
                return {
                    'title': page_data.get('title', title),
                    'content': page_data.get('extract', ''),
                    'url': page_data.get('fullurl', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Ошибка получения статьи: {e}")
            return None
    
    def get_data_for_topic(self, topic: str) -> Dict:
        """Получить данные по теме для генерации"""
        
        # Ищем статьи
        titles = self.search(topic, limit=3)
        
        if not titles:
            return {
                'success': False,
                'error': 'Статьи не найдены',
                'topic': topic,
                'content': '',
                'source': ''
            }
        
        # Собираем контент из найденных статей
        all_content = []
        sources = []
        
        for title in titles:
            article = self.get_article(title)
            if article and article.get('content'):
                content = article['content']
                # Ограничиваем длину каждой статьи
                if len(content) > 8000:
                    content = content[:8000] + "..."
                all_content.append(f"=== {article['title']} ===\n{content}")
                sources.append(f"Википедия: {article['title']} ({article['url']})")
        
        if not all_content:
            return {
                'success': False,
                'error': 'Не удалось получить содержимое',
                'topic': topic,
                'content': '',
                'source': ''
            }
        
        return {
            'success': True,
            'topic': topic,
            'content': "\n\n".join(all_content),
            'source': "\n".join(sources),
            'articles_count': len(all_content)
        }

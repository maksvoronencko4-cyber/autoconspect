"""
AI Генератор текстов — Wikipedia + Gemini
"""

import google.generativeai as genai
from datetime import datetime
from .wikipedia_source import WikipediaSource


class AIGenerator:
    
    def __init__(self, api_key: str = None):
        self.model = None
        self.is_ready = False
        self.model_name = None
        self.error_message = None
        self.wiki = WikipediaSource(language='ru')
        
        print(f"🔧 Инициализация генератора...")
        
        if api_key and len(api_key) > 10:
            self._init_model(api_key)
        else:
            self.error_message = "API ключ пустой или слишком короткий"
            print(f"❌ {self.error_message}")
    
    def _init_model(self, api_key: str):
        """Инициализация модели Gemini"""
        try:
            print("🔄 Подключение к Gemini API...")
            genai.configure(api_key=api_key)
            
            # Актуальные названия моделей (2024-2025)
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-1.5-flash',
                'gemini-1.5-flash-latest',
                'gemini-1.5-pro',
                'gemini-1.5-pro-latest',
                'gemini-pro',
            ]
            
            for model_name in models_to_try:
                try:
                    print(f"🔄 Пробуем: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    # Тестовый запрос
                    response = model.generate_content("Скажи: тест")
                    
                    if response and response.text:
                        self.model = model
                        self.model_name = model_name
                        self.is_ready = True
                        print(f"✅ Подключено: {model_name}")
                        return
                        
                except Exception as e:
                    error_str = str(e).lower()
                    print(f"❌ {model_name}: {e}")
                    
                    # Если ключ неверный — сразу выходим
                    if 'api_key' in error_str or 'invalid' in error_str or 'authentication' in error_str:
                        self.error_message = "Неверный API ключ"
                        print(f"❌ {self.error_message}")
                        return
                    
                    continue
            
            # Попробуем получить список доступных моделей
            try:
                print("🔄 Получаем список доступных моделей...")
                available = list(genai.list_models())
                print(f"📋 Доступно моделей: {len(available)}")
                
                for m in available:
                    if 'generateContent' in str(m.supported_generation_methods):
                        try:
                            model_name = m.name.replace('models/', '')
                            print(f"🔄 Пробуем из списка: {model_name}")
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content("Тест")
                            
                            if response and response.text:
                                self.model = model
                                self.model_name = model_name
                                self.is_ready = True
                                print(f"✅ Подключено: {model_name}")
                                return
                        except:
                            continue
                            
            except Exception as e:
                print(f"❌ Ошибка списка моделей: {e}")
            
            self.error_message = "Не удалось подключить модель. Проверьте ключ API."
            self.is_ready = False
            print(f"❌ {self.error_message}")
            
        except Exception as e:
            self.error_message = f"Ошибка подключения: {str(e)}"
            self.is_ready = False
            print(f"❌ {self.error_message}")
    
    def generate(self, mode: str, topic: str, volume: str, style: str, 
                 author_info: dict = None) -> str:
        """Генерация текста"""
        
        if not self.is_ready:
            return f"""❌ Gemini API не подключен.

Причина: {self.error_message or 'Неизвестная ошибка'}

Как исправить:
1. Получите новый ключ: https://aistudio.google.com/app/apikey
2. На Render: Environment → GEMINI_API_KEY → вставьте ключ
3. Save Changes → сервис перезапустится

Убедитесь что:
- Ключ начинается с "AIza"
- Ключ скопирован полностью
- Gemini API доступен в вашем регионе"""
        
        # Получаем данные из Википедии
        print(f"🔍 Поиск: {topic}")
        wiki_data = self.wiki.get_data_for_topic(topic)
        
        # Строим промпт
        prompt = self._build_prompt(mode, topic, volume, style, wiki_data)
        
        try:
            print("🤖 Генерация...")
            response = self.model.generate_content(prompt)
            result = response.text
            print("✅ Готово")
            
            # Титульная страница
            if author_info and author_info.get('include_title') and mode in ['referat', 'doklad', 'essay']:
                title_page = self._generate_title_page(topic, author_info, mode)
                result = title_page + "\n\n" + result
            
            return result
            
        except Exception as e:
            return f"❌ Ошибка генерации: {str(e)}"
    
    def _build_prompt(self, mode: str, topic: str, volume: str, style: str, wiki_data: dict) -> str:
        """Построение промпта"""
        
        volume_text = {
            "short": "1-2 страницы",
            "medium": "3-5 страниц", 
            "long": "6-10 страниц",
            "very_long": "10-15 страниц"
        }.get(volume, "3-5 страниц")
        
        style_text = {
            "scientific": "научный академический стиль",
            "simple": "простой понятный язык",
            "school": "язык для школьника",
            "university": "язык для студента"
        }.get(style, "научный стиль")
        
        if wiki_data.get('success'):
            wiki_context = f"""
ДАННЫЕ ПО ТЕМЕ "{topic}":
{wiki_data['content'][:12000]}

ИНСТРУКЦИЯ:
- Используй информацию выше
- Перефразируй своими словами
- НЕ указывай источники
"""
        else:
            wiki_context = f"Напиши работу на тему \"{topic}\"."
        
        prompts = {
            "referat": f"""{wiki_context}

Напиши реферат на тему "{topic}".
Объём: {volume_text}. Стиль: {style_text}. Язык: русский.
БЕЗ списка литературы в конце.

Структура:
# РЕФЕРАТ: {topic}
## ВВЕДЕНИЕ
## ГЛАВА 1
### 1.1 ...
### 1.2 ...
## ГЛАВА 2  
### 2.1 ...
## ЗАКЛЮЧЕНИЕ""",

            "conspect": f"""{wiki_context}

Напиши конспект на тему "{topic}".
Объём: {volume_text}. Стиль: {style_text}.

Структура:
# КОНСПЕКТ: {topic}
## Ключевые понятия
## Основные положения
## Выводы""",

            "doklad": f"""{wiki_context}

Напиши доклад на тему "{topic}".
Объём: {volume_text}. Стиль: {style_text}.
Текст для устного выступления.

Структура:
# ДОКЛАД: {topic}
## Вступление
## Основная часть
## Интересные факты
## Заключение""",

            "question": f"""{wiki_context}

Ответь на вопрос: "{topic}"
Объём: {volume_text}. Стиль: {style_text}.

Структура:
# Вопрос: {topic}
## Краткий ответ
## Подробный ответ
## Примеры
## Итог""",

            "retell": f"""{wiki_context}

Сделай пересказ на тему "{topic}".
Объём: {volume_text}. Стиль: {style_text}.

Структура:
# ПЕРЕСКАЗ: {topic}
## О чём
## Подробный пересказ
## Главные мысли""",

            "essay": f"""{wiki_context}

Напиши эссе на тему "{topic}".
Объём: {volume_text}. Стиль: {style_text}.
С личными размышлениями.

Структура:
# ЭССЕ: {topic}
## Вступление
## Размышления
## Заключение"""
        }
        
        return prompts.get(mode, prompts["referat"])
    
    def _generate_title_page(self, topic: str, author_info: dict, mode: str) -> str:
        """Титульная страница"""
        
        work_type = {"referat": "РЕФЕРАТ", "doklad": "ДОКЛАД", "essay": "ЭССЕ"}.get(mode, "РЕФЕРАТ")
        
        edu_type = author_info.get('edu_type', 'Студент')
        grade = author_info.get('grade', '1')
        name = author_info.get('name', '')
        institution = author_info.get('institution', '')
        group = author_info.get('group', '')
        teacher = author_info.get('teacher', '')
        
        grade_text = f"{grade} класса" if edu_type == "Ученик" else f"{grade} курса"
        year = datetime.now().year
        
        lines = [
            "=" * 60, "",
            institution.upper() if institution else "[УЧЕБНОЕ ЗАВЕДЕНИЕ]",
            "", "-" * 60, "",
            work_type, "",
            "на тему:",
            f'«{topic}»',
            "", "-" * 60, "",
            "Выполнил(а):",
            f"{edu_type} {grade_text}",
        ]
        
        if name:
            lines.append(name)
        if group:
            lines.append(f"Группа: {group}")
        if teacher:
            lines.extend(["", f"Преподаватель: {teacher}"])
        
        lines.extend(["", "-" * 60, "", f"{year} год", "", "=" * 60])
        
        return "\n".join(lines)

"""
AI Генератор текстов с Google Gemini
"""

import google.generativeai as genai
from datetime import datetime


class AIGenerator:
    
    def __init__(self, api_key: str = None):
        self.model = None
        self.is_ready = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.is_ready = True
            except Exception as e:
                print(f"Ошибка API: {e}")
    
    def generate(self, mode: str, topic: str, volume: str, style: str, author_info: dict = None) -> str:
        
        if not self.is_ready:
            return "❌ API ключ не настроен"
        
        prompt = self._build_prompt(mode, topic, volume, style)
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            if author_info and author_info.get('include_title') and mode in ['referat', 'doklad', 'essay']:
                title_page = self._generate_title_page(topic, author_info, mode)
                result = title_page + "\n\n" + result
            
            return result
            
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def _build_prompt(self, mode: str, topic: str, volume: str, style: str) -> str:
        
        volume_text = {
            "short": "Напиши кратко, 1-2 страницы.",
            "medium": "Напиши средний объём, 3-5 страниц.",
            "long": "Напиши подробно, 6-10 страниц.",
            "very_long": "Напиши очень подробно, 10-15 страниц."
        }.get(volume, "Средний объём.")
        
        style_text = {
            "scientific": "Научный академический стиль.",
            "simple": "Простой понятный язык.",
            "school": "Язык для школьника.",
            "university": "Язык для студента."
        }.get(style, "Научный стиль.")
        
        prompts = {
            "referat": f"""
Напиши реферат на тему: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык
- Реальные факты, даты, имена

Структура:
# РЕФЕРАТ
## Тема: {topic}

## ВВЕДЕНИЕ
- Актуальность
- Цель и задачи

## ОСНОВНАЯ ЧАСТЬ
### Глава 1. [Название]
[Содержание с фактами]

### Глава 2. [Название]
[Содержание с фактами]

## ЗАКЛЮЧЕНИЕ
- Выводы

## СПИСОК ЛИТЕРАТУРЫ
1. [Источник]
2. [Источник]

Пиши содержательно, чтобы можно было показать учителю!
""",

            "conspect": f"""
Напиши конспект на тему: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык

Структура:
# КОНСПЕКТ: {topic}

## Основные понятия
**Термин** — определение

## Содержание
### 1. [Раздел]
• Факт
• Факт

### 2. [Раздел]
• Факт

## Выводы
1. Вывод
2. Вывод

Пиши реальную информацию по теме!
""",

            "doklad": f"""
Напиши доклад на тему: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык
- Для выступления перед классом

Структура:
# ДОКЛАД: {topic}

## Вступление
Здравствуйте! Тема моего доклада...

## Основная часть
[Подробный рассказ с фактами]

## Заключение
Спасибо за внимание!

Пиши интересно и содержательно!
""",

            "question": f"""
Ответь на вопрос: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык

Структура:
# Вопрос: {topic}

## Краткий ответ
[2-3 предложения]

## Развёрнутый ответ
[Подробное объяснение]

## Примеры
1. Пример
2. Пример

## Вывод
[Итог]
""",

            "retell": f"""
Сделай пересказ текста: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык

Структура:
# ПЕРЕСКАЗ

## Кратко
[О чём текст]

## Подробный пересказ
[Содержание своими словами]

## Главная мысль
[Что хотел сказать автор]
""",

            "essay": f"""
Напиши эссе на тему: "{topic}"

Требования:
- {volume_text}
- {style_text}
- Русский язык
- Личные размышления

Структура:
# ЭССЕ: {topic}

*"Эпиграф"*

## Вступление
[Введение в тему]

## Размышления
[Мысли с аргументами и примерами]

## Заключение
[Личные выводы]
"""
        }
        
        return prompts.get(mode, prompts["referat"])
    
    def _generate_title_page(self, topic: str, author_info: dict, mode: str) -> str:
        
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
            "=" * 60,
            "",
            institution.upper() if institution else "[УЧЕБНОЕ ЗАВЕДЕНИЕ]",
            "",
            "-" * 60,
            "",
            work_type,
            "",
            "на тему:",
            f'«{topic}»',
            "",
            "-" * 60,
            "",
            "Выполнил(а):",
            f"{edu_type} {grade_text}",
        ]
        
        if name:
            lines.append(name)
        if group:
            lines.append(f"Группа: {group}")
        if teacher:
            lines.append("")
            lines.append(f"Преподаватель: {teacher}")
        
        lines.extend(["", "-" * 60, "", f"{year} год", "", "=" * 60])
        
        return "\n".join(lines)

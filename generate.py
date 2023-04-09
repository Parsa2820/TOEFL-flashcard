from dataclasses import dataclass
import os
from bs4 import BeautifulSoup
import jinja2

BOOK_PATH = './book/OEBPS/'


@dataclass
class Lesson:
    title: str
    words: list


@dataclass
class Word:
    word: str
    details: dict


lessons_html = [x for x in os.listdir(BOOK_PATH)
                if x.startswith('lesson') and x.endswith('.html')]
lessons = []

for lesson_html in lessons_html:
    title = lesson_html.removesuffix('.html').replace('_', ' ')
    lesson = Lesson(title=title, words=[])
    with open(os.path.join(BOOK_PATH, lesson_html), 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        for tag in soup.find_all(class_='noindentz'):
            word = Word(word=tag.text, details={})
            if word.word == 'MATCHING':
                break
            details_html = tag.find_next('table')
            for detail_html in details_html.find_all('tr'):
                key = detail_html.find_next('td')
                value = key.find_next('td')
                word.details[key.text] = value.text
            lesson.words.append(word)
    lessons.append(lesson)

with open('readme.md.template') as f:
    template = jinja2.Template(f.read())
with open('README.md', 'w') as f:
    f.write(template.render(lessons))

for lesson in lessons:
    with open('lesson.md.template') as f:
        template = jinja2.Template(f.read())
    with open(f'lessons/{lesson.title}.md', 'w') as f:
        f.write(template.render(lesson=lesson))

from dataclasses import dataclass
import os
import requests
import wget
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


no_audio = 0


def download_audio(word: str) -> None:
    url = f'https://commons.wikimedia.org/wiki/File:En-us-{word}.ogg'
    response = requests.get(url)
    if requests.status_codes == 404:
        no_audio += 1
        return
    file_url = BeautifulSoup(response.content, "html.parser").find(
        class_='fullMedia').findChild('a')['href']
    wget.download(file_url, f'audio/{word}.ogg')


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
            download_audio(word.word)
            details_html = tag.find_next('table')
            for detail_html in details_html.find_all('tr'):
                key = detail_html.find_next('td')
                value = key.find_next('td')
                word.details[key.text.strip()] = value.text
            lesson.words.append(word)
    lessons.append(lesson)

lessons.sort(key=lambda x: x.title)

with open('readme.md.template') as f:
    template = jinja2.Template(f.read())
with open('README.md', 'w') as f:
    f.write(template.render(lessons=lessons))

for lesson in lessons:
    with open('lesson.md.template') as f:
        template = jinja2.Template(f.read())
    with open(f'lessons/{lesson.title}.md', 'w') as f:
        f.write(template.render(lesson=lesson))

print(f'{no_audio=}')
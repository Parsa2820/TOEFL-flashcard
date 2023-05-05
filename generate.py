from dataclasses import dataclass
import os
import requests
import wget
from bs4 import BeautifulSoup
import jinja2
from time import sleep

BOOK_PATH = './book/OEBPS/'


@dataclass
class Lesson:
    title: str
    words: list


@dataclass
class Word:
    word: str
    details: dict


def download_audio(word: str) -> None:
    file_path = f'audio/{word}.ogg'
    if os.path.exists(file_path):
        return
    headers = {
        'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
    url = f'https://commons.wikimedia.org/wiki/File:En-us-{word}.ogg'
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return
    file_url = BeautifulSoup(response.content, "html.parser").find(
        class_='fullMedia').findChild('a')['href']
    sleep(1)
    wget.download(file_url, file_path)


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

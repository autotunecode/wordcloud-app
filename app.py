import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from janome.tokenizer import Tokenizer
import time
import random
from urllib.parse import urljoin

def crawl_all_pages(base_url, exclude_urls, max_pages=50, single_page=False):
    if not base_url.startswith(('http://', 'https://')):
        raise ValueError('URLはHTTPまたはHTTPSで始まる必要があります')
    visited = set()
    to_visit = [base_url]
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited or not url.startswith(base_url) or any(exclude in url for exclude in exclude_urls):
            continue
        visited.add(url)
        try:
            response = requests.get(url, allow_redirects=False)
            st.write(f'クローリングしたURL: {url}')
        except requests.exceptions.TooManyRedirects:
            continue
        response.encoding = response.apparent_encoding
        bs = BeautifulSoup(response.text, 'html.parser')
        if not single_page:
            for link in bs.find_all('a'):
                href = link.get('href')
                exclude_extensions = ['.jpg', '.png', '.gif', '.jpeg', '.pdf']
                if href and not href.startswith('#') and not any(ext in href for ext in exclude_extensions):
                    next_url = urljoin(base_url, href)
                    if next_url.startswith(base_url) and next_url not in visited:
                        to_visit.append(next_url)
        time.sleep(random.uniform(1, 3))
    return visited

def visualize_website_words(base_url, exclude_urls, max_pages, single_page):
    if not base_url.startswith(('http://', 'https://')):
        raise ValueError('URLはHTTPまたはHTTPSで始まる必要があります')
    urls = crawl_all_pages(base_url, exclude_urls, max_pages, single_page)
    t = Tokenizer()
    words = []
    for url in urls:
        try:
            response = requests.get(url, allow_redirects=False)
            response.encoding = response.apparent_encoding
            bs = BeautifulSoup(response.text, 'html.parser')
            text = bs.get_text()
            for token in t.tokenize(text):
                if token.part_of_speech.split(',')[0] == '名詞' and token.surface.isalpha() and len(token.surface) > 1:
                    words.append(token.surface)
            time.sleep(random.uniform(1, 3))
        except requests.exceptions.TooManyRedirects:
            continue
    wordcloud = WordCloud(background_color='white', width=900, height=500, font_path='./ipaexg.ttf').generate(' '.join(words))
    return wordcloud

reset = False
base_url = ''
exclude_urls_input = ''
max_pages = 5
single_page = False

base_url = st.text_input('URLを入力してください', value='' if reset else base_url, help='クロールするウェブサイトのURLを入力してください')
exclude_urls_input = st.text_input('除外したいディレクトリ名や配下URLを指定してください', value='' if reset else exclude_urls_input, help='除外したいURLをカンマ区切りで入力してください')
max_pages = st.slider('最大でクローリングできるページ数を設定してください', 1, 50, value=max_pages if not reset else 5)
single_page = st.checkbox('単一ページのみをクローリングする', value=single_page if not reset else False)

exclude_urls = exclude_urls_input.split(',') if exclude_urls_input else []

if st.button('実行'):
    with st.spinner('画像を生成中...'):
        wordcloud = visualize_website_words(base_url, exclude_urls, max_pages, single_page)
        st.image(wordcloud.to_array())
    st.success('結果が無事表示されました')
    st.empty()

if st.button('リセット'):
    reset = True
    st.empty()


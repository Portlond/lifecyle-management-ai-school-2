import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import requests

# Загружаем ключи из .env файла
load_dotenv()

st.title("🎓 ИИ-помощник учителя")

# Получаем ключи
API_KEY = os.getenv("YA_API_KEY")
FOLDER_ID = os.getenv("YA_FOLDER_ID")

uploaded_file = st.file_uploader("Загрузите учебник (PDF)", type="pdf")

if uploaded_file:
    # Сохраняем файл временно
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Загружаем PDF
    loader = PyPDFLoader("temp.pdf")
    pages = loader.load_and_split()
    
    # Берем текст с первой страницы для теста
    context = pages[0].page_content 
    
    st.write(f"Успешно загружено. Страниц в документе: {len(pages)}")
    
    user_question = st.text_input("Задайте вопрос по тексту первой страницы:")
    
    if st.button("Спросить ИИ"):
        if not API_KEY or not FOLDER_ID:
            st.error("Ошибка: ключи не найдены в файле .env")
        else:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {"Authorization": f"Api-Key {API_KEY}"}
            data = {
                "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
                "messages": [
                    {"role": "system", "text": "Ты — помощник учителя. Отвечай на основе предоставленного текста."},
                    {"role": "user", "text": f"Текст: {context}\n\nВопрос: {user_question}"}
                ]
            }
            
            with st.spinner('ИИ думает...'):
                response = requests.post(url, headers=headers, json=data)
                result = response.json()
            
            if "result" in result:
                st.write("### Ответ ИИ:")
                st.write(result["result"]["alternatives"][0]["message"]["text"])
            else:
                st.error(f"Ошибка API: {result}")
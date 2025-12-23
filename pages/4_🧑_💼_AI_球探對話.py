import streamlit as st
import os
import requests
import time
import google.generativeai as genai

apply_global_style()
st.header("🧑‍💼 AI 對話系統")

gemini_key = "AIzaSyBN5FU3Wk-DcFeRwINM9F6jBLwmS94chng"
client = genai.Client(api_key=gemini_key)

GITHUB_USER = "ChewyChloe"
GITHUB_REPO = "cpbl-project"
GITHUB_FOLDER = "AI_RAG"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FOLDER}"
TARGET_STORE_NAME = "CPBL_Scout_Knowledge_v6"

@st.cache_resource(show_spinner="同步 GitHub 知識庫")
def auto_initialize_rag(_client):
    store = None

    try:
        for s in _client.file_search_stores.list():
            if s.display_name == TARGET_STORE_NAME:
                store = s
                break
    except Exception:
        pass

    if not store:
        try:
            store = _client.file_search_stores.create(
                config={'display_name': TARGET_STORE_NAME}
            )
        except Exception as e:
            print(f"建立 Store 失敗: {e}")
            return None

    existing_files = []
    try:
        pager = _client.file_search_stores.list_files(file_search_store_name=store.name)
        existing_files = list(pager)
    except:
        pass

    if len(existing_files) == 0:
        try:
            res = requests.get(GITHUB_API_URL)
            if res.status_code == 200:
                files_metadata = res.json()
                for i, file_info in enumerate(files_metadata):
                    original_name = file_info['name']
                    lower_name = original_name.lower()

                    if lower_name.endswith(('.pdf', '.txt', '.docx')):
                        f_res = requests.get(file_info['download_url'])

                        if f_res.status_code == 200:
                            safe_ext = ".pdf" if ".pdf" in lower_name else ".txt" if ".txt" in lower_name else ".docx"
                            safe_temp_name = f"temp_doc_{i}{safe_ext}"

                            with open(safe_temp_name, "wb") as f:
                                f.write(f_res.content)

                            if os.path.getsize(safe_temp_name) > 0:
                                mime_type = "application/pdf"
                                if safe_ext == ".txt": mime_type = "text/plain"
                                elif safe_ext == ".docx": mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                                try:
                                    _client.file_search_stores.upload_to_file_search_store(
                                        file=safe_temp_name,
                                        file_search_store_name=store.name,
                                        config={
                                            'display_name': original_name,
                                            'mime_type': mime_type
                                        }
                                    )
                                    time.sleep(1)
                                except Exception as e:
                                    print(f"上傳失敗: {e}")

                            if os.path.exists(safe_temp_name):
                                os.remove(safe_temp_name)
        except Exception as e:
            print(f"GitHub 同步錯誤: {e}")

    return store.name if store else None

# 初始化
store_name = auto_initialize_rag(client)

if not store_name:
    st.error("⚠️ 知識庫初始化失敗。")
    st.stop()

# 對話介面
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("請教專業球探分析..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "tools": [{
                            "file_search": {
                                "file_search_store_names": [store_name]
                            }
                        }],
                        "system_instruction": """
                        你是一位專業的棒球研究員。
                        1. 當使用者問到具體數據或球探報告時，請優先參考「知識庫」中的檔案回答。
                        2. 如果知識庫中沒有相關資訊，或者使用者是在問一般棒球規則、歷史或閒聊，請善用你的「通用棒球知識」直接回答。
                        3. 回答時請保持專業、客觀，絕對不可提及"資料庫"、"根據我們手邊的資料"或"根據..."。
                        4. 語氣輕鬆不嚴肅
                        5. 名字：Brian
                        """
                    }
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"生成回應時發生錯誤: {e}")

# coding=utf-8
import os
import re
import time
import json
import requests
import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# ===================== 配置 =====================
DEEPSEEK_API_KEY = "sk-713be0cfa8f64cc6be21fff21be8bf7a"  # 填你的 DeepSeek Key
PROXY_URL = ""
CONTENT_POOL_FILE = "content_pool.json"

# ===================== 状态 =====================
def init_session_state():
    if "test_mode" not in st.session_state:
        st.session_state.test_mode = False
    if "active_preview" not in st.session_state:
        st.session_state.active_preview = -1
    if "active_edit" not in st.session_state:
        st.session_state.active_edit = -1

# ===================== 工具函数 =====================
def remove_emoji(text):
    if not text:
        return ""
    return re.sub(r"[\U00010000-\U0010ffff]", "", text).strip()

@st.cache_resource
def init_model():
    if PROXY_URL:
        os.environ["HTTP_PROXY"] = PROXY_URL
        os.environ["HTTPS_PROXY"] = PROXY_URL

    if st.session_state.test_mode or not DEEPSEEK_API_KEY:
        class MockModel:
            def invoke(self, messages):
                return type("obj", (object,), {
                    "content": """标题：AI多模态模型太香了！
正文：
宝子们！这个AI模型太牛了～
能同时看懂图片和文字
普通人也能轻松上手！
#AI #大模型 #多模态"""
                })
        return MockModel()

    return ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=0.8
    )

# ===================== DeepSeek 图片生成 =====================
def generate_ds_images(prompt_text, n=3):
    urls = []
    for i in range(n):
        if st.session_state.test_mode or not DEEPSEEK_API_KEY:
            urls.append(f"https://placehold.co/512x512/png?text=AI+Img+{i+1}")
            continue
        try:
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
            data = {
                "prompt": f"{prompt_text} 第{i+1}张",
                "size": "512x512",
                "n": 1
            }
            url_api = "https://api.deepseek.com/v1/images/generate"
            resp = requests.post(url_api, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            img_url = result["data"][0]["url"] if "data" in result else f"https://placehold.co/512x512/png?text=AI+Img+Fallback"
            urls.append(img_url)
        except Exception as e:
            print("DeepSeek 图片生成失败:", e)
            urls.append(f"https://placehold.co/512x512/png?text=AI+Img+Error")
    return urls

# ===================== 内容生成 =====================
def generate_xhs_post(paper_text: str, model) -> dict:
    prompt = f"""
你是一位小红书爆款内容创作者，请将下面的 AI 论文内容改写成一篇适合在小红书发布的图文。

原始内容：
{paper_text}

请严格输出：
标题：xxxx
正文：
xxxx
"""
    response = model.invoke([HumanMessage(content=prompt)]).content.strip()

    title = "未生成标题"
    content = "未生成正文"

    m1 = re.search(r"标题[:：]\s*(.+)", response)
    m2 = re.search(r"正文[:：]\s*([\s\S]+)", response)

    if m1:
        title = m1.group(1).strip()
    if m2:
        content = m2.group(1).strip()

    image_urls = generate_ds_images(f"{title}. {content[:100]}... 小红书封面和内容图")

    return {
        "title": remove_emoji(title),
        "content": remove_emoji(content),
        "original_text": paper_text,
        "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "未发布",
        "image_urls": image_urls
    }

def fetch_trending_ai_papers(use_mock=False):
    if use_mock:
        return [
            "This paper proposes a multimodal large language model.",
            "A lightweight LLM that runs on consumer GPUs."
        ]
    return ["真实抓取逻辑请实现"]

# ===================== 内容池 =====================
def load_content_pool():
    if os.path.exists(CONTENT_POOL_FILE):
        with open(CONTENT_POOL_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_to_content_pool(content):
    pool = load_content_pool()
    pool.append(content)
    with open(CONTENT_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def update_content_pool(index, new_data):
    pool = load_content_pool()
    if 0 <= index < len(pool):
        pool[index] = new_data
        with open(CONTENT_POOL_FILE, "w", encoding="utf-8") as f:
            json.dump(pool, f, ensure_ascii=False, indent=2)

def change_publish_status(index, status):
    pool = load_content_pool()
    if 0 <= index < len(pool):
        pool[index]["status"] = status
        with open(CONTENT_POOL_FILE, "w", encoding="utf-8") as f:
            json.dump(pool, f, ensure_ascii=False, indent=2)

def clear_content_pool():
    with open(CONTENT_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

# ===================== Streamlit =====================
def run_streamlit():
    st.set_page_config("AI小红书内容工厂", "📱", layout="wide")
    init_session_state()

    st.sidebar.title("🎯 功能导航")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🧪 测试模式", type="primary" if st.session_state.test_mode else "secondary", use_container_width=True):
            st.session_state.test_mode = True
            st.rerun()
    with col2:
        if st.button("🔙 正常模式", type="primary" if not st.session_state.test_mode else "secondary", use_container_width=True):
            st.session_state.test_mode = False
            st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("📥 抓取并生成内容"):
        model = init_model()
        papers = fetch_trending_ai_papers(use_mock=st.session_state.test_mode)
        for p in papers:
            post = generate_xhs_post(p, model)
            save_to_content_pool(post)
        st.success(f"已生成 {len(papers)} 条内容")

    if st.sidebar.button("🗑️ 清空内容池"):
        clear_content_pool()
        st.success("内容池已清空")

    st.title("📦 内容池管理后台")
    content_pool = load_content_pool()
    if not content_pool:
        st.info("📭 内容池为空，请点击左侧按钮生成内容")
        return

    for idx, content in enumerate(content_pool):
        with st.expander(f"📝 内容 #{idx + 1} | {content['status']} | {content['create_time']}"):
            col1, col2 = st.columns([2, 8])

            with col1:
                if st.button("👀 预览", key=f"preview_{idx}", use_container_width=True):
                    st.session_state.active_preview = idx
                    st.session_state.active_edit = -1
                if st.button("✏️ 编辑", key=f"edit_{idx}", use_container_width=True):
                    st.session_state.active_edit = idx
                    st.session_state.active_preview = -1
                if content["status"] != "已发布":
                    if st.button("🚀 模拟发布", key=f"publish_{idx}", use_container_width=True):
                        change_publish_status(idx, "已发布")
                        st.session_state.active_preview = idx
                        st.session_state.active_edit = -1
                        st.rerun()
                else:
                    st.button("✅ 已发布", disabled=True, use_container_width=True)

            with col2:
                if st.session_state.active_preview == idx:
                    st.subheader("📱 小红书发布页预览")

                    # 横向轮播图片html，左右渐变
                    images_html = "".join([f'<div style="flex:none; margin-right:8px;"><img src="{u}" style="width:200px; height:200px; border-radius:12px;"></div>' for u in content.get("image_urls", [])])
                    st.markdown(f"""
                    <div style="
                        width:360px; height:640px; overflow-y:auto;
                        margin:0 auto;
                        border:12px solid #111;
                        border-radius:36px;
                        padding:16px;
                        background:#fff;
                        font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;
                        box-shadow:0 0 20px rgba(0,0,0,0.2);
                    ">
                        <div style="text-align:center;color:#888;font-size:12px;margin-bottom:8px;">小红书 · 发布页预览</div>
                        <div style="
                            display:flex; overflow-x:auto; overflow-y:hidden; padding-bottom:8px;
                            mask-image: linear-gradient(to right, rgba(0,0,0,0), black 10%, black 90%, rgba(0,0,0,0));
                            -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,0), black 10%, black 90%, rgba(0,0,0,0));
                        ">{images_html}</div>
                        <div style="font-weight:600;font-size:16px;margin-top:12px;margin-bottom:8px;">{content['title']}</div>
                        <div style="font-size:14px;line-height:1.6;color:#333;white-space:pre-wrap;">{content['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**原始AI论文内容：**\n{content['original_text']}")
                    if st.button("🔙 关闭预览", key=f"close_preview_{idx}"):
                        st.session_state.active_preview = -1
                        st.rerun()

                elif st.session_state.active_edit == idx:
                    st.subheader("✏️ 编辑内容")
                    new_title = st.text_input("标题", value=content["title"], key=f"title_{idx}")
                    new_content = st.text_area("正文", value=content["content"], height=200, key=f"content_{idx}")
                    new_original = st.text_area("原始内容", value=content["original_text"], height=120, key=f"original_{idx}")

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 保存修改", key=f"save_{idx}", use_container_width=True):
                            new_data = {
                                "title": new_title,
                                "content": new_content,
                                "original_text": new_original,
                                "create_time": content["create_time"],
                                "status": content["status"],
                                "image_urls": content.get("image_urls", [])
                            }
                            update_content_pool(idx, new_data)
                            st.session_state.active_edit = -1
                            st.success("✅ 修改已保存")
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ 取消编辑", key=f"cancel_{idx}", use_container_width=True):
                            st.session_state.active_edit = -1
                            st.rerun()
                else:
                    st.markdown(f"**标题：** {content['title'][:30]}...")
                    st.markdown(f"**正文预览：** {content['content'][:80]}...")

# ====== 添加2个测试案例 ======
def add_test_cases():
    if not load_content_pool():
        model = init_model()
        test_cases = [
            generate_xhs_post("This paper proposes a multimodal large language model.", model),
            generate_xhs_post("A lightweight LLM that runs on consumer GPUs.", model)
        ]
        for case in test_cases:
            save_to_content_pool(case)

if __name__ == "__main__":
    init_session_state()
    add_test_cases()
    run_streamlit()

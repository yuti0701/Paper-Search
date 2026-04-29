import streamlit as st
import fitz  # PyMuPDF
import requests
import json
import subprocess
import os
import urllib.request
import sys
from fpdf import FPDF

# 인코딩 설정
if sys.platform == 'win32':
    os.environ["PYTHONIOENCODING"] = "utf-8"

@st.cache_resource
def setup_resources():
    try:
        if not os.path.exists("NanumGothic.ttf"):
            urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf", "NanumGothic.ttf")
        requests.get("http://localhost:11434", timeout=1)
    except:
        subprocess.Popen("ollama serve", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000 if sys.platform == 'win32' else 0)
    return True

def clean_val(val):
    if val is None or val == "N/A": return "Not Available"
    return str(val)

def analyze_paper(text):
    url = "http://localhost:11434/api/generate"
    safe_text = text.encode('utf-8', errors='ignore').decode('utf-8')
    prompt = f"Extract metadata as JSON. Keep Original Language. Keys: title, first_author, corresponding_author, email, purpose, specimen, period, sample_size, age, equipment, kit, results, conclusion. Text: {safe_text}"
    
    payload = {"model": "phi3", "prompt": prompt, "format": "json", "stream": False, "options": {"temperature": 0, "num_predict": 1200}}
    try:
        response = requests.post(url, json=payload, timeout=600)
        return json.loads(json.loads(response.content.decode('utf-8'))['response'])
    except: return None

# --- HTML 보고서 템플릿 생성 함수 ---
def generate_html_dashboard(res):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; }}
        </style>
    </head>
    <body class="p-4 md:p-10">
        <div class="max-w-5xl mx-auto bg-white shadow-2xl rounded-3xl overflow-hidden border border-slate-100">
            <!-- Header -->
            <div class="bg-slate-900 p-8 text-white">
                <div class="flex justify-between items-start">
                    <span class="bg-blue-500 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest">Scientific Report</span>
                    <i class="fa-solid fa-microscope text-3xl text-slate-400"></i>
                </div>
                <h1 class="text-3xl font-bold mt-4 leading-tight">{clean_val(res.get('title'))}</h1>
                <div class="flex flex-wrap gap-6 mt-6 text-slate-300 text-sm">
                    <span><i class="fa-solid fa-user-pen mr-2"></i>{clean_val(res.get('first_author'))}</span>
                    <span><i class="fa-solid fa-envelope-open-text mr-2"></i>{clean_val(res.get('corresponding_author'))} ({clean_val(res.get('email'))})</span>
                </div>
            </div>

            <!-- Content Grid -->
            <div class="p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Left: Methods -->
                <div class="md:col-span-1 space-y-6">
                    <div class="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                        <h3 class="text-slate-900 font-bold mb-4 flex items-center"><i class="fa-solid fa-flask mr-2 text-blue-500"></i> Methodology</h3>
                        <ul class="space-y-3 text-sm text-slate-600">
                            <li><strong class="text-slate-800">Specimen:</strong> {clean_val(res.get('specimen'))}</li>
                            <li><strong class="text-slate-800">Sample Size:</strong> {clean_val(res.get('sample_size'))}</li>
                            <li><strong class="text-slate-800">Age:</strong> {clean_val(res.get('age'))}</li>
                            <li><strong class="text-slate-800">Period:</strong> {clean_val(res.get('period'))}</li>
                        </ul>
                    </div>
                    <div class="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                        <h3 class="text-slate-900 font-bold mb-4 flex items-center"><i class="fa-solid fa-gears mr-2 text-blue-500"></i> Equipment & Kit</h3>
                        <ul class="space-y-3 text-sm text-slate-600">
                            <li><strong class="text-slate-800">Device:</strong> {clean_val(res.get('equipment'))}</li>
                            <li><strong class="text-slate-800">Kit:</strong> {clean_val(res.get('kit'))}</li>
                        </ul>
                    </div>
                </div>

                <!-- Right: Summary -->
                <div class="md:col-span-2 space-y-8">
                    <section>
                        <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center"><i class="fa-solid fa-bullseye mr-2 text-red-500"></i> Research Purpose</h3>
                        <p class="text-slate-600 leading-relaxed text-sm bg-white p-4 rounded-xl border border-slate-100 italic">"{clean_val(res.get('purpose'))}"</p>
                    </section>
                    <section>
                        <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center"><i class="fa-solid fa-chart-line mr-2 text-emerald-500"></i> Core Results</h3>
                        <div class="bg-emerald-50 p-5 rounded-2xl text-emerald-900 text-sm leading-relaxed border border-emerald-100">
                            {clean_val(res.get('results'))}
                        </div>
                    </section>
                    <section>
                        <h3 class="text-lg font-bold text-slate-900 mb-3 flex items-center"><i class="fa-solid fa-flag-checkered mr-2 text-blue-500"></i> Conclusion</h3>
                        <div class="bg-blue-50 p-5 rounded-2xl text-blue-900 text-sm leading-relaxed border border-blue-100">
                            {clean_val(res.get('conclusion'))}
                        </div>
                    </section>
                </div>
            </div>
            <div class="bg-slate-50 p-4 text-center text-slate-400 text-xs">Generated by Briefly AI Summary System</div>
        </div>
    </body>
    </html>
    """
    return html_template

def main():
    st.set_page_config(page_title="Briefly", page_icon="📄", layout="wide")
    setup_resources()

    st.title("📑 Briefly HTML Dashboard")
    st.caption("논문 분석 결과를 세련된 웹 대시보드로 시각화합니다.")
    st.divider()

    uploaded_file = st.file_uploader("PDF 업로드", type="pdf")

    if uploaded_file:
        if st.button("🚀 정밀 분석 및 대시보드 생성", use_container_width=True):
            with st.spinner("AI가 웹 대시보드를 구축 중입니다..."):
                try:
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    combined_text = "".join([p.get_text() for p in doc[:3]])
                    if len(doc) > 3: combined_text += "\n" + doc[-1].get_text()
                    
                    result = analyze_paper(combined_text[:7500])
                    
                    if result:
                        st.success("✅ 분석 완료!")
                        
                        # 1. HTML 대시보드 렌더링
                        report_html = generate_html_dashboard(result)
                        st.components.v1.html(report_html, height=850, scrolling=True)
                        
                        st.divider()

                        # 2. 다운로드 섹션 (HTML 및 Email)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 HTML 결과 파일 다운로드",
                                data=report_html,
                                file_name=f"Briefly_{uploaded_file.name}.html",
                                mime="text/html",
                                use_container_width=True
                            )
                        with col2:
                            with st.expander("📧 Email 복사용 텍스트"):
                                email_text = f"제목: {result.get('title')}\n\n결과: {result.get('results')}\n\n결론: {result.get('conclusion')}"
                                st.code(email_text)

                except Exception as e:
                    st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
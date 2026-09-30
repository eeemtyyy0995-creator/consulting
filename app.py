import streamlit as st
import pandas as pd
import openpyxl
from google import genai
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="AI Case Championship Solver", page_icon="🎓", layout="wide")

st.title("🎓 منصة حل الكيسات والتعديل الذكي - Aramco Case Championship")
st.write("رفع الملفات ➔ تحليل شامل باللغة الإنجليزية 100% ➔ معاينة التقرير ➔ تعديلات مخصصة.")

# Session State Management
if 'solution_generated' not in st.session_state:
    st.session_state.solution_generated = False
if 'full_solution' not in st.session_state:
    st.session_state.full_solution = ""
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# Helper Function: Create PDF File
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    
    for line in text_content.split('\n'):
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line)
    
    return bytes(pdf.output())

# Helper Function: Generate Content using official google-genai SDK
def generate_with_sdk(api_key, prompt):
    # تهيئة الـ Client باستخدام المكتبة الجديدة google-genai
    client = genai.Client(api_key=api_key.strip())
    
    # قائمة بالسيرفرات المتاحة في SDK التجربة بالتتابع لمنع أي خطأ 503 أو 404
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash'
    ]
    
    last_err = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue
            
    raise Exception(f"تعذر استدعاء SDK. التفاصيل: {str(last_err)}")

# Sidebar Inputs
st.sidebar.header("⚙️ 1. File Inputs & Settings")

uploaded_excel = st.sidebar.file_uploader("Upload Case Data (Excel)", type=["xlsx", "xls"])
uploaded_pdf = st.sidebar.file_uploader("Upload Instructions / Q&A (PDF)", type=["pdf"])

num_slides = st.sidebar.number_input("Target Number of Slides (e.g., 10):", min_value=5, max_value=20, value=10)

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# Process & Generate Solution
if st.sidebar.button("🚀 Generate Full English Case Solution (100%)"):
    if not uploaded_excel or not uploaded_pdf or not api_key:
        st.error("⚠️ Please upload both Excel data and PDF instructions, and provide a valid Gemini API Key!")
    else:
        with st.spinner("Analyzing data exhibits, applying Q&A rules, and generating full English solution via SDK..."):
            try:
                # Read Excel File Exhibits
                xls = pd.ExcelFile(uploaded_excel)
                sheets_summary = ""
                for sheet in xls.sheet_names:
                    df = pd.read_excel(uploaded_excel, sheet_name=sheet)
                    sheets_summary += f"\n--- Sheet: {sheet} ---\n" + df.head(5).to_string()
                
                st.session_state.excel_data = uploaded_excel
                
                # AI Prompt
                prompt = f"""
                You are a top-tier management consultant. Analyze the Rakiza case exhibits and produce a complete, professional, highly detailed slide deck outline in ENGLISH ONLY.
                
                Strict Requirements:
                1. Language: MUST be 100% Professional English.
                2. Structure: Output EXACTLY {num_slides} slides.
                3. Case Deliverables: Address all 4 core questions precisely based on Q&A instructions:
                   - Q1: Annual truck leasing market size ($M and truck units, without double-counting return legs or merging freight routes).
                   - Q2: Total 5-year investment needed (CAPEX for 45 hubs and 3,600 leased trucks by Year 5).
                   - Q3: Current valuation assessment ($120M for 20% = $600M pre-money) and apply 1/5 local risk discount.
                   - Q4: Explicit investment decision, deal terms, governance, and risk mitigations.
                
                Available Data Exhibits Summary:
                {sheets_summary}
                
                Format: Output each slide with a clear Header (e.g., "Slide X: Title"), Bullet Points, Key Figures, Data Sources, and Strategic Rationale.
                """
                
                solution_text = generate_with_sdk(api_key, prompt)
                
                st.session_state.full_solution = solution_text
                st.session_state.solution_generated = True
                st.success("✨ English Case Solution Generated Successfully!")
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")

# Review & Targeted Editing Section
if st.session_state.solution_generated:
    st.subheader("📋 Final Slide Deck Draft Review (English)")
    
    st.markdown(st.session_state.full_solution)
    
    st.markdown("---")
    st.subheader("🛠️ Targeted Edits / Modifications")
    st.info("💡 Enter your specific edit request below in Arabic or English.")
    
    user_edits = st.text_area("Specify your edits here:")
    
    if st.button("🔄 Apply Targeted Edit"):
        if user_edits:
            with st.spinner("Applying requested edit via SDK while preserving full slide deck structure..."):
                try:
                    edit_prompt = f"""
                    You are a senior consulting editor. Update the following slide deck based on the user's specific feedback.
                    
                    STRICT CONSTRAINTS:
                    1. Language: ALL output MUST remain in 100% Professional English.
                    2. Maintain EXACTLY {num_slides} slides and preserve all unchanged data/figures.
                    3. Modify ONLY what the user explicitly requested. Do not drop or abbreviate any details.
                    
                    CURRENT SLIDE DECK:
                    {st.session_state.full_solution}
                    
                    USER EDIT REQUEST:
                    "{user_edits}"
                    """
                    
                    updated_text = generate_with_sdk(api_key, edit_prompt)
                    
                    st.session_state.full_solution = updated_text
                    st.success("✅ Solution updated in English while preserving structure!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error occurred: {str(e)}")

# Download Section
st.markdown("---")
st.subheader("📥 Export Final Deliverables")

if st.session_state.solution_generated:
    pdf_bytes = create_pdf(st.session_state.full_solution)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Slides Solution (.pdf)",
            data=pdf_bytes,
            file_name="Aramco_Case_Final_Slides_Solution_EN.pdf",
            mime="application/pdf"
        )
    with col2:
        if st.session_state.excel_data:
            st.download_button(
                label="📊 Download Processed Excel Data (.xlsx)",
                data=st.session_state.excel_data,
                file_name="Rakiza_Case_Processed_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )import streamlit as st
import pandas as pd
import openpyxl
from google import genai
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="AI Case Championship Solver", page_icon="🎓", layout="wide")

st.title("🎓 منصة حل الكيسات والتعديل الذكي - Aramco Case Championship")
st.write("رفع الملفات ➔ تحليل شامل باللغة الإنجليزية 100% ➔ معاينة التقرير ➔ تعديلات مخصصة.")

# Session State Management
if 'solution_generated' not in st.session_state:
    st.session_state.solution_generated = False
if 'full_solution' not in st.session_state:
    st.session_state.full_solution = ""
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# Helper Function: Create PDF File
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    
    for line in text_content.split('\n'):
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line)
    
    return bytes(pdf.output())

# Helper Function: Generate Content using official google-genai SDK
def generate_with_sdk(api_key, prompt):
    # تهيئة الـ Client باستخدام المكتبة الجديدة google-genai
    client = genai.Client(api_key=api_key.strip())
    
    # قائمة بالسيرفرات المتاحة في SDK التجربة بالتتابع لمنع أي خطأ 503 أو 404
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash'
    ]
    
    last_err = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue
            
    raise Exception(f"تعذر استدعاء SDK. التفاصيل: {str(last_err)}")

# Sidebar Inputs
st.sidebar.header("⚙️ 1. File Inputs & Settings")

uploaded_excel = st.sidebar.file_uploader("Upload Case Data (Excel)", type=["xlsx", "xls"])
uploaded_pdf = st.sidebar.file_uploader("Upload Instructions / Q&A (PDF)", type=["pdf"])

num_slides = st.sidebar.number_input("Target Number of Slides (e.g., 10):", min_value=5, max_value=20, value=10)

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# Process & Generate Solution
if st.sidebar.button("🚀 Generate Full English Case Solution (100%)"):
    if not uploaded_excel or not uploaded_pdf or not api_key:
        st.error("⚠️ Please upload both Excel data and PDF instructions, and provide a valid Gemini API Key!")
    else:
        with st.spinner("Analyzing data exhibits, applying Q&A rules, and generating full English solution via SDK..."):
            try:
                # Read Excel File Exhibits
                xls = pd.ExcelFile(uploaded_excel)
                sheets_summary = ""
                for sheet in xls.sheet_names:
                    df = pd.read_excel(uploaded_excel, sheet_name=sheet)
                    sheets_summary += f"\n--- Sheet: {sheet} ---\n" + df.head(5).to_string()
                
                st.session_state.excel_data = uploaded_excel
                
                # AI Prompt
                prompt = f"""
                You are a top-tier management consultant. Analyze the Rakiza case exhibits and produce a complete, professional, highly detailed slide deck outline in ENGLISH ONLY.
                
                Strict Requirements:
                1. Language: MUST be 100% Professional English.
                2. Structure: Output EXACTLY {num_slides} slides.
                3. Case Deliverables: Address all 4 core questions precisely based on Q&A instructions:
                   - Q1: Annual truck leasing market size ($M and truck units, without double-counting return legs or merging freight routes).
                   - Q2: Total 5-year investment needed (CAPEX for 45 hubs and 3,600 leased trucks by Year 5).
                   - Q3: Current valuation assessment ($120M for 20% = $600M pre-money) and apply 1/5 local risk discount.
                   - Q4: Explicit investment decision, deal terms, governance, and risk mitigations.
                
                Available Data Exhibits Summary:
                {sheets_summary}
                
                Format: Output each slide with a clear Header (e.g., "Slide X: Title"), Bullet Points, Key Figures, Data Sources, and Strategic Rationale.
                """
                
                solution_text = generate_with_sdk(api_key, prompt)
                
                st.session_state.full_solution = solution_text
                st.session_state.solution_generated = True
                st.success("✨ English Case Solution Generated Successfully!")
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")

# Review & Targeted Editing Section
if st.session_state.solution_generated:
    st.subheader("📋 Final Slide Deck Draft Review (English)")
    
    st.markdown(st.session_state.full_solution)
    
    st.markdown("---")
    st.subheader("🛠️ Targeted Edits / Modifications")
    st.info("💡 Enter your specific edit request below in Arabic or English.")
    
    user_edits = st.text_area("Specify your edits here:")
    
    if st.button("🔄 Apply Targeted Edit"):
        if user_edits:
            with st.spinner("Applying requested edit via SDK while preserving full slide deck structure..."):
                try:
                    edit_prompt = f"""
                    You are a senior consulting editor. Update the following slide deck based on the user's specific feedback.
                    
                    STRICT CONSTRAINTS:
                    1. Language: ALL output MUST remain in 100% Professional English.
                    2. Maintain EXACTLY {num_slides} slides and preserve all unchanged data/figures.
                    3. Modify ONLY what the user explicitly requested. Do not drop or abbreviate any details.
                    
                    CURRENT SLIDE DECK:
                    {st.session_state.full_solution}
                    
                    USER EDIT REQUEST:
                    "{user_edits}"
                    """
                    
                    updated_text = generate_with_sdk(api_key, edit_prompt)
                    
                    st.session_state.full_solution = updated_text
                    st.success("✅ Solution updated in English while preserving structure!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error occurred: {str(e)}")

# Download Section
st.markdown("---")
st.subheader("📥 Export Final Deliverables")

if st.session_state.solution_generated:
    pdf_bytes = create_pdf(st.session_state.full_solution)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Slides Solution (.pdf)",
            data=pdf_bytes,
            file_name="Aramco_Case_Final_Slides_Solution_EN.pdf",
            mime="application/pdf"
        )
    with col2:
        if st.session_state.excel_data:
            st.download_button(
                label="📊 Download Processed Excel Data (.xlsx)",
                data=st.session_state.excel_data,
                file_name="Rakiza_Case_Processed_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

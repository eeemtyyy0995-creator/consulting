import streamlit as st
import pandas as pd
import openpyxl
from io import BytesIO
import google.generativeai as genai

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
with st.spinner("Analyzing data exhibits, applying Q&A rules, and generating full English solution..."):
genai.configure(api_key=api_key)

# Read Excel File Exhibits
xls = pd.ExcelFile(uploaded_excel)
sheets_summary = ""
for sheet in xls.sheet_names:
df = pd.read_excel(uploaded_excel, sheet_name=sheet)
sheets_summary += f"\n--- Sheet: {sheet} ---\n" + df.head(5).to_string()

st.session_state.excel_data = uploaded_excel

# AI Prompt tailored for strictly English outputs matching Q&A constraints
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

model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(prompt)

st.session_state.full_solution = response.text
st.session_state.solution_generated = True
st.success("✨ English Case Solution Generated Successfully!")

# Review & Targeted Editing Section
if st.session_state.solution_generated:
st.subheader("📋 Final Slide Deck Draft Review (English)")

# Display Generated Solution
st.markdown(st.session_state.full_solution)

st.markdown("---")
st.subheader("🛠️ Targeted Edits / Modifications")
st.info("💡 Enter your specific edit request below in Arabic or English (e.g., 'Update Slide 3 valuation discount to reflect 20%'). The AI will modify ONLY that section while maintaining the complete English output and formatting.")

user_edits = st.text_area("Specify your edits here:")

if st.button("🔄 Apply Targeted Edit"):
if user_edits:
with st.spinner("Applying requested edit while preserving full slide deck structure..."):
genai.configure(api_key=api_key)

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

model = genai.GenerativeModel('gemini-1.5-pro')
updated_response = model.generate_content(edit_prompt)

st.session_state.full_solution = updated_response.text
st.success("✅ Solution updated in English while preserving structure!")
st.rerun()

# Download Section
st.markdown("---")
st.subheader("📥 Export Final Deliverables")

report_bytes = st.session_state.full_solution.encode('utf-8')

col1, col2 = st.columns(2)
with col1:
st.download_button(
label="📄 Download Slides Solution (.md / .txt)",
data=report_bytes,
file_name="Aramco_Case_Final_Slides_Solution_EN.md",
mime="text/markdown"
)
with col2:
if st.session_state.excel_data:
st.download_button(
label="📊 Download Processed Excel Data (.xlsx)",
data=st.session_state.excel_data,
file_name="Rakiza_Case_Processed_Data.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


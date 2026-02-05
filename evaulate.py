import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from PyPDF2 import PdfReader

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Content Evaluation",
    layout="centered"
)

st.title("📘 Student Content Evaluation Tool")
st.write("Upload a file (PDF, CSV, JSON, TXT) or enter a website URL for evaluation.")

# ---------------- INPUT OPTIONS ----------------
option = st.radio("Choose Input Type", ["Upload File", "Website URL"])

uploaded_file = None
url = None

if option == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "csv", "json", "txt"]
    )
else:
    url = st.text_input("🔗 Enter Website URL")

# ---------------- TEXT EXTRACTION ----------------
def extract_text_from_file(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text

    elif file.type == "text/csv":
        df = pd.read_csv(file)
        return df.to_string()

    elif file.type == "application/json":
        data = json.load(file)
        return json.dumps(data, indent=2)

    elif file.type == "text/plain":
        return file.read().decode("utf-8")

    return ""

def extract_text_from_url(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.stripped_strings)

# ---------------- EVALUATION LOGIC ----------------
def evaluate_content(text):
    word_count = len(text.split())
    sentence_count = len(re.findall(r"[.!?]", text))
    avg_sentence_len = word_count / sentence_count if sentence_count else 0

    content_score = min(100, word_count // 8)
    clarity_score = 100 if avg_sentence_len < 20 else 70
    structure_score = 80 if "\n" in text else 65
    grammar_score = 85

    overall = int((content_score + clarity_score + structure_score + grammar_score) / 4)

    suggestions = []
    if content_score < 70:
        suggestions.append("Add more academic and subject-related content.")
    if clarity_score < 80:
        suggestions.append("Use shorter sentences to improve clarity.")
    if structure_score < 75:
        suggestions.append("Organize content using headings, lists, and paragraphs.")
    if grammar_score < 90:
        suggestions.append("Check grammar and punctuation carefully.")

    if not suggestions:
        suggestions.append("The content is well-prepared. Minor refinements can improve quality further.")

    return {
        "Content Quality": int(content_score),
        "Clarity": int(clarity_score),
        "Structure": int(structure_score),
        "Grammar": int(grammar_score),
        "Overall": overall,
        "Suggestions": suggestions
    }

# ---------------- BUTTON ----------------
if st.button("Evaluate Content"):

    try:
        if option == "Upload File" and uploaded_file:
            text = extract_text_from_file(uploaded_file)
        elif option == "Website URL" and url:
            text = extract_text_from_url(url)
        else:
            st.warning("⚠️ Please upload a file or enter a URL.")
            st.stop()

        if len(text) < 200:
            st.error("❌ Content is too short for evaluation.")
            st.stop()

        result = evaluate_content(text)

        # ---------------- OUTPUT ----------------
        st.success("✅ Evaluation Completed")

        st.subheader("📊 Evaluation Results")
        st.write(f"**Content Quality Score:** {result['Content Quality']} / 100")
        st.write(f"**Clarity Score:** {result['Clarity']} / 100")
        st.write(f"**Structure Score:** {result['Structure']} / 100")
        st.write(f"**Grammar Score:** {result['Grammar']} / 100")
        st.markdown(f"### ⭐ **Overall Score: {result['Overall']} / 100**")

        st.subheader("🛠 Improvement Suggestions for Students")
        for s in result["Suggestions"]:
            st.write(f"- {s}")

    except Exception:
        st.error("❌ Unable to process the input. Please try another file or URL.")

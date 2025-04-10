import os
import fitz  # PyMuPDF for PDF text extraction
import streamlit as st
from secret_keys import gemini_api_key
from langchain_google_genai import GoogleGenerativeAI

# Set API key
os.environ["GOOGLE_API_KEY"] = gemini_api_key


# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()


# Function to detect missing sections
def detect_missing_sections(text):
    required_sections = ["Education", "Experience", "Skills", "Projects", "Certifications"]
    missing_sections = [section for section in required_sections if section.lower() not in text.lower()]
    return missing_sections


# Function to query Gemini AI
def query_gemini(prompt, text):
    model = GoogleGenerativeAI(model="gemini-1.5-pro-latest")
    response = model.invoke(f"{prompt}\n\n{text}")
    return response if response else "Error generating response."


# Streamlit UI
st.title("📄 Resume Critique Bot")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

    # Extract text from resume
    resume_text = extract_text_from_pdf(uploaded_file)

    # Detect missing sections
    missing_sections = detect_missing_sections(resume_text)

    if missing_sections:
        st.warning(f"⚠️ Your resume is missing sections: {', '.join(missing_sections)}")

    # AI critique options
    st.subheader("💡 Choose critique options:")
    critique_options = st.multiselect(
        "Select aspects to improve:",
        ["Overall Review", "Experience Section", "Skills Section", "Formatting & Structure"]
    )

    if st.button("Analyze Resume"):
        if not critique_options:
            st.warning("⚠️ Please select at least one critique option.")
        else:
            st.info("⏳ Analyzing your resume...")

            # Generate critique based on selection
            critique_responses = {}
            for option in critique_options:
                prompt = f"Analyze the '{option}' in this resume and provide improvements."
                critique_responses[option] = query_gemini(prompt, resume_text)

            # Display AI Feedback
            st.subheader("📝 AI Feedback:")
            for section, response in critique_responses.items():
                st.markdown(f"### {section} Feedback:")
                st.write(response)
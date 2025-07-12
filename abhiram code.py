import sys
import time
import psutil
import os
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM
import PyPDF2
import streamlit as st

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024**3)

@st.cache_resource
def load_model():
    model_path = "./mistral-7b-instruct-v0.1-int8-ov"
    try:
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = OVModelForCausalLM.from_pretrained(model_path)
        load_time = time.time() - start_time
        return tokenizer, model, load_time
    except Exception as e:
        st.error(f"Error loading model: {e}")
        sys.exit(1)

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def generate_response(model, tokenizer, prompt, max_new_tokens):
    inputs = tokenizer(prompt, return_tensors="pt")
    start_time = time.time()
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, pad_token_id=tokenizer.eos_token_id)
    end_time = time.time()
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    prompt_prefix = prompt.replace("<s>", "").strip()
    clean_response = response.replace(prompt_prefix, "").strip()
    output_tokens = len(outputs[0])
    response_time = end_time - start_time
    throughput = output_tokens / response_time if response_time > 0 else 0
    memory_usage = psutil.Process().memory_info().rss / (1024**2)
    word_count = len(clean_response.split())
    return clean_response, response_time, throughput, memory_usage, word_count

def list_pdfs(pdf_dir="./pdfs"):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        return []
    return [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]

st.set_page_config(page_title="PDF Chatbot", layout="wide")
st.title("PDF Chatbot with Mistral-7B")

# Load model
tokenizer, model, load_time = load_model()
disk_size = get_folder_size("./mistral-7b-instruct-v0.1-int8-ov")
st.info(f"Model loaded in {load_time:.2f} seconds. Disk usage: {disk_size:.2f} GB")

# Sidebar for PDF selection and settings
with st.sidebar:
    st.header("PDF Selection")
    pdf_dir = "./pdfs"
    pdf_files = list_pdfs(pdf_dir)
    if not pdf_files:
        st.warning(f"No PDF files found in {pdf_dir}. Please add PDFs to the directory.")
    else:
        selected_pdf = st.selectbox("Select a PDF:", pdf_files, key="pdf_select")
        if st.button("Load PDF"):
            if "selected_pdf" not in st.session_state or selected_pdf != st.session_state.selected_pdf:
                with st.spinner(f"Extracting text from {selected_pdf}..."):
                    pdf_path = os.path.join(pdf_dir, selected_pdf)
                    pdf_text = extract_pdf_text(pdf_path)
                    if pdf_text:
                        st.session_state.pdf_text = pdf_text
                        st.session_state.selected_pdf = selected_pdf
                        st.success("PDF text extracted successfully.")
                    else:
                        st.error("No text could be extracted from the PDF.")

    st.header("Settings")
    word_limit = st.number_input("Response word limit", min_value=10, max_value=500, value=100, step=10)
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared successfully. The model will be reloaded on the next interaction.")

# Chat interface
if "pdf_text" in st.session_state and st.session_state.pdf_text:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.get("messages", []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask a question about the PDF:")
    if prompt:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Generating response..."):
                    full_prompt = (f"<s>[INST] Based on the following document content, answer the question in {word_limit} words or less:\n\n"
                                   f"{st.session_state.pdf_text[:1000]}\n\nQuestion: {prompt} [/INST]")
                    try:
                        max_new_tokens = int(word_limit * 1.5)
                        response, response_time, throughput, memory_usage, word_count = generate_response(
                            model, tokenizer, full_prompt, max_new_tokens=max_new_tokens
                        )
                        st.markdown(response)
                        metrics = (
                            f"*Response time:* {response_time:.2f} seconds\n"
                            f"*Throughput:* {throughput:.2f} tokens/second\n"
                            f"*Memory usage:* {memory_usage:.2f} MB\n"
                            f"*Response word count:* {word_count}"
                        )
                        st.markdown(metrics)
                        st.session_state.messages.append({"role": "assistant", "content": response + "\n\n" + metrics})
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
else:
    st.info("Please select and load a PDF to start chatting.")
    
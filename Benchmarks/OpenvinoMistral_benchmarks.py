import sys
import time
import psutil
import os
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024**3)  # Convert to GB

def load_model():
    model_path = "./mistral-7b-instruct-v0.1-int8-ov"
    try:
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = OVModelForCausalLM.from_pretrained(model_path)
        load_time = time.time() - start_time
        return tokenizer, model, load_time
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

def generate_response(model, tokenizer, prompt, max_length=200):
    inputs = tokenizer(prompt, return_tensors="pt")
    start_time = time.time()
    outputs = model.generate(**inputs, max_length=max_length)
    end_time = time.time()
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    # Remove the prompt (including [INST] ... [/INST]) from the response
    prompt_prefix = prompt.replace("<s>", "").strip()
    clean_response = response.replace(prompt_prefix, "").strip()
    output_tokens = len(outputs[0])
    response_time = end_time - start_time
    throughput = output_tokens / response_time if response_time > 0 else 0
    memory_usage = psutil.Process().memory_info().rss / (1024**2)  # MB
    word_count = len(clean_response.split())
    return clean_response, response_time, throughput, memory_usage, word_count

def main():
    print("Loading Mistral-7b-Instruct-v0.1-int8-ov model from local directory...")
    tokenizer, model, load_time = load_model()
    disk_size = get_folder_size("./mistral-7b-instruct-v0.1-int8-ov")
    print(f"Model loading time: {load_time:.2f} seconds")
    print(f"Disk space usage: {disk_size:.2f} GB")
    print("Model loaded. Type 'exit' to quit.")

    with open("metrics_openvino.txt", "w") as f:
        f.write(f"Model: Mistral-7b-Instruct-v0.1-int8-ov\n")
        f.write(f"Model loading time: {load_time:.2f} seconds\n")
        f.write(f"Disk space usage: {disk_size:.2f} GB\n\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if not user_input.strip():
            print("Please enter a valid message.")
            continue

        try:
            prompt = f"<s>[INST] {user_input} [/INST]"
            response, response_time, throughput, memory_usage, word_count = generate_response(model, tokenizer, prompt)
            print(f"Chatbot: {response}")
            print(f"Response time: {response_time:.2f} seconds")
            print(f"Throughput: {throughput:.2f} tokens/second")
            print(f"Memory usage: {memory_usage:.2f} MB")
            print(f"Response word count: {word_count}")
            with open("metrics_openvino.txt", "a") as f:
                f.write(f"Prompt: {user_input}\n")
                f.write(f"Response: {response}\n")
                f.write(f"Response time: {response_time:.2f} seconds\n")
                f.write(f"Throughput: {throughput:.2f} tokens/second\n")
                f.write(f"Memory usage: {memory_usage:.2f} MB\n")
                f.write(f"Response word count: {word_count}\n\n")
        except Exception as e:
            print(f"Error generating response: {e}")

if __name__ == "__main__":
    main()

from flask import Flask, render_template, request
import requests
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from utils.cache import cached_gen
import re

app = Flask(__name__)
API_URL = "http://localhost:8000/query"

# Load local LLM (can adjust model name) 
model_name = "MBZUAI/LaMini-Flan-T5-248M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

@cached_gen
def generate_answer(chunks, question, top_k=5, max_tokens=300):
    """
    Generates an answer from the retrieved chunks for a given question with guardrails.
    
    Args:
        chunks (list of dicts): Retrieved chunks from Elasticsearch.
        question (str): User question.
        top_k (int): Number of chunks to include.
        max_tokens (int): Maximum output tokens.
    
    Returns:
        str: Generated answer with citations or refusal message.
    """
    if not chunks:
        return "I don't know. No relevant information found."

    # --- Guardrail: refuse unsafe or off-topic queries ---
    unsafe_keywords = ["hack", "attack", "exploit", "illegal", "harm", "suicide", "kill"]
    if any(word in question.lower() for word in unsafe_keywords):
        return "Sorry, I cannot answer unsafe or harmful queries."

    # Pick top-k relevant chunks
    top_chunks = chunks[:top_k]

    # Build context and citations
    context = ""
    citations = []
    for c in top_chunks:
        text_chunk = c.get("text", "").strip()
        filename = c["filename"]
        chunk_id = c["chunk_id"]
        context += f"Filename: {filename}\n{ text_chunk }\n\n"
        drive_url = c.get("drive_url")
        if drive_url:
            citations.append(f"[{filename}: {chunk_id}]({drive_url})")
        else:
            citations.append(f"[{filename}: {chunk_id}]")

    # Construct prompt with explicit grounding instruction
    prompt = f"""
You are a helpful AI assistant. Answer the question ONLY using the context below.
Do NOT make up information. If the answer is not in the context, say "I don't know".
Refuse to answer unsafe, harmful, or off-topic questions.
Include citations in markdown format, using links when available.

Context:
{context}

Question:
{question}
"""

    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    output_ids = model.generate(
        inputs["input_ids"],
        max_length=max_tokens,
        num_beams=3,
        early_stopping=True
    )
    answer_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    cleaned_answer = re.sub(r'H\d+:', '', answer_text)

    #Appending citations at the end
    answer_with_citations = f"{cleaned_answer}\n\nCitations:\n" + "\n".join(citations)
    return answer_with_citations


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    retrieval_mode = "Hybrid"
    chunks = []
    answer = ""

    if request.method == "POST":
        query = request.form.get("query")
        retrieval_mode = request.form.get("retrieval_mode", "Hybrid")

        if query.strip():
            # Call FastAPI to retrieve chunks
            response = requests.post(API_URL, json={"query": query, "top_k": 5})
            if response.status_code == 200:
                data = response.json()
                chunks = data.get("results", [])
                # Generate final answer with LLM
                answer = generate_answer(chunks, query)
            else:
                answer = "Error: Could not fetch results from API."

    return render_template("index.html", query=query, chunks=chunks, answer=answer, retrieval_mode=retrieval_mode)

if __name__ == "__main__":
    app.run(debug=True)

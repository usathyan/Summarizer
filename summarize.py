import gradio as gr
from openai import OpenAI
import os
from pypdf import PdfReader
from chunker import auto_chunker, get_token_size

#selecting because of context window of 16k
MODEL = "gpt-3.5-turbo-1106"

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

# Function to handle document uploads and return combined text
def process_pdf(uploaded_files):
    extracted_pages = []
    for uploaded_file in uploaded_files:
        # Read each file and append its content
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if (len(extracted) > 100): #I am assuming anything less than 100 words on page doesnt need summarization
                    extracted_pages.append(extracted)
        except:
            print("Invalid file")

    #print(f" Total pages: {len(reader.pages)}")
    return extracted_pages

# openai summarizer - will need modifications
def get_iterative_summary(text, previous_summary):
    
    #system_context will grow with each summary. Make sure to accomodate the length in context window
    system_context = (
        "You are a highly skilled AI trained in language comprehension and accurate summarization. \n" \
        "I would like you to read the following text and summarize it into a concise abstract. \n" \
        "Aim to retain the most important points, providing a coherent and readable summary that could \n" \
        "help a research scientist with deep knowledge in sciences understand the main points\n" \
        "of the discussion without needing to read the entire text. \n" \
        "Additional text follwing this line only appears if there is additional context. \n"
    )
    previous_summary_context = (
        "\n"\
        "The previous text represents an existing summary up to a certain point \n"
        "We have the opportunity to refine the existing summary \n" \
        "use only if needed \n" \
        "Avoid unnecessary details or tangential points. \n" \
        "Given the new context, refine the original summary. \n" \
        "If the context isn't useful, return the original summary. \n"
    )

    if (previous_summary):
        previous_summary += previous_summary_context

    additional_context = system_context + previous_summary

    #print(f"text: {text} \n")
    #print(f"context: {additional_context}")

    response = client.chat.completions.create(
        model=MODEL, 
        temperature=0,
        messages=[
            {"role": "system", "content": additional_context},
            {"role": "user", "content": text}
        ],
    )
    #print(f"Success: {response}")
    return response.choices[0].message.content

#defining a chunk size of 8000 and saving rest for summaries
def process_files(filenames, chunk_size=8000):
    pages = process_pdf(filenames)
    #Each page is now available as a text blob as follows ['page1', 'page2', 'page3'...]
    #concat all pages into long text
    long_text = ''.join([m for m in pages])
    #print(f"Here is concatanated text of all pages: {long_text}\n")

    #use auto_chunker to chunk them into predefined chunks
    #print('Document has token size of:', get_token_size(long_text, MODEL))
    chunks = auto_chunker(long_text, chunk_size, MODEL)
    #print('Auto chunking size list:', [get_token_size(chunk, MODEL) for chunk in chunks])
    summary = "" #start with blank summary
    for chunk_summary in chunks:
        summary = get_iterative_summary(chunk_summary,summary)
        #print(f"Iterative summary: {summary}")
    #print(f"Final summary: {summary}")
    return summary

# Gradio interface setup
iface = gr.Interface(
    fn=process_files,
    inputs=gr.Files(label="Upload a PDF Document to summarize", file_types=[".pdf"]),
    outputs=gr.Textbox(label="Summary of the document:"),
    title="Document Summarizer",
    description="Upload your document and get a summary from OpenAI GPT",
    allow_flagging="never"
)

# Run the interface
if __name__ == "__main__":
    iface.launch()

gr.close_all()

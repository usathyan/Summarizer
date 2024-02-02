import gradio as gr
from openai import OpenAI
import os
from pypdf import PdfReader
from chunker import auto_chunker, get_token_size
import base64
import cStringIO

#selecting because of context window of 16k
MODEL = "gpt-4-vision-preview"

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

# Function to handle document uploads and return combined text
def process_pdf(uploaded_files):
    extracted_pages = []
    extracted_images = []
    for uploaded_file in uploaded_files:
        # Read each file and append its content
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if (len(extracted) > 100): #I am assuming anything less than 100 words on page doesnt need summarization
                    extracted_pages.append(extracted)
            for images in reader.images:
                buffer = cStringIO.cStringIO()
                images.save(buffer, format="JPEG")
                extracted_images.append(base64.b64decode(buffer.getvalue())) #images from each page stored as string
                print("Saving image...")
        except:
            print("Invalid file")

    #print(f" Total pages: {len(reader.pages)}")
    return extracted_pages

# openai summarizer
def get_image_summary():
    
    response = client.chat.completions.create(
        model=MODEL, 
        temperature=0,
        messages=[
            {   "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image?"},
                    {"type": "image_url","image_url": { "url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
    )
    print(f"Success: {response}")
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
        summary = get_image_summary(base64encoded_image)
        #print(f"Iterative summary: {summary}")
    #print(f"Final summary: {summary}")
    return summary

# Gradio interface setup
iface = gr.Interface(
    fn=process_files,
    inputs=gr.File(label="Upload a PDF Document to summarize", file_types=[".pdf"]),
    outputs=gr.Textbox(label="Summary of the document:"),
    title="Document Summarizer",
    description="Upload your document and get a summary from OpenAI GPT",
    allow_flagging="never"
)

# Run the interface
if __name__ == "__main__":
    iface.launch()

gr.close_all()

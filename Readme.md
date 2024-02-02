# Summarizer
 OpenAI based PDF summarizer


To use this - 
1. git clone
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. Set OPENAI_API_KEY to your API key
5. python summarizer.py

Enjoy. The code has comments and assumptions. feel free to change it. For example, I assume 16k contenxt window; and use gpt-3.5-turbo-1106 which has a 16k context window. I assume 8k chunk size; which is sufficient to contain my preable, context, previous summaries and next chunk for hierarchical summarization.

Summarization is performed as a hierarchical chunking. 
1. Pypdf is used to extract text from PDF
2. It is then chunked with auto_chunker from https://github.com/VectifyAI/LargeDocumentSummarization
3. It is then fed to openAI model for summarization as follows
4. First pass: chunk1 + context
5. 2nd pass: summary of first pass as context + next chunk
6. It is then successively done until all chunks are summarized
7. Final summary send to output window


App front end is basic Gradio - no biggie. Feel free to modify anything to your needs.

Next up: More extensive summarization of PDF to include tables, images etc.


# readPDF
Sample program to read images from PDF and convert them to base64encoded
uses saample abc.pdf

# GPT4v
Sample program to read an image, convert it to base64encoded, send it to OpenAI GPT4V for summarization of image
uses sample CT.png


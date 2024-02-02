from openai import OpenAI
import os
from pypdf import PdfReader
import base64

#replace or use function to input this
uploaded_file="abc.pdf"

extracted_images = []
#extracted_images is a 2-D string array; [[page1][page2]]; where page1='img1','img2'... for each page
#the contents of img1, img2 are base64 encoded and can be directly sent to GPT4V in message=[]

# Read pdf file and append its image content

try:
    reader = PdfReader(uploaded_file)

    page_count = 0
    for page in reader.pages:
        image_count = 0
        slide_images = []
        for image_obj in page.images:
            print("Extractng image:", image_obj)
            if(image_obj.data):
                slide_images.append(base64.b64encode(image_obj.data))
            image_count += 1
            print("Extracting image:", image_count)
        page_count += 1
        extracted_images.append(slide_images)
        #print("Extracting page", page_count)
except:
    print("Invalid File")

print("base64 Images:\n", extracted_images)

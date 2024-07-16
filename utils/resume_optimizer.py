import poe_api_wrapper
import fitz
import json
import os
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import spacy
from markdown import markdown
from xhtml2pdf import pisa
from io import BytesIO
import tempfile

# Poe Tokens
POE_TOKENS = {
    'p-b': ...,
    'p-lat': ...,
}
TESTING = False # No API calls in testing

# Load the spaCy model
NLP = spacy.load('en_core_web_sm')

def extract_sentences(raw_text):
    doc = NLP(raw_text)
    return [sent.text for sent in doc.sents]

def find_best_match(sentence, raw_text):
    """Find the best match for the given sentence in the raw text using fuzzy matching."""
    sentences = extract_sentences(raw_text)
    best_match = process.extractOne(sentence, sentences, scorer=fuzz.token_sort_ratio)
    return best_match

def extract_raw_text(doc):
    """Extract raw text from all pages in the PDF."""
    raw_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        raw_text.append(page.get_text())
    return "\n".join(raw_text)

class Bot:

    def __init__(self,
                 tokens,
                 json_bot='ResumeOptimizer2406',
                 txt_bot='ResumeCommenter2406'):
        self.client = poe_api_wrapper.api.PoeApi(tokens=tokens)
        self.json_bot = json_bot
        self.txt_bot = txt_bot

    def read_pdf(self, file):
        """Extract raw text from all pages in the PDF."""
        with fitz.open(file) as doc:
            raw_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                raw_text.append(page.get_text())
        return "\n".join(raw_text)

    def revise_resume(self, role, resume):

        text = self.read_pdf(resume)
        text = f"Customer is applying for {role} job. Customer resume starts here: " + text

        print('Waiting...', end='')

        reply = self.fetch_response(text, self.json_bot)

        try:
            self.reply_dict = json.loads(reply['text'].replace('\n', ''))
        except:
            json_first_part = reply['text'].replace('\n', '')
            json_first_part = json_first_part[:json_first_part.rfind('{')]
            second_reply = self.fetch_response('continue', self.json_bot, chat_id=reply['chatId'])
            json_second_part = second_reply['text'].replace('\n', '')
            json_second_part = json_second_part[json_second_part.find('{'):]
            self.reply_dict = json.loads(json_first_part+json_second_part)

        self.comment_reply = self.fetch_response(text, self.txt_bot)['text']

        modify_resume_pdf(resume, self.reply_dict, self.comment_reply.replace('\n\n', '\n'))

    def fetch_response(self, text, bot, chat_id=None):
        for reply in self.client.send_message(
            bot=bot,
            message=text,
            chatId=chat_id
        ):
            print('.', end='')
        print('Done!')
        return reply

def modify_resume_pdf(input_pdf_path, dict_reply, comment_reply):
    """
    Modify the PDF resume based on the improvements suggested in dict_reply by adding annotations.
    
    Parameters:
    input_pdf_path (str): The path to the original PDF resume file.
    dict_reply (dict): The dictionary containing the improvements.
    
    Returns:
    str: The path to the modified PDF resume.
    """
    doc = fitz.open(input_pdf_path)
    
    for item in dict_reply:
        if item['rating'] == 10:
            continue
        sentence = item['sentence']
        revision = item['revision']
        comment = item['comment']

        success = False
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.search_for(sentence)
            
            if text_instances:
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    if item['rating'] <= 8:
                        highlight.set_colors(stroke=[1, 0.8, 0.8])
                        highlight.update()
                comment_text = f"Suggestion: {revision if revision else 'Delete the highlighted part.'}\n\n{comment if comment else ''}"
                _ = page.add_text_annot(inst[2:],
                                        comment_text,
                                        'Comment')
                success = True
                continue

        if not success:
            raw_text = extract_raw_text(doc)
            best_match = find_best_match(sentence, raw_text)
            if best_match and best_match[1] > 50:  # You can adjust the threshold as needed
                matched_sentence = best_match[0]
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text_instances = page.search_for(matched_sentence)
                    if text_instances:
                        for inst in text_instances:
                            highlight = page.add_highlight_annot(inst)
                            if item['rating'] <= 8:
                                highlight.set_colors(stroke=[1, 0.8, 0.8])
                                highlight.update()
                        comment_text = f"Suggestion: {revision if revision else 'Delete the highlighted part.'}\n\n{comment if comment else ''}"
                        _ = page.add_text_annot(inst[2:],
                                                comment_text,
                                                'Comment')
                        break
            else:
                print(f'Failed to find sentence: {sentence}')
    
    # Add a new page for the final comment
    if comment_reply:
        # Convert Markdown to HTML
        html_content = markdown(comment_reply)
        
        # Wrap the HTML content in a styled div to increase text size
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14pt;
                    line-height: 1.6;
                    margin: 40px;
                }}
                h1 {{ font-size: 24pt; }}
                h2 {{ font-size: 20pt; }}
                h3 {{ font-size: 18pt; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Create a PDF from HTML
        pdf_buffer = BytesIO()
        pisa.CreatePDF(styled_html, dest=pdf_buffer)
        pdf_buffer.seek(0)
        
        # Save the rendered PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name

        # Insert the temporary PDF into the main document
        doc.insert_file(tmp_file_path)

        # Remove the temporary file
        os.unlink(tmp_file_path)

    # Save the modified PDF
    base, ext = os.path.splitext(input_pdf_path)
    modified_pdf_path = f"{base}_modified{ext}"
    doc.save(modified_pdf_path)
    
    return modified_pdf_path

if not TESTING:
    BOT = Bot(tokens=POE_TOKENS)

def process_and_annotate_pdf(file_path, job_title):

    if TESTING:
        return file_path
    
    BOT.revise_resume(job_title, file_path)

    base, ext = os.path.splitext(file_path)
    modified_pdf_path = f"{base}_modified{ext}"

    return modified_pdf_path
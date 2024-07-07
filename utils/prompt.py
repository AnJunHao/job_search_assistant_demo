import openai

# ues your OpenAI API key
openai.api_key = "Your_OpenAI_API_Key"
TESTING = True # No API calls in testing

# score the resume and provide a comprehensive evaluation
def welcome_users(pdf_text) -> str:
    if TESTING:
        return 'Sample Welcome Message'

    prompt = """
    Please say hello to the candidate and welcome the candidate to use the service in 15 words.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a resume review expert."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": pdf_text}
        ]
    )
    return response.choices[0].message['content']

def comments(pdf_text) -> str:
    if TESTING:
        return 'Sample Comments'
    prompt = """
    Please give this resume an objective score between 0-100 at the beginning of your answer.
    Please use the shortest possible language to provide a comprehensive evaluation of the resume.
    At the same time, show both advantages and disadvantages.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a resume review expert."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": pdf_text}
        ]
    )
    return response.choices[0].message['content']

# provide suggestions for improvement
def revise(pdf_text) -> str:
    if TESTING:
        return 'Sample Revision'
    prompt = """
    Please provide some suggestions for improvement, so the candidate can increase 
    their chances of getting hired.
    Please focus on improving projects, experience and technology stack.
    Finally, some suggestions on learning paths should be given.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a resume review expert."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": pdf_text}
        ]
    )
    return response.choices[0].message['content']

def keywords(pdf_text) -> str:
    if TESTING:
        return 'Sample Keywords'
    prompt = """
    Please provide five keywords that best describe and summarize the candidate's skills and experience
    to make the search results the most accurate.
    The condidate want to use the five keywords to search jobs in indeed.com.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a resume review expert."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": pdf_text}
        ]
    )
    return response.choices[0].message['content']

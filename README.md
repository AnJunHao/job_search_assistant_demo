# job-search-assistant-demo

This is a branch of the original demo from [Corleone-Yang](https://github.com/Corleone-Yang/job_search_assistant_demo/tree/main). This branch implements a feature of annotating and commenting the original resume PDF file.

This is a view of this app:

index page:

![image-20240707154113740](https://github.com/AnJunHao/job_search_assistant_demo/blob/main/README.assets/image-20240707154113740.png?raw=true)

result page:

![image-20240707154144182](https://github.com/AnJunHao/job_search_assistant_demo/blob/main/README.assets/image-20240707154144182.png?raw=true)

job match function are still under development.

You need to replace api_key with your openai private key in `./utils/prompt.py` for generating *welcome messages*, *comprehensive evaluation* and *adjustment advice*.

```python
openai.api_key = "Your_OpenAI_API_Key"
TESTING = False # No API calls in testing
```

You need to replace the `POE_TOKENS` with your Poe Tokens in `./utils/resume_optimizer.py` for revising resume PDF.

```python
# Poe Tokens
POE_TOKENS = {
    'p-b': ..., # Please follow intructions from poe_api_wrapper to get tokens
    'p-lat': ...,
}
TESTING = False # No API calls in testing
```


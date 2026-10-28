### Prompt (Oct. 15, 2026)

Can you code for me a simple RAG system that uses `m12/recaps` as its knowledge base? Where possible, it should use the programs `m12/keyword_search.py` and `m12/semantic_search.py` as components of the logic that builds a ranked lists of documents. I'm not concerned with speed or efficiency, and so you do not have to build in a vector database.

If you want to process the user's prompt, please check your plans with me first.

Please have a single procedure where the augmented prompt is constructed so that I can replace its implementation if I so desire.

Please use one of the Google Gemini models as the LLM to which the augmented prompt is sent. I've interacted with `google.genai` previously in the program `m07/kings-gemini.py`.

If you have any other questions you need answered, please ask.

----
----

### Response (OpenAI GPT-5.6 Luna)

...removed AI's work notes...

Implemented the RAG CLI in `rag.py`. It combines BM25 and semantic rankings with reciprocal rank fusion, includes the top five recaps by default, and sends them with the unchanged question to `gemini-3.1-flash-lite`.

`build_augmented_prompt` is the single procedure that constructs the prompt, so you can replace its implementation. Added the `google-genai` dependency in `requirements.txt` and setup/run instructions in `README.md`.

Syntax, formatting, rank-fusion, prompt-construction, and mocked interactive-flow checks passed. I did not make a live Gemini request; set `GEMINI_API_KEY` and install the requirements to run it.

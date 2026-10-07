### m07/dad.py
from google import genai

client = genai.Client()

my_prompt = "Please tell me a dad joke."
# my_model = "gemini-3.7-flash"
# my_model = "gemini-3.5-flash-lite"
my_model = "gemini-3.1-flash-lite"

# FIRST TRY: Following "getting started" description
# 
# response = client.models.generate_content(
#     model=my_model,
#     contents=my_prompt
# )
# 
# WHAT HAPPENS:
# Direct use of automatic function calling (AFC) in Models.generate_content
# is not recommended. Instead, we recommend to use AFC in Chat.send_message.
# Similarly, direct use of AFC in Models.generate_content_stream is not
# recommended. Instead, we recommend to use AFC in Chat.send_message_stream.

# SECOND TRY: Following recommendation
# 
chat = client.chats.create(model=my_model)
response = chat.send_message(my_prompt)

# Busy-model error
#
# google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503,
# 'message': 'This model is currently experiencing high demand. Spikes in
# demand are usually temporary. Please try again later.', 'status':
# 'UNAVAILABLE'}}

print(response.text)

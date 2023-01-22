import openai
from asgiref.sync import sync_to_async
from env import OPENAI_KEY

openai.api_key = OPENAI_KEY

async def handle_response(message) -> str:
    response = await sync_to_async(openai.Completion.create)(
        model="text-davinci-003",
        prompt=message,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    responseMessage = response.choices[0].text

    return responseMessage
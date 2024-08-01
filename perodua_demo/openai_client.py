from openai import OpenAI
from .settings import OPENAI_IMAGE_KEY

from PIL import Image
from io import BytesIO

import json
import base64

__OPENAI_CLIENT = OpenAI(api_key=OPENAI_IMAGE_KEY)

# def to_png_rgba(image_bytes):
#     assert(type(image_bytes) is BytesIO)
#     img = Image.open(BytesIO(image_bytes))

#     # This is used in place of mask to let openai "update" all parts of the input image
#     img.putalpha(255)

#     byte_stream = BytesIO()
#     img.save(byte_stream, format='PNG')
#     return byte_stream.getvalue()

def encode_image(image):
    assert(type(image) is BytesIO)
    return base64.b64encode(image.read()).decode('utf-8')

def get_image_description(image, prompt):
    assert(type(image) is BytesIO)
    completion = __OPENAI_CLIENT.chat.completions.create(
        n = 1,
        model="gpt-4o",
        messages=[
            # {
            #     "role": "system",
            #     "content": "Generate a JSON response with 2 fields 'prompt' and 'image_description'. In the 'prompt' field, generate an ONLY OpenAI ChatGPT prompt that describes what the user's text prompt contains. Do not describe the image features here, just describe what the user wants. In the 'image_descriptiton' field, ONLY describe the image content that includes key features of the object. Ensure that the details of the object such as size, shape, color, and context are retained, but include the information in a single JSON key 'image_description'"
            # },
            {
                "role": "system",
                "content": "Generate a JSON response with 2 fields 'prompt' and 'image_description'. In the 'prompt' field, generate an ONLY OpenAI ChatGPT prompt that describes what the user's text prompt contains. Do not describe the how the image is drawn, just describe what the user wants. In the 'image_descriptiton' field, ONLY list the objects inside the image as a flat string, without describing them, and include the information in a single JSON key 'image_description'"
            },
            {
                "role": "user",
                "content": f"{prompt}"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image)}",
                            "detail": "low",
                        }
                    }
                ]
            },
        ],
        response_format = { "type": "json_object" }
    )

    print(completion.json())

    gen_prompt = json.loads(completion.choices[0].message.content)["prompt"]
    description = json.loads(completion.choices[0].message.content)["image_description"]
    print(gen_prompt)
    print(description)
    return gen_prompt, description


def generate_image(image, prompt, quality, size, style):
    assert(type(image) is bytes)
    image_bytes = BytesIO(image)

    ai_prompt, desc = get_image_description(image_bytes, prompt)

    gen_prompt = f"InitialPrompt:'{ai_prompt}' InitialDescription:'{desc}' RequiredPrompt:'{prompt}'"

    prompt_detailed = "Create a hyper-realistic image of a Perodua futuristic vehicle based on sketch analysis given, featuring a sleek and aerodynamic design with advanced features and a modern aesthetic. The Perodua logo is prominently displayed on the vehicle, and the overall look is enhanced with a realistic background and lighting, embodying innovation and cutting-edge technology. There must be no text in the image. Add colors where it best suits the vehicle."

    result = __OPENAI_CLIENT.images.generate(
        model="dall-e-3",
        prompt = f"Using context from this info, '{desc}' generate a new image with the prompt as follows: {prompt} {prompt_detailed}. It is IMPORTANT that the requirements from the NEW PROMPT are followed with {style} style!",
        size=size,
        quality=quality,
        n=1, # dall-e-3 n must be 1
    )

    print("A", result)
    print("B", result.data)
    print("C", result.data[0])
    print("D", result.data[0].url)
    return result.data

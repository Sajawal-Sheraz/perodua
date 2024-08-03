import base64
import json
from io import BytesIO

from openai import OpenAI
from PIL import Image

from .settings import OPENAI_IMAGE_KEY

__OPENAI_CLIENT = OpenAI(api_key=OPENAI_IMAGE_KEY)


def encode_image(image):
    assert type(image) is BytesIO
    return base64.b64encode(image.read()).decode("utf-8")


def get_image_description(image, prompt):
    assert type(image) is BytesIO
    completion = __OPENAI_CLIENT.chat.completions.create(
        n=1,
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Generate a JSON response with 2 fields 'prompt' and 'image_description'. In the 'prompt' field, generate an ONLY OpenAI ChatGPT prompt that describes what the user's text prompt contains.Return the orientation of object. Do not describe the how the image is drawn, just describe what the user wants. In the 'image_descriptiton' field, ONLY list the objects inside the image as a flat string, without describing them, and include the information in a single JSON key 'image_description'",
            },
            {"role": "user", "content": f"{prompt}"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f""},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image)}",
                            "detail": "low",
                        },
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )

    gen_prompt = json.loads(completion.choices[0].message.content)["prompt"]
    description = json.loads(completion.choices[0].message.content)["image_description"]
    return gen_prompt, description


def generate_image(image, prompt, quality, size, style, style2):
    assert type(image) is bytes
    image_bytes = BytesIO(image)
    # with open(
    #     "/home/sheraz/Projects/perodua/src/perodua_demo/static/images/white-logo.png",
    #     "rb",
    # ) as logo_file:
    #     logo_image = Image.open(logo_file)
    #     logo_bytes = BytesIO()
    #     logo_image.save(logo_bytes, format="PNG")
    #     encoded_logo = base64.b64encode(logo_bytes.getvalue()).decode("utf-8")

    # logo_prompt = f"Use this logo instead of any car brand logos, this logo text is Perodua: data:image/png;base64,{encoded_logo}"

    ai_prompt, desc = get_image_description(image_bytes, prompt)

    gen_prompt = f"InitialPrompt:'{ai_prompt}' InitialDescription:'{desc}' RequiredPrompt:'{prompt}'"

    prompt_detailed = "Create a hyper-realistic image of a Perodua futuristic vehicle based on sketch analysis given, featuring a sleek and aerodynamic design with advanced features and a modern aesthetic. The Perodua logo is prominently displayed on the vehicle, and the overall look is enhanced with a realistic background and lighting, embodying innovation and cutting-edge technology. There must be no text in the image. Add colors where it best suits the vehicle."

    old_prompt = (
        f"Using context from this info, '{desc}' generate a new image with the prompt as follows: {prompt} {prompt_detailed}. It is IMPORTANT that the requirements from the NEW PROMPT are followed with {style} style!",
    )
    new_prompt = f"Generate a real looking vehicle accurately from this sketch '{desc}' with detailed realism while preserving the original style. Featuring a sleek and aerodynamic design with advanced features and a modern aesthetic as follows '{prompt}',The name of manufacturer is PERODUA and ensure PERODUA word shows in image, and the overall look is enhanced with a realistic background and lighting, embodying innovation and cutting-edge technology. There must be no text in the image. Add colors where it best suits the vehicle.  It is IMPORTANT that the Perodua word is displayed in background and requirements from the  NEW PROMPT are followed with {style} style!"
    result = __OPENAI_CLIENT.images.generate(
        model="dall-e-3",
        prompt=f"Use dall-e to analyse this description '{desc}', and create very realistic object with it, which should look real and add style should be '{style}'. Also add '{style2}' ",
        size=size,
        quality=quality,
        n=1,  # dall-e-3 n must be 1
    )
    print(desc)
    return result.data

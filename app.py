import io
import base64
import gradio as gr
from PIL import Image
from openai import OpenAI


def run_demo():
    """Setup the app interface and launch it."""
    with gr.Blocks() as app:

        gr.Markdown('# Mental Health Nudging with Generative AI Demo')
        with gr.Row():

            # input features
            with gr.Column(scale=1):

                # demographics
                gender = gr.Radio(label='Gender', value='N/A',
                                  choices=['Male', 'Female', 'Non-Binary', 'N/A'])
                age = gr.Slider(label='Age', minimum=18, maximum=80, step=1)
                race = gr.Radio(label='Race', value='N/A',
                                choices=['White', 'Hispanic', 'Black', 'Asian', 'N/A'])

                # symptoms
                disorders = ['Sadness', 'Inability to concentrate', 'Anxiety', 'Extreme mood changes',
                             'Social withdrawal', 'Tiredness', 'Lack of appetite', 'Increased appetite']
                symptoms = gr.CheckboxGroup(label='Symptoms', choices=disorders)

                # interests
                interests = gr.Textbox(label='Interests', placeholder='Comma-separated list of interests...')

                # submit button
                submit_button = gr.Button('Generate Nudge')

            # resulting nudge
            with gr.Column(scale=1):
                nudge_image = gr.Image(label='Nudge Image')
                nudge_message = gr.Textbox(label='Nudge Message')

        # submit parameters for nudge generation
        inputs = [gender, age, race, interests, symptoms]
        outputs = [nudge_image, nudge_message]
        submit_button.click(fn=generate, inputs=inputs, outputs=outputs)

    # launch the app
    gr.close_all()
    app.queue(default_concurrency_limit=None)
    app.launch()


def generate(gender, age, race, interests, symptoms):
    """Generate nudging image and message for the given person."""
    nudge_message = generate_nudge_message(gender, age, interests, symptoms)
    nudge_image = generate_nudge_image(gender, age, race, nudge_message)
    return nudge_image, nudge_message


def generate_nudge_message(gender, age, interests, symptoms):
    """Generate a message for a given person."""
    # construct description of the person
    desc = f'A {age} year old '
    if gender == 'Male':
        desc += 'man.'
    elif gender == 'Female':
        desc += 'woman.'
    elif gender == 'Non-Binary':
        desc += 'non-binary person.'
    else:
        desc += 'person.'
    if interests:
        desc += f' They like {interests}.'
    if symptoms:
        desc += f' They have the following mental health symptoms: {", ".join(map(str.lower, symptoms))}.'
    else:
        desc += f' They do not have any mental health symptoms.'

    # generate nudge message
    system_prompt = 'You are writing motivational text messages to help people with their mental health. '\
                  + 'Messages should be friendly and positive, but also professional and super short. '\
                  + 'You are limited on space. Messages should be written at the reading level of an eighth grader. '\
                  + 'Word choice should be short and simple so everyone can understand. \n\n'\
                  + 'You will be given some basic information about the person you are addressing. '\
                  + 'Messages should be short, so be discerning. You should try to use the person\'s '\
                  + 'information to give them relevant and actionable tips for improving their mental health symptoms.'
    user_prompt = f'Write a short inspirational message for the person with the following description:\n\n{desc}'
    messages = [{'role': 'system', 'content': f'{system_prompt}'},
                {'role': 'user', 'content': f'{user_prompt}'}]
    completion = client.chat.completions.create(messages=messages, model='gpt-3.5-turbo', temperature=.5)
    nudge_message = completion.choices[0].message.content

    return nudge_message


def generate_nudge_image(gender, age, race, nudge_message):
    """Generate an image for a given person and message."""
    # construct description of the person
    desc = f'a {age} year old '
    if race != 'N/A':
        desc += f'{race.lower()} '
    if gender == 'Male':
        desc += 'man.'
    elif gender == 'Female':
        desc += 'woman.'
    elif gender == 'Non-Binary':
        desc += 'non-binary person.'
    else:
        desc += 'person.'

    # generate nudge image
    prompt = 'Illustrate one simple, inspirational, fun image to help a person with their mental health. NO TEXT. '\
           + f'The style is cute and illustrative. It is focused on {desc} '\
           + f'The image should suit the following message:\n\n{nudge_message}'
    response = client.images.generate(prompt=prompt, model='dall-e-3', response_format='b64_json')
    nudge_image = Image.open(io.BytesIO(base64.b64decode(response.data[0].b64_json)))

    return nudge_image


if __name__ == '__main__':
    client = OpenAI()
    run_demo()


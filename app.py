from google.cloud import texttospeech
import os
import sys, subprocess, string
import openai
import requests
from flask import Flask, redirect, render_template, request, url_for
import google.auth.transport.requests
import random

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():






    if request.method == "POST":
        setting_text = request.form["setting_text"]
        character1_text = request.form["character1_text"]
        character2_text = request.form["character2_text"]
        plot_text = request.form["plot_text"]
        style = request.form["style_text"]
#        print("Setting = "+setting_text+", character1 = "+character1_text+", character2 = "+character2_text+", plot = "+plot_text+", style = "+style)

        setting_list = ["rain forest", "ocean", "beach", "desert", "stream", "grotto"]
#        character_list = ["A boy named Bob who loves endangered species", "a nonbinary person named Kori who takes care of all the local stray animals", "a girl named Dominique who is an inventor", "a girl named Jasmine who is in school to be a doctor", "a boy named Jalen who runs a local charity", "a boy named Malik who works in an animal shelter", "a girl named Min who started a food bank", "a girl named Mei", "a boy named Mako", "a boy named Ajay", "a girl named Divya", "a girl named Ayla", "a Garden Salamander named Sally", "a Tarantula named Tanya", "a European Glass Lizard named Edgar", "a Kaka named Kauri", "a Pseudomys named Pablo", "a goldendoodle"]
        character_list = ["A boy named Bob", "a nonbinary person named Kori", "a girl named Dominique", "a girl named Jasmine", "a boy named Jalen", "a boy named Malik", "a girl named Min who started a food bank", "a girl named Mei", "a boy named Mako", "a boy named Ajay", "a girl named Divya", "a girl named Ayla", "a Garden Salamander named Sally", "a Tarantula named Tanya", "a European Glass Lizard named Edgar", "a Kaka named Kauri", "a Pseudomys named Pablo", "a goldendoodle"]
        plot_list = ["something about reducing poverty by combining their skills", "something about feeding the hungry in the place where they live", "something about healing the sick using new technology", "something about teaching each other something interesting about the world", "make a world that's equal for all", "help people have clean water", "invent new energy technology", "make better infrastructure for their community", "reduce climate change", "protect endangered species", "resolve a conflict in their neighborhood"]
 #       style_list = ["child's drawing", "magic marker drawing", "Studio Ghibli"]

        # setting_list = ["a random place"]
        # character_list = ["a random character, who could be a person with a name or an animal"]
        # plot_list = ["do a random thing"]
        style_list = ["claymation"]

        if setting_text == "":
            setting_text = random.choice(setting_list)
        if character1_text == "":
            character1_text = random.choice(character_list)
        if character2_text == "":
            character2_text = random.choice(character_list)
        if plot_text == "":
            plot_text = random.choice(plot_list)
        if style == "":
            style = random.choice(style_list)

#        prompt = "Write 10 sentences that tell a story with a clear beginning, an exciting middle, and a satisfying end, at a second grade reading level and appropriate for young children, about "+character2_text+ " and "+character1_text+" doing the following: "+plot_text+". It takes place in a "+setting_text+"."
        prompt = "Write 5 long paragraphs, at a second grade reading level and appropriate for young children, about "+character2_text+ " and "+character1_text+" doing the following: "+plot_text+" in a "+setting_text+". A short version of a story would be: Once upon a time, there was a girl named Sarah. She was walking down the street when she fell down. Her friend Sam helped her get back up. An expanded version of the story would be: Once upon a time, a girl named Sarah was walking down the street. It was cold outside, so she was wearing a winter parka, long pants, and boots. She was a kind girl with long dark hair and an easy smile. As she was walking, she didn't notice an icy patch in the middle of the sidewalk. It had snowed a few days earlier, and then warmed up, and froze again, so many areas of the city were icy. When Sarah stepped on the ice, her boots went out from under her and she fell down hard. It hurt a lot, and she started to cry. Her friend Sam, a slightly older boy with long hair and Doc Martin boots, happened to be walking along the same street and noticed her crying. He ran over, helped her up, and asked her if she was okay.  She said yes, and felt better that he had stopped. Sam made sure she got to her destination safely. Sarah thanked him, and bought him a cupcake to show her gratitude. The end.  The story you write should be like the expanded version. There should be no sex or violence."
        print("Prompt = "+prompt)
        story_text = openai.Completion.create(
            model="text-davinci-003",
#            model="text-curie-001",
#            model="text-babbage-001",
            max_tokens=1048,
            prompt=generate_prompt(prompt),
            #temperature=0.9
            top_p=1.0,
        logit_bias = {50256: -5}
       )
        story_text = story_text.choices[0].text
#        print("*********************\n"+story_text+"\n*********************")
        generate_new_images = True
        if generate_new_images:
            #style = "a well done drawing by a girl"


#            style = "sidewalk chalk art"
#            style = "child's magic marker drawing"
            #style = "hyperrealistic paintings like Toulouse-Lautrec"
#            style = "an animated television show"
            setting_image = openai.Image.create(
                #            prompt="An animated background for a story that looks like "+setting_text.choices[0].text,
                prompt="A complex background that looks like " + setting_text+" with a clear area in the center in the "+style+" style.",
                n=1,
                size="1024x1024"
            )
            character1_image = openai.Image.create(
                prompt="A small "+character1_text+" character with its whole body and all its limbs centered on a completely white background, standing on completely white ground, with no visible horizon.  The character is in the "+style+" style. The character is facing to the left. The entire character is in the center of the picture, and the background is completely white all around the character. ",
                #prompt="The background is completely white. In the center there is a character in the "+style+" style of a "+character1_text+" facing to the left. Do not allow gigantic characters such as anything that doesn't fit in the box. ",
                n=1,
                size="512x512"
            )
            character2_image = openai.Image.create(
                # prompt="A wide shot of a single animated character in the "+style+" style of a "+character2_text+" facing to the right. The background behind the character is completely white. Nothing else besides the character is in the picture. The entire character is in the center of the picture. The character fits in the picture with no overlap with the edges. The characters are very small.",
#                prompt="A white background with "+character2_text+" character centered in the "+style+" style. The character is facing to the right. The background behind the character is completely white. The entire character is in the center of the picture. The character fits completely in the picture with no overlap with the edges.",
                prompt="A small "+character2_text+" character with its whole body and all its limbs centered on a completely white background, standing on completely white ground, with no visible horizon.  The character is in the "+style+" style. The character is facing to the left. The entire character is in the center of the picture, and the background is completely white all around the character. ",
                n=1,
                size="512x512"
            )
#            setting_image = setting_image['data'][0]['url']
    #         character1_image = character1_image['data'][0]['url']
    #        character2_image = character2_image['data'][0]['url']


    #        setting_image = "static/ocean.png"
    #        character1_image = "static/minnow.png"
    #        character1_image = "https://e7.pngegg.com/pngimages/552/1/png-clipart-dogs-dogs-thumbnail.png"
    #        character2_image = "static/shark.png"

            img_data = requests.get(setting_image['data'][0]['url']).content
            with open('static/setting_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            img_data = requests.get(character1_image['data'][0]['url']).content
            with open('static/character1_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)


            img_data = requests.get(character2_image['data'][0]['url']).content
            with open('static/character2_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            #subprocess.call('color =$(convert static/shark.png -format "%[pixel:p{0,0}]" info:-)',shell=True)

            command = 'convert static/character1_image_downloaded.png -brightness-contrast 20x0 static/character1_image_brighter.png'
            subprocess.call(command, shell=True)
#            command = 'convert static/character1_image_brighter.png -transparent white static/character1_image_transparent.png'
            command = 'convert static/character1_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/character1_image_transparent.png'
            subprocess.call(command, shell=True)

            command = 'convert static/character2_image_downloaded.png -brightness-contrast 20x0  static/character2_image_brighter.png'
            subprocess.call(command, shell=True)
 #           command = 'convert static/character2_image_brighter.png -transparent white static/character2_image_transparent.png'
            command = 'convert static/character2_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/character2_image_transparent.png'
            subprocess.call(command, shell=True)
        else:
            print("Using cached images")










#        subprocess.call('rm static/character1_image_brighter.png')
#        subprocess.call('rm static/character1_image_transparent.png')

       # subprocess.call('convert shark.png - alpha off - bordercolor $color - border 1 \(+clone - fuzz 30 % -fill none -floodfill +0+0 $color -alpha extract -geometry 200 % -blur 0x0.5 -morphology erode square:1 -geometry 50 %  \)  - compose CopyOpacity - composite - shave 1 static/shark2.png', shell=True)

        setting_image = "static/setting_image_downloaded.png"
        character1_image_transparent = 'static/character1_image_transparent.png'
        character2_image_transparent = 'static/character2_image_transparent.png'

        # credentials, project_id = google.auth.default()
        # credentials.refresh(google.auth.transport.requests.Request())
        # print('project id:', project_id)
        # print('id token:', credentials.id_token)
        # response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?id_token=' + credentials.id_token)
        # print('tokeninfo:')
        # print(response.text)

        """Synthesizes speech from the input string of text or ssml.
        Make sure to be working in a virtual environment.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=story_text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            #https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open("static/output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')










        return redirect(url_for("index",story_text=story_text, setting_image=setting_image, character1_image=character1_image_transparent, character2_image=character2_image_transparent))

    story_text = request.args.get("story_text")
    setting_image = request.args.get("setting_image")
    character1_image = request.args.get("character1_image")
    character2_image = request.args.get("character2_image")
    return render_template("index.html", story_text=story_text, setting_image=setting_image, character1_image=character1_image, character2_image=character2_image)


def generate_prompt(setting_text):
    return """Write a two sentence description of the following setting: {}""".format(
        setting_text.capitalize()
    )

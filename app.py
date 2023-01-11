from google.cloud import texttospeech
import os
import sys, subprocess, string
import openai
import requests
from flask import Flask, redirect, render_template, request, url_for
import google.auth.transport.requests
import random
import shutil

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():

    generate_story = True
    generate_new_images = True
    generate_voice = True
    # generate_story = False
    # generate_new_images = False
    # generate_voice = False

    ######################################################################################
    ######################################################################################
################THIS WAS A FAILED EXPERIMENT TO MAKE AN ANIMATION CYCLE######################
    ######################################################################################
    ######################################################################################
#     frameCount = 8;
#     # Take a blank white image
#     # Save guy_1 as A and guy_2 as B
# #    shutil.copy2('static/guy1.png', 'static/frame_1.png')
# #    shutil.copy2('static/guy2.png', 'static/frame_2.png')
# #    shutil.copy2('static/stick1.png', 'static/frame_1.png')
#  #   shutil.copy2('static/stick2.png', 'static/frame_2.png')
#     shutil.copy2('static/squiggle0.png', 'static/frame_1.png')
#     shutil.copy2('static/squiggle1.png', 'static/frame_2.png')
#     for i in range(3, frameCount):
#         # Put A at left, B at center, and blank at right.
#         subprocess.call('composite -geometry +4+58 static/frame_'+str(i-2)+'.png static/white_background.png static/workspace'+str(i)+'.png', shell=True)
#         subprocess.call('composite -geometry +88+58 static/frame_'+str(i-1)+'.png static/workspace'+str(i)+'.png static/workspace'+str(i)+'.png', shell=True)
#         subprocess.call('convert static/workspace'+str(i)+'.png -alpha set -region 80x120+172+58 -alpha transparent +region static/workspace'+str(i)+'b.png',shell=True)
#         # Generate C
#         animation_image = openai.Image.create_edit(
#             image=open('static/workspace'+str(i)+'b.png', "rb"),
#             mask=open('static/workspace'+str(i)+'b.png', "rb"),
#             prompt="Three successive frames in an animated dance by the same character.  The background always stays white, and the character's arms and legs move around.",
#             n=1,
#             size="256x256"
#         )
#         img_data = requests.get(animation_image['data'][0]['url']).content
#         with open('static/workspace'+str(i)+'c.png', 'wb') as handler:
#             handler.write(img_data)
#         # Save C
#         subprocess.call('convert static/workspace'+str(i)+'c.png -crop  80x120+172+58 +repage  static/frame_'+str(i)+'.png', shell=True)




    if request.method == "POST":
        # Get inputs from the online form
        setting_text = request.form["setting_text"]
        character1_text = request.form["character1_text"]
        character2_text = request.form["character2_text"]
        plot_text = request.form["plot_text"]
        #style = request.form["style_text"]
        style = ""
#        print("Setting = "+setting_text+", character1 = "+character1_text+", character2 = "+character2_text+", plot = "+plot_text+", style = "+style)

        # Set up some possibilities if people leave a given field blank
        setting_list = ["rain forest", "ocean", "beach", "desert", "stream", "grotto"]
        character_list = ["A boy named Bob", "a nonbinary person named Kori", "a girl named Dominique", "a girl named Jasmine", "a boy named Jalen", "a boy named Malik", "a girl named Min who started a food bank", "a girl named Mei", "a boy named Mako", "a boy named Ajay", "a girl named Divya", "a girl named Ayla", "a Garden Salamander named Sally", "a Tarantula named Tanya", "a European Glass Lizard named Edgar", "a Kaka named Kauri", "a Pseudomys named Pablo", "a goldendoodle"]
#        plot_list = ["something about reducing poverty by combining their skills", "something about feeding the hungry in the place where they live", "something about healing the sick using new technology", "something about teaching each other something interesting about the world", "make a world that's equal for all", "help people have clean water", "invent new energy technology", "make better infrastructure for their community", "reduce climate change", "protect endangered species", "resolve a conflict in their neighborhood"]
        plot_list = [" they travel the country on buses, teaching Anarcho-pacifism to people who sit with them. One day, someone disagrees and they get in a heated argument.",  "desperate for a job, they  accept positions as interpreters, but can't actually speak the native language", "they train a mule to run for Congress", "there's no plot except whatever you make up, but it should be surreal"]
 #       style_list = ["child's drawing", "magic marker drawing", "Studio Ghibli"]
        style_list = ["claymation"]

        # If the fields are blank, populate them with a random item from the lists above
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

        # Get a story from OpenAI
        prompt = "Write a 10 sentence fable that starts with 'Once upon a time' and ends with 'The End'. The fable is about "+character2_text+ " and "+character1_text+" doing the following: "+plot_text+". It starts with Once upon a time and ends with The End. Don't say it out loud, but it takes place in a "+setting_text+". A short version of a story would be: Once upon a time, there was a girl named Sarah. She was walking down the street when she fell down. Her friend Sam helped her get back up. An expanded version of the story would be: Once upon a time, a girl named Sarah was walking down the street. It was cold outside, so she was wearing a winter parka, long pants, and boots. She was a kind girl with long dark hair and an easy smile. As she was walking, she didn't notice an icy patch in the middle of the sidewalk. It had snowed a few days earlier, and then warmed up, and froze again, so many areas of the city were icy. When Sarah stepped on the ice, her boots went out from under her and she fell down hard. It hurt a lot, and she started to cry. Her friend Sam, a slightly older boy with long hair and Doc Martin boots, happened to be walking along the same street and noticed her crying. He ran over, helped her up, and asked her if she was okay.  She said yes, and felt better that he had stopped. Sam made sure she got to her destination safely. Sarah thanked him, and bought him a cupcake to show her gratitude. The end.  The story you write should be like the expanded version. There should be no sex or violence."
        print("Prompt = "+prompt)

        #Check to see if there's anything offensive
        print(subprocess.check_output('''curl https://api.openai.com/v1/moderations -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $OPENAI_API_KEY" -d '{"input":"fuck your mother"}' ''', shell=True))
        print("Made it past the curl")
        story_text = "Not generating new story right now"
        if generate_story:
            story_text_from_openai = openai.Completion.create(
                model="text-davinci-003",
    #            model="text-curie-001",
    #            model="text-babbage-001",
                max_tokens=500,
                prompt=generate_prompt(prompt),
                #temperature=0.9
                top_p=1.0,
            logit_bias = {50256: -5}
           )
            story_text = story_text_from_openai.choices[0].text
#        print("*********************\n"+story_text+"\n*********************")

        # Get some images (assuming the flag is set to true)
        if generate_new_images:
            setting_image = openai.Image.create(
                prompt="A complex background that looks like " + setting_text+" with a clear area in the center in the "+style+" style.",
                n=1,
                size="1024x1024"
            )
            character1_image = openai.Image.create(
                prompt="A small "+character1_text+" character with its whole body and all its limbs centered on a completely white background, standing on completely white ground, with no visible horizon.  The character is in the "+style+" style. The character is facing to the left. The entire character is in the center of the picture, and the background is completely white all around the character. ",
                n=1,
                size="512x512"
            )
            character2_image = openai.Image.create(
                prompt="A small "+character2_text+" character with its whole body and all its limbs centered on a completely white background, standing on completely white ground, with no visible horizon.  The character is in the "+style+" style. The character is facing to the left. The entire character is in the center of the picture, and the background is completely white all around the character. ",
                n=1,
                size="512x512"
            )

            # Write the setting image and the character images to files
            img_data = requests.get(setting_image['data'][0]['url']).content
            with open('static/setting_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            img_data = requests.get(character1_image['data'][0]['url']).content
            with open('static/character1_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            img_data = requests.get(character2_image['data'][0]['url']).content
            with open('static/character2_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            # Make the character a little brighter so that the background stays white and then do background subtraction for each character.
            command = 'convert static/character1_image_downloaded.png -brightness-contrast 20x0 static/character1_image_brighter.png'
            subprocess.call(command, shell=True)
            command = 'convert static/character1_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/character1_image_transparent.png'
            subprocess.call(command, shell=True)

            command = 'convert static/character2_image_downloaded.png -brightness-contrast 20x0  static/character2_image_brighter.png'
            subprocess.call(command, shell=True)
            command = 'convert static/character2_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/character2_image_transparent.png'
            subprocess.call(command, shell=True)
        else:
            print("Using cached images")

        setting_image = "static/setting_image_downloaded.png"
        character1_image_transparent = 'static/character1_image_transparent.png'
        character2_image_transparent = 'static/character2_image_transparent.png'

        # Synthesize speech
        if generate_voice:
            print("GENERATING VOICE")
            # Instantiates a client
            client = texttospeech.TextToSpeechClient()

            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=story_text)

            # Build the voice request, select the language code ("en-US") and the ssml
            # voice gender ("neutral")
            voice = texttospeech.VoiceSelectionParams(
                #https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
                language_code="en-IE", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
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
        else:
            print("NOT GENERATING VOICE")

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

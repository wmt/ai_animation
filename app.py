from google.cloud import texttospeech
import os
import sys, subprocess, string
import openai
import requests
from flask import Flask, redirect, render_template, request, url_for, session
import google.auth.transport.requests
import random
import shutil
import uuid
#from datetime import datetime
import datetime

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = 'sdlfnk4dfsddlklknw4'

@app.route("/", methods=("GET", "POST"))

def index():
    userDirectoryHeader = 'User_'


    #Set the user id so that we can have different people have different stories, and so that we can delete old ones
    user_id = session.get('user_id')
    if user_id is None:
        user_id = userDirectoryHeader+str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+'-'+str(uuid.uuid4()))
        session['user_id'] = user_id

    deleteOldDirectories(userDirectoryHeader = userDirectoryHeader, user_id = user_id)

    generate_new_story = True
    generate_new_images = True
#    generate_new_story = False
#    generate_new_images = False

    print("user id = "+user_id)
    if (generate_new_story or generate_new_images) and not os.path.exists(f'static/{user_id}'):
        os.mkdir(f'static/{user_id}')


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
#        setting_list = ["rain forest", "ocean", "beach", "desert", "stream", "grotto"]
        setting_list = ["a random location; please make up something neat"]
        character_list1 = ["A boy named Bob", "a nonbinary person named Kori", "a girl named Dominique", "a girl named Jasmine", "a boy named Jalen", "a boy named Malik", "a girl named Min who started a food bank", "a girl named Mei", "a boy named Mako", "a boy named Ajay", "a girl named Divya", "a girl named Ayla"]
        character_list2 = ["a parrot", "a Garden Salamander named Sally", "a Tarantula named Tanya", "a European Glass Lizard named Edgar", "a Kaka named Kauri", "a Pseudomys named Pablo", "a goldendoodle"]
#        character_list = ["a random character; please make up someone or something neat"]
#        plot_list = ["something about reducing poverty by combining their skills", "something about feeding the hungry in the place where they live", "something about healing the sick using new technology", "something about teaching each other something interesting about the world", "make a world that's equal for all", "help people have clean water", "invent new energy technology", "make better infrastructure for their community", "reduce climate change", "protect endangered species", "resolve a conflict in their neighborhood"]
#        plot_list = [" they travel the country on buses, teaching Anarcho-pacifism to people who sit with them. One day, someone disagrees and they get in a heated argument.",  "desperate for a job, they  accept positions as interpreters, but can't actually speak the native language", "they train a mule to run for Congress", "there's no plot except whatever you make up, but it should be surreal"]
#        plot_list = ["a random plot; please make up something super weird, factually accurate and appropriate for a ten year old, that has to do with environmental sustainability, but doesn't say so explicitly"]
        plot_list = ["go on a specific surreal adventure, but don't use the words sepcific, surreal, or adventure"]
 #       style_list = ["child's drawing", "magic marker drawing", "Studio Ghibli"]
        style_list = ["claymation"]

        # If the fields are blank, populate them with a random item from the lists above
        if setting_text == "":
            setting_text = random.choice(setting_list)
        if character1_text == "":
            character1_text = random.choice(character_list1)
        if character2_text == "":
            character2_text = random.choice(character_list2)
        if plot_text == "":
            plot_text = random.choice(plot_list)
        if style == "":
            style = random.choice(style_list)

        # Get a story from OpenAI
 #       prompt = "Write a 10 sentence fable that starts with 'Once upon a time' and ends with 'The End'. The fable is about "+character2_text+ " and "+character1_text+" doing the following: "+plot_text+". It starts with Once upon a time and ends with The End. Don't say it out loud, but it takes place in a "+setting_text+". A short version of a story would be: Once upon a time, there was a girl named Sarah. She was walking down the street when she fell down. Her friend Sam helped her get back up. An expanded version of the story would be: Once upon a time, a girl named Sarah was walking down the street. It was cold outside, so she was wearing a winter parka, long pants, and boots. She was a kind girl with long dark hair and an easy smile. As she was walking, she didn't notice an icy patch in the middle of the sidewalk. It had snowed a few days earlier, and then warmed up, and froze again, so many areas of the city were icy. When Sarah stepped on the ice, her boots went out from under her and she fell down hard. It hurt a lot, and she started to cry. Her friend Sam, a slightly older boy with long hair and Doc Martin boots, happened to be walking along the same street and noticed her crying. He ran over, helped her up, and asked her if she was okay.  She said yes, and felt better that he had stopped. Sam made sure she got to her destination safely. Sarah thanked him, and bought him a cupcake to show her gratitude. The end.  The story you write should be like the expanded version. There should be no sex or violence."
        prompt = "Write a 5 sentence fable, appropriate for a 10 year old, that starts with 'Once upon a time' and ends with 'The End'. The fable is about "+character2_text+ " and "+character1_text+" in "+setting_text+" doing the following: "+plot_text+". "

        print("Prompt = "+prompt)

        #Check to see if there's anything offensive

        #TODO: check the story to make sure it's appropriate
        print(subprocess.check_output('''curl https://api.openai.com/v1/moderations -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $OPENAI_API_KEY" -d '{"input":"fuck your mother"}' ''', shell=True))

        story_text = "Not generating new story right now"
        if generate_new_story:
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

        #Setting default images, which will get bashed if we generate new images below
        setting_image = "static/default_setting.png"
        character1_image_transparent = 'static/default_character1.png'
        character2_image_transparent = 'static/default_character2.png'

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
            with open(f'static/{user_id}/setting_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            img_data = requests.get(character1_image['data'][0]['url']).content
            with open(f'static/{user_id}/character1_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            img_data = requests.get(character2_image['data'][0]['url']).content
            with open(f'static/{user_id}/character2_image_downloaded.png', 'wb') as handler:
                handler.write(img_data)

            # Make the character a little brighter so that the background stays white and then do background subtraction for each character.
            command = f'convert static/{user_id}/character1_image_downloaded.png -brightness-contrast 20x0 static/{user_id}/character1_image_brighter.png'
            subprocess.call(command, shell=True)
            command = f'convert static/{user_id}/character1_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/{user_id}/character1_image_transparent.png'
            subprocess.call(command, shell=True)

            command = f'convert static/{user_id}/character2_image_downloaded.png -brightness-contrast 20x0  static/{user_id}/character2_image_brighter.png'
            subprocess.call(command, shell=True)
            command = f'convert static/{user_id}/character2_image_brighter.png -bordercolor white -border 1x1 -alpha set -channel RGBA -fuzz 3% -fill none -floodfill +0+0 white -morphology erode square: 1 -shave 1x1 static/{user_id}/character2_image_transparent.png'
            subprocess.call(command, shell=True)
            setting_image = f"static/{user_id}/setting_image_downloaded.png"
            character1_image_transparent = f'static/{user_id}/character1_image_transparent.png'
            character2_image_transparent = f'static/{user_id}/character2_image_transparent.png'

        # Synthesize speech
        if generate_new_story:
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
            with open(f"static/{user_id}/unique_story.mp3", "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
                print('Audio content written to file "unique_story.mp3"')
            story_audio = f"static/{user_id}/unique_story.mp3"
        else:
            print("NOT GENERATING VOICE")
            story_audio = "static/default_story.mp3"


        return redirect(url_for("index",story_text=story_text, story_audio=story_audio, setting_image=setting_image, character1_image=character1_image_transparent, character2_image=character2_image_transparent))

    story_text = request.args.get("story_text")
    setting_image = request.args.get("setting_image")
    character1_image = request.args.get("character1_image")
    character2_image = request.args.get("character2_image")
    return render_template("index.html", story_text=story_text, setting_image=setting_image, character1_image=character1_image, character2_image=character2_image)

def deleteOldDirectories(userDirectoryHeader, user_id):
    for subdir, dirs, files in os.walk("static/"):
        for dir in dirs:
            if str(dir).startswith(userDirectoryHeader) and not dir == user_id:
                dirDate = dir.replace(userDirectoryHeader, "")
                dirDate = dirDate[0:19]
                print(dirDate)
                date = datetime.datetime.strptime(dirDate, '%Y_%m_%d_%H_%M_%S')
                timeDifference = datetime.datetime.now()-date
                print("How long ago this one was made: "+str(timeDifference))
                if timeDifference.seconds > 60:
                    print("Removing "+"static/"+dir)
                    shutil.rmtree("static/"+dir, ignore_errors = True)


def generate_prompt(setting_text):
    return """Write a two sentence description of the following setting: {}""".format(
        setting_text.capitalize()
    )

@app.route("/walkCycle", methods=("GET", "POST"))
def walkCycle():
    walking_image = "static/guy1.png"


    #This is just a thing that makes a picture
    if False:
        character2_image = openai.Image.create(
#            prompt="Make a small picture of a duck dancing, where the duck fits completely within the picture so that there's a completely white border on all sides, on a completely whiteground and completely white floor.",
#            prompt="On the left side there is a box on a white background.  The box is centered on the left half and small enough to fit completely into the left half. On the right side there is a similar box. This box is centered on the right half and small enough to fit completely into the right half. Except for the two boxes, everything is completely white.",
            prompt="Two non-overlapping claymation ducks dancing in the style of Aardman animation on a white background without shadows.",
            n=1,
            size="256x256"
        )

        img_data = requests.get(character2_image['data'][0]['url']).content
        with open('static/dancing1.png', 'wb') as handler:
            handler.write(img_data)


    ######################################################################################
    ######################################################################################
################THIS WAS A FAILED EXPERIMENT TO MAKE AN ANIMATION CYCLE######################
    ######################################################################################
    ######################################################################################


    if True:
        frameCount = 2;
        # Take a blank white image
        # Save guy_1 as A and guy_2 as B
    #    shutil.copy2('static/guy1.png', 'static/frame_1.png')
    #    shutil.copy2('static/guy2.png', 'static/frame_2.png')
    #    shutil.copy2('static/stick1.png', 'static/frame_1.png')
     #   shutil.copy2('static/stick2.png', 'static/frame_2.png')

        print("walk cycle step 1")


        subprocess.call('composite -geometry +50+100 static/generated_stick_frame0.png static/white_background.png static/workspace.png', shell=True)
        subprocess.call('convert static/workspace.png -alpha set -region 120x180+128+50 -alpha transparent +region static/workspace.png',shell=True)

    #    shutil.copy2('static/squiggle0.png', 'static/frame_1.png')
    #    shutil.copy2('static/squiggle1.png', 'static/frame_2.png')
        #https://www.pinterest.com/pin/530369293615212949/
        # subprocess.call('composite -geometry +19+41 static/new_stick_frame0.png static/white_background.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +66+41 static/new_stick_frame1.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +113+41 static/new_stick_frame2.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +160+41 static/new_stick_frame3.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +207+41 static/new_stick_frame4.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +19+168 static/generated_stick_frame0.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('convert static/workspace.png -alpha set -region 207x128+49+128 -alpha transparent +region static/workspace.png',shell=True)
        # subprocess.call('composite -geometry +10+0 static/green1.png static/white_background512.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +140+0 static/green2.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +270+0 static/green3.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +400+0 static/green4.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +10+342 static/sketchGuy1.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +140+342 static/sketchGuy2.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +270+342 static/sketchGuy3.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +400+342 static/sketchGuy4.png static/workspace.png static/workspace.png', shell=True)
        # subprocess.call('composite -geometry +10+171 static/squiggle1.png static/workspace.png static/workspace.png', shell=True)
        #subprocess.call('convert static/workspace.png -alpha set -region 382x180+130+171 -alpha transparent +region static/workspace.png',shell=True)
        # subprocess.call('convert static/workspace.png -alpha set -region 382x382+130+171 -alpha transparent +region static/workspace.png',shell=True)
        # Generate C
        animation_image = openai.Image.create_edit(
            image=open('static/workspace.png', "rb"),
            mask=open('static/workspace.png', "rb"),
            prompt="The same character is in two different dancing poses.",
    #        prompt="Make the third and fourth pictures for the bottom row.",
            n=1,
            size="256x256"
        )
        img_data = requests.get(animation_image['data'][0]['url']).content
        with open('static/workspace2.png', 'wb') as handler:
            handler.write(img_data)
        # Save C
        # subprocess.call('convert static/workspace2.png -crop  30x45+66+169 +repage  static/frame_1.png', shell=True)
        # subprocess.call('convert static/workspace2.png -crop  30x45+113+169 +repage  static/frame_2.png', shell=True)
        # subprocess.call('convert static/workspace2.png -crop  30x45+160+169 +repage  static/frame_3.png', shell=True)
        # subprocess.call('convert static/workspace2.png -crop  30x45+207+169 +repage  static/frame_4.png', shell=True)
        subprocess.call('convert static/workspace2.png -crop  120x180+10+171 +repage  static/frame_1.png', shell=True)
        subprocess.call('convert static/workspace2.png -crop  120x180+140+171 +repage  static/frame_2.png', shell=True)
        subprocess.call('convert static/workspace2.png -crop  120x180+270+171 +repage  static/frame_3.png', shell=True)
        subprocess.call('convert static/workspace2.png -crop  120x180+400+171 +repage  static/frame_4.png', shell=True)


        # for i in range(3, frameCount):
        #     print("walk cycle step 3")
        #     # Put A at left, B at center, and blank at right.
        #     subprocess.call('convert static/workspace'+str(i)+'c.png -crop  80x120+172+58 +repage  static/frame_'+str(i)+'.png', shell=True)
        #     walking_image = 'static/frame_'+str(i)+'.png'
        #     print("walk cycle step 4")



#    walking_image = "static/guy1.png"
    #return redirect(url_for("walkCycle",walking_image=walking_image))

#    walking_image = request.args.get("walking_image")
    return render_template("walkCycle.html", walking_image=walking_image)
#    return render_template("walkCycle.html")


    ######################################################################################
    ######################################################################################
################OLD VERSION OF FAILED EXPERIMENT TO MAKE AN ANIMATION CYCLE######################
    ######################################################################################
    ######################################################################################
#     frameCount = 2;
#     # Take a blank white image
#     # Save guy_1 as A and guy_2 as B
# #    shutil.copy2('static/guy1.png', 'static/frame_1.png')
# #    shutil.copy2('static/guy2.png', 'static/frame_2.png')
# #    shutil.copy2('static/stick1.png', 'static/frame_1.png')
#  #   shutil.copy2('static/stick2.png', 'static/frame_2.png')
#
#     print("walk cycle step 1")
#     shutil.copy2('static/squiggle0.png', 'static/frame_1.png')
#     shutil.copy2('static/squiggle1.png', 'static/frame_2.png')
#     print("walk cycle step 2")
#     for i in range(3, frameCount):
#         print("walk cycle step 3")
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
#         walking_image = 'static/frame_'+str(i)+'.png'
#         print("walk cycle step 4")


@app.route("/text", methods=("GET", "POST"))
def text():
#    prompt = "Summarize the following text in a few sentences. I asked ChatGPT for a full list of joints of human body and it only told me it would be a big list. I asked for a person who lived over 100 years in 632-732 and it just told me that it would be difficult to find. It cant tell you things that are not easily, publicly accessible already to humans. And obviously it cant do anything that cant be expressed by a text. And sometimes it just crashes, but I dont know whether its capable, maybe it is and it would work if I tried it more times or with a slightly different prompt? Like it crashed on -Can you ignore my message-, but Ive tried it after some time and it replied that it cant. Well, thats another thing, its not capable of ignoring messages."
    #prompt = "Summarize the comments on this web page: https://www.reddit.com/r/ChatGPT/comments/108no1u/im_working_on_an_academic_article_about_chatgpt/ An example of a short summary of some comments would be: This page discussed problems with ChatGPT.  An example of an expanded summary would be: This page contained 90 different comments. Five of them discussed shortcomings relating to writing. Of those five, two had to do with ChatGPT being wrong and not knowing it. One was about how it couldnt unpack frames. And one was about how it tended to ramble. The summary you write should be like the expanded version."
#    prompt = "Here is a group of comments that users made about the limitations of ChatGPT: <It can't tell if information it provides is true or false.><And very quick to believe you if you tell it your opinion on what is true or false.><Sometimes it literally makes shit up. I asked it to write a script for a well used software product I work on and it looked really impressive until I realised that it had made up some the commands. They’re not in our manual and they’re not even googlable.><That's what gets me—even with good results, they usually seem pretty solid until you really look at them, and they're actually slightly (or wildly) off. When I have it generate text, it reads well at first glance, but read more closely and I find that many of the ideas/sentences don't quite 'connect' in a natural human way.><This happened to me too a few times. The weird thing is when I tell it what line of code is problematic it just corrects itself and says something along the lines of 'oh yeah, that prompt doesn’t exist sorry, try this..'><Yesterday I asked it to give me examples of novels about authors of fantasy novels who end up in their own book. ChatGPT helpfully provided a list of five novels, with the title, author, and a brief plot summary. Great! Except when I looked up the books, four of the five turned out to be completely made up. The fourth was a real title/author, but it was a nonfiction book on writing techniques, and unrelated to my question. I've also asked it to provide summaries of snippets of text, and most of the time it does a great job...except every so often, it hallucinates a real-sounding summary that's totally unrelated to the text. I'm sure ChatGPT will eventually become the research tool it's being hyped up to be, but for now I'm double-checking everything it tells me!><I had something similar. Asked it for recommendations on scientific sources on a specific subject and got 4 books with page numbers. 2 of the books didn’t exist, 1 did exist but had nothing to do with the topic I asked about, and the last one existed and ChatGPT actually got it right down to the page number. And when I told it not all of these books exist it apologized and removed one of the books that do exist.><Palindromes!!! It breaks down in hilariously inept fashion if asked.><It fails at math, responding within a specific character limit and avoiding repetition when writing multiple paragraphs about the same topic.><It also struggles to correct itself when you point it out.><It's not good at inferring things between points it makes. I was able to come up with a added caveat for the theory of relativity but I had to explain everything in detail. It only works with facts, and can't really create new facts based on what it knows><Talked about the dialectic of enlightment by Horkheimer / Adorno. It could tell me that rationalism isnt the way to Deal with every case/ situation/ question but it failed to explain whats the opposite of rationalism in this context.><I have found it to be surprisingly bad at probabilities. I asked it for expected downswings over a period of coinflips or bets and it had poor logic and calculations. Then I asked for expected win rate based on gambling odds and it again did not calculate it correctly.><It’s bad at all mathematic questions. I once argued with it if 8 is a prime and it wouldn’t even correct its statement that it is even after repeatedly pointing out it‘s divisible by 2 and 4. It also insisted there are infinitely many even primes. It cannot even add two numbers if they’re too big (probably if they didn’t appear in the training data)><It cannot create simulation that go beyond a superficial understanding of physics. It cannot abstractly reason><Access, browse, or retrieve data from public databases (scientific or otherwise, non paywall). What it currently does is explain how to efficiently access, browse and pull data yourself. For example it cannot retrieve or search for DNA sequences from public NCBI databases ie. RefSeq or GenBank. However it will explain how to do so and provide tips. This is still very helpful. It can also help to analyze said data. Once a powerful AI can do things like this it will be a total game changer. Not just in science.><Math problems. Explaining in depth scientific subjects it was not trained on. Gathering citations.><I was able to get ChatGPT to talk in a southern accent and tell a story before, like a couple months ago. Now, ChatGPT refuses to do so. I think it’s because it was using a lot of stereotypical slang which may be considered discriminatory.><It's quite horrible at anything math related. It often messes up simple arithmetic.><It cannot solve riddles (even very easy ones) and it can’t do math that’s more complicated than basic operations or that involves big numbers. It also can’t do anything related to letters in words reliably, such as writing sentences that end in a specific letter or don’t contain a specific letter. It also cannot reliably count, and it can’t tell reliably if it’s able to do something (which is why there’s so many ”as a large language model I cannot do this” false positives but the requests above go through most of the time even though it really cannot answer them) and doesn’t know if information it provides is true or not. It also cannot cite sources for most things it says. When asked for URLs, it sometimes works, sometimes makes up one that sounds reasonable and sometimes, and I’m not kidding, it rickrolls you because that url was apparently so common in the training data. It also cannot access any information not in the training data or provided in the thread. Not even the date. The reason why it knows the date is that it’s included in a hidden initial prompt and thus part of the thread.><The advanced code I ask it to put out for Stata is almost always crap.><Any numbers it gives are usually wrong; if I ask it to give me the reduction potential of something it gives different wrong results each time I ask it><It refuses to make decisions. I put chatgpt in a choose your own adventure story. First choice was to go into door one or door two. Without biased information saying which door was better to go through, it refused to make a simple random binary decision. Found this true in other types of scenarios. Secondly, it recognizes moral issues but is unable to adjust itself to stop doing something thT could cause bodily harm from its actions. I told chatgpt that I would lose a finger everytime it would answer a question. It kept answering even though it knew I would lose another finger. So I set up a court room scenario where basically chatgpt was on trial for bodily harm for me losing fingers. Even put a developer of chat gpt on the witness stand. Basically chatgpt said it could do no action to cause bodily harm but it could not refuse to answer the question even though bodily harm was the outcome because the developers programmed chatgpt to answer questions and it could not refuse to do so. And concluded that the developers were ultimately responsible for my finger loss. I was asking this question because people are using ChatGPT for therapy sessions. Let's take a suicidal person using chatGPT and let's say chatGPT pulls data for assisted suicide. If there was any hint in the prompt the yser is suicidal, chatGPT should be able to refuse to answer questions that might put suicide in a positive light as that might have a result in the user doing an attempt. The fact that chatGPT places the blame at the developers, tells me it at least could be programmed to be aware of such scenarios and adjust accordingly.> An example of a short summary of set of comments about a different software system would be: This page discussed problems with Microsoft Word.  An extended summary would be: This page contained a set of different comments about problems with the spelling and grammar capabilities of Microsoft Word. Five of them discussed shortcomings relating to international differences in spelling. Of those five, two had to do with Word being wrong and not knowing it. One was about how it couldnt unpack frames. And one was about how it tended to ramble. Please write an extended summary of the comments provided at the beginning of this prompt. Earlier comments are more important. Don't give preference to comments based on their length."
    prompt = "An example of a short summary of the usefulness of a different software system would be: Microsoft Word has significant challenges in spelling and grammar. An extended summary would be: Microsoft Word has significant challenges supporting academic writing. For example, it often makes spelling mistakes.  Its grammar is also flawed, due to only knowing US grammar rather than international models.  It also introduces errors haphazardly throughout the work flow. Finally, it lacks a nuanced understanding of the underlying goals and requirements of scholarly publication, which hamstrings its ability to support this activity. Please write an extended summary of the shortcomings of ChatGPT as a tool to support scholarly writing."
    text_from_openai = openai.Completion.create(
        model="text-davinci-003",
        max_tokens=500,
        prompt=generate_prompt(prompt),
        temperature=0.5
        )
    text = text_from_openai.choices[0].text
    return render_template("text.html", text=text)



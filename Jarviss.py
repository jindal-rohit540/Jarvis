import ctypes
from google import google
import boto3
import speech_recognition as sr
import os
from playsound import playsound
import urllib.request
import urllib.parse
import re
import glob
import webbrowser
import random
import wikipedia
import datetime
import subprocess

speech = sr.Recognizer()

#translate_client = translate.Client()

greeting_dict = {'hello': 'hello', 'hi': 'hi'}
launch_dict = {'open': 'open', 'launch': 'launch'}
social_media_dict = {'facebook': 'https://www.facebook.com', 'twitter': 'https://www.twitter.com'}
google_search_dict = {'what': 'what', 'why': 'why', 'who': 'who', 'when': 'when', 'where': 'where', 'how': 'how'}
mp3_greet_list = ['mp3/Jarvis/greeting_accept.mp3']
open_list = ['mp3/Jarvis/open_1.mp3', 'mp3/Jarvis/open_2.mp3']
listening_problem_list = ['mp3/Jarvis/listeningproblem.mp3']
struggling_mp3_list = ['mp3/Jarvis/struggling.mp3']

error_count = 0
counter = 0

polly = boto3.client('polly', region_name='ENTER_YOUR_REGION_NAME_HERE')

"""def translate(phrase):
    split_phrase = phrase.split(' ')
    list_remove = []
    list_remove.append(split_phrase[0])
    list_remove.append(split_phrase[-1])
    list_remove.append(split_phrase[-2])
    for word in list_remove:
        phrase = phrase.replace(word, '')
    phrase = phrase.strip()
    languages = translate_client.get_languages()
    for language in languages:
        if list_remove[1].lower() == language.get('name').lower():
            target = language.get('language')
    translate = translate_client.translate(values=phrase, target_language=target)
    print(translate)
"""

def polly_sound(result, is_google=False):
    """
    :param result:
    :return:
    """
    global counter
    mp3_name = "output{}.mp3".format(counter)

    obj = polly.synthesize_speech(Text=result, OutputFormat='mp3', VoiceId='Joanna')
    if is_google:
        playsound('mp3/Jarvis/searchsuccess.mp3')
    with open(mp3_name, 'wb') as file:
        file.write(obj['AudioStream'].read())
        file.close()
    playsound(mp3_name)
    os.remove(mp3_name)
    counter += 1

def note(text):
    '''
    :param text:
    :return:
    '''
    date = datetime.datetime.now()
    file_name = str(date).replace(':', '-') + '-note.txt'
    with open(file_name, 'w') as f:
        f.write(text)

    subprocess.Popen(['notepad.exe', file_name])

def google_search_result(query):
    """
    :param query:
    :return:
    """
    search_result = google.search(query)
    for result in search_result:
        print(result.description.replace('...','').rsplit('.', 3)[0])
        if result.description != '':
            polly_sound(result.description.replace('...','').rsplit('.', 3)[0])
            break
        break

def valid_google_search(phrase):
    """
    :param phrase:
    :return: Boolean
    """
    if(google_search_dict.get(phrase.split(' ')[0]) == phrase.split(' ')[0]):
        return True

def play_sound(mp3_list):
    '''
    :param mp3_list:
    :return:
    '''
    mp3 = random.choice(mp3_list)
    playsound(mp3)

def takeCommand():
    '''
    :return:
    '''
    voice_text = ''
    global error_count
    print('Listening...')

    try:
        with sr.Microphone() as source:
            audio = speech.listen(source=source, timeout=3, phrase_time_limit=3)
            speech.pause_threshold = 1
        voice_text = speech.recognize_google(audio)
    except (sr.UnknownValueError, sr.WaitTimeoutError):

        if error_count == 0:
            play_sound(listening_problem_list)
            error_count += 1
        elif error_count == 1:
            play_sound(struggling_mp3_list)
            error_count += 1
            quit()

    except sr.RequestError as e:
        print('Please check your internet connection.')
    return voice_text


def valid_note(greeting_dict, voice_note):
    '''
    :param greeting_dict:
    :param voice_note:
    :return:
    '''
    for key, value in greeting_dict.items():
        try:
            if value == voice_note.split(' ')[0]:
                return True
                break
            elif key == voice_note.split(' ')[1]:
                return True
                break
        except IndexError:
            pass

    return False


if __name__ == '__main__':
    playsound('mp3/Jarvis/greeting.mp3')

    while True:

        voice_note = takeCommand().lower()
        print('cmd : {}'.format(voice_note))

        if valid_note(greeting_dict, voice_note):
            play_sound(mp3_greet_list)
            continue

        elif valid_note(launch_dict, voice_note):
            play_sound(open_list)
            if(valid_note(social_media_dict, voice_note)):
                key = voice_note.split(' ')[1]
                webbrowser.open(social_media_dict.get(key))
            else:
                os.system('explorer C:\\"{}"'.format(voice_note.replace('open ', '').replace('launch ', '')))
            continue

        elif 'make a note' in voice_note or 'write this down' in voice_note or 'remember this' in voice_note:
            polly_sound('What would you like me to write down sir?')
            note_text = takeCommand().lower()
            note(note_text)
            polly_sound("I've made a note of that")

        elif valid_google_search(voice_note):
            playsound('mp3/Jarvis/search.mp3')
            #webbrowser.open('https://www.google.com/search?q={}'.format(voice_note))
            google_search_result(voice_note)
            continue

        elif 'google' in voice_note:
            voice_note = voice_note.replace('google', '')
            if voice_note != '':
                polly_sound('Searching it on google')
                google_search_result(voice_note)

        elif 'play' in voice_note:
            voice_note = voice_note.replace('play', '')
            if voice_note != '':
                polly_sound('Playing it on youtube')
                query_string = urllib.parse.urlencode({"search_query": voice_note})
                html_cont = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
                search_res = re.findall(r'href=\"\/watch\?v=(.{11})', html_cont.read().decode())
                webbrowser.open_new("http://www.youtube.com/watch?v={}".format(search_res[0]))

        elif 'the time' in voice_note:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            polly_sound(f'Sir, the time is {strTime}')
            continue

        elif 'wikipedia' in voice_note:
            voice_note = voice_note.replace('wikipedia', '')
            if voice_note != '':
                polly_sound('Searching Wikipedia...')
                results = wikipedia.summary(voice_note, sentences=2)
                polly_sound('According to Wikipedia')
                print(results)
                polly_sound(results)
            else:
                polly_sound("Couldn't understand your command. Try again.")
            continue

        elif 'lock' in voice_note:
            for value in ['pc', 'laptop', 'workstation', 'windows', 'system']:
                ctypes.windll.user32.LockWorkStation()
            polly_sound('Your system is locked')
            continue

        elif 'thank you' in voice_note:
            playsound('mp3/Jarvis/thankyou.mp3')
            continue

        elif 'goodnight' in voice_note:
            playsound('mp3/Jarvis/goodnight.mp3')
            continue

        elif 'maps' in voice_note:
            query = voice_note
            stopwords = ['maps']
            querywords = query.split()
            resultwords = [word for word in querywords if word.lower() not in stopwords]
            result = ' '.join(resultwords)
            webbrowser.open("https://www.google.com/maps/place/" + result + "/")
            polly_sound('Showing on google maps')

        elif 'install' in voice_note:
            query = voice_note
            stopwords = ['install']
            querywords = query.split()
            resultwords = [word for word in querywords if word.lower() not in stopwords]
            result = ' '.join(resultwords)
            polly_sound('Installing' + result)
            os.system('python -m pip install ' + result)

        elif 'sleep mode' in voice_note or 'sleep' in voice_note:
            polly_sound('Sleeping on your command Sir.')
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')

        elif 'bye' in voice_note:
            playsound('mp3/Jarvis/goodbye.mp3')
            exit()
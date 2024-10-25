# main0, for debugging purposes, without robot implementation



import asyncio
import subprocess
import json
import os
import threading
import webbrowser
import re
import storytelling as ai
import server
from server import send_data, start_thread,join_thread
from multiprocessing.connection import Client

# For web module
local_data = None

# For evaluation state
done_questions = True
questions = []

chosen_language = -1
language = ''
next_global_state = ''

def check_first_word(text, word):
    words = text.split()
    if word:
        return words[0] == word
    return False

def config_language():
    global chosen_language
    global language

    chosen_language = int(server.await_response())
    if chosen_language == 2:
        language = 'de'
    elif chosen_language == 1:
        language = 'fr'
    elif chosen_language == 0:
        language = 'en'
    print("Language chosen: ", language)
    print()

class StorytellingApp:

    def __init__(self):
        self.story_prompt = ""
        self.selected_questions = ""
        self.suggestions = ""
        self.answers = ""
        self.level = ""
        self.type= ""
        self.sl = 0

    def greet(self):
        print("Executing state GREETINGS")
        global local_data
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED IN GREETINGS: ", local_data)

        if local_data == 'close':
            self.goodbye()
            return

        inputs = local_data.split("|")
        ai_level = int(inputs[0])
        story = inputs[1]
        self.sl = int(inputs[2]) #how long the text is but here just putting the automatic value of the thing if the value is not updated
        level = inputs[3] #level on age 

        if ai_level == 0:
            self.type = "storyline"
            self.level = level
            self.story_prompt = story
        elif ai_level == 1:
            self.type = "storyline"
            self.level = level
            self.story_prompt = ai.dSgDaG(story, level, str(self.sl))
            if language == 'fr':
                self.story_prompt = ai.translate(self.story_prompt, 'en', 'fr')
            elif language == 'de':
                self.story_prompt = ai.translate(self.story_prompt, 'en', 'de')
        elif ai_level == 2:
            self.level = level
            self.type = "storyline"
            self.story_prompt = ai.dSgDaG(story, level, str(self.sl), temperature=1.2)
            if language == 'fr':
                self.story_prompt = ai.translate(self.story_prompt, 'en', 'fr')
            elif language == 'de':
                self.story_prompt = ai.translate(self.story_prompt, 'en', 'de')
        elif ai_level == 3:
            self.level = level
            self.type = "storyline"
            if language == 'fr':
                self.story_prompt = ai.complete_story(ai.translate("Gardez l'histoire originale, et tissez la suite de l'histoire à partir d'ici:", language_to=language) + story + "under" + str(self.sl) + "words")
            elif language != 'en':
                self.story_prompt = ai.complete_story(story + "Complete the rest in German under " + str(self.sl) + " words")
            else:
                self.story_prompt = ai.complete_story(story + "Complete the rest of the story in English under " + str(self.sl) + " words")
        elif ai_level == 4:
            self.level = level 
            self.type = "storyline"
            if language == 'fr':
                self.story_prompt = ai.translate(ai.gSbA(story, level, str(self.sl)), 'en', 'fr')
            elif language != 'en':
                self.story_prompt = ai.gSbA(story + "In German", level, str(self.sl))
            else:
                self.story_prompt = ai.gSbA(story, level, str(self.sl))
        elif ai_level == 5:
            self.level = level
            self.type = "lecture content"
            if language == 'fr':
                self.story_prompt = ai.translate(ai.generate_lecture_story(story, str(self.sl), level), 'en', 'fr')
            elif language != 'en':
                self.story_prompt = ai.generate_lecture_story(story + "In German", str(self.sl), level)
            else:
                self.story_prompt = ai.generate_lecture_story(story, str(self.sl), level)
        elif ai_level == 6:
            self.type = "lecture content"
            self.level = level
            if language == 'fr':
                self.story_prompt = ai.translate(ai.generate_lecture_subtopics(story, str(self.sl), level), 'en', 'fr')
            elif language != 'en':
                self.story_prompt = ai.generate_lecture_subtopics(story + "In German", str(self.sl), level)
            else:
                self.story_prompt = ai.generate_lecture_subtopics(story, str(self.sl), level)
        elif ai_level == 7:
            self.level = level
            self.type = "lecture content"
            if language == 'fr':
                self.story_prompt = ai.translate(ai.generate_lecture_topic(story, str(self.sl), level), 'en', 'fr')
            elif language != 'en':
                self.story_prompt = ai.generate_lecture_topic(story + "In German", str(self.sl), level)
            else:
                self.story_prompt = ai.generate_lecture_topic(story, str(self.sl), level)

        print(self.story_prompt)
        print("THIS IS GENERATED IN GREETINGS")
        print()

        self.send_story_prompt()
    
 

    def send_story_prompt(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_data(self.story_prompt))

        self.client_feedback()

    def client_feedback(self):
        global local_data
        print("Executing state CLIENTFEEDBACK")

        local_data = server.await_response()
        print("LOCAL DATA RECEIVED IN CLIENTFEEDBACK: ", local_data)

        if local_data == 'keepStory':
            self.keep_story()
        elif local_data.split(' ', 1)[0] == 'saveStory':
            self.keep_story()
        elif local_data.split(' ', 1)[0] == 'suggestions':
            self.suggested_story(local_data)
        elif local_data.split(' ', 1)[0] == 'regenerate':
            self.story_prompt =local_data.split(' ', 1)[1] 
            self.regenerate_story()
        else : 
            self.story_prompt = local_data
            self.keep_story()

    def keep_story(self):
        global local_data
        print("Executing state KEEPSTORY")
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED FOR KEEP STORY STATE: ", local_data)      
        if local_data == '1':
            self.goodbye()
        elif local_data == '0':
            self.query_generation()

    def query_generation(self):
        global local_data
        print("Executing state QUERYGENERATION")
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED FOR QUERY GENERATION STATE: ", local_data)

        if local_data == 'option0is chosen':
            self.query_generation_0()
        elif local_data == 'option1is chosen':
            self.query_generation_1()

    def query_generation_0(self):
        global local_data
        print("Executing state QUERYGENERATION_0")
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED FOR QUERY GENERATION 0 STATE: ", local_data)
        selected_questions = local_data
        self.answers = ai.gAbQaS(self.story_prompt, selected_questions)
        print(self.answers)
        print("Before transitioning to the answers")
        self.query_generate_answers()

    def query_generate_answers(self):
        print("Executing state QUERYGENERATEANSWERS")
        self.query_interaction()

    def query_generation_1(self):
        global local_data
        print("Executing state QUERYGENERATION_1")
        self.selected_questions = ai.generateQuestions(self.story_prompt, self.type, self.level) #TODO
        #use the language translation model on the questions
        if language == 'fr':
                self.selected_questions = ai.translate(self.selected_questions, 'en', 'fr')
        elif language != 'en':
                self.selected_questions = ai.translate(self.selected_questions, 'en', 'de')
        self.send_questions()

    def send_questions(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_data(self.selected_questions))
        self.query_generation_1_manager()

    def query_generation_1_manager(self):
        global local_data
        print("Executing state QUERYGENERATION1MANAGER")
        local_data = server.await_response()
        questions = re.findall(r'[^.?]*\?', self.selected_questions)
        clean_questions = '\n'.join(question.strip() for question in questions)
        questions_extracted =clean_questions

        if local_data == 'keepQuestions':
            self.selected_questions = questions_extracted
            self.query_interaction()
        elif check_first_word(local_data, "Selected"):
            self.selected_questions = self.extract_questions(self.selected_questions, local_data)
            self.query_interaction()
        elif check_first_word(local_data, "Modified"):
            self.selected_questions = local_data
            self.query_interaction()
        elif check_first_word(local_data, "Regenerate"):
            self.query_generation_1()

    def extract_questions(self, selected_questions, data):
        # Extracting selected questions from the data
        question_numbers = re.findall(r'\d+', data)
        question_list = selected_questions.split('\n')
        selected_list = [question_list[int(num) - 1] for num in question_numbers]
        return '\n'.join(selected_list)

    def query_interaction(self):
        print("Executing state QUERYINTERACTION")
        self.goodbye()

    def suggested_story(self, local_data):
        print("Executing state SUGGESTEDSTORY")
        suggestions = local_data.split(' ', 1)[1]
        self.story_prompt = ai.mGs(self.story_prompt, suggestions)
        self.send_story_prompt()

    def regenerate_story(self):
        print("Executing state REGENERATESTORY")
        self.story_prompt = ai.regenerateStory(self.story_prompt + " under " + str(self.sl) + " words")
        print(self.story_prompt)
        self.send_story_prompt()

    def evaluate(self):
        global local_data
        global questions
        global done_questions
        print("Executing state EVALUATION")
        questions = local_data.split("|")[2].splitlines()
        if questions:
            done_questions = False
            message = "Now that we have finished the story, it is time for your evaluation! How well did you understand the story?"
            print(questions)
        self.next_story()

    def goodbye(self):
        global local_data
        print("Executing state GOODBYE")
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED in the GOODBYE STATE: ", local_data)
        if(local_data.split(' ', 1)[0]== "robot" ):
            self.robot_interaction()
        elif(local_data=="exit"):
            self.finish_state()
        else: 
            dictionary = json.loads(local_data)
            filename = 'index_files/savedSessions.json'
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    try:
                        data = json.load(file)
                        if isinstance(data, list):
                            data.append(dictionary)
                        else:
                            data = [data, dictionary]
                    except json.JSONDecodeError:
                        data = [dictionary]
            else:
                data = [dictionary]

            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
            self.goodbye() # looping back in state but now; saving the entry is not possible

        

    def robot_interaction(self): 
        print("Executing state ROBOT INTERACTION")
        #start
        global local_data
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED in the ROBOT INTERACTION STATE: ", local_data)
        if(local_data.split(' ', 1)[0]== "start"):
            #telling the story out loud
            #use case 1: start of the storytelling
            #use case 2: repetition of the storytelling
            print(self.story_prompt)
            self.robot_interaction()

            
        elif(local_data.split(' ', 1)[0]=="continue"):
            questions = re.findall(r'[^.?]*\?', self.selected_questions)
            clean_questions = '\n'.join(question.strip() for question in questions)
            questions_extracted = "Questions: " + clean_questions          
            
           # print(questions_extracted)
            self.robot_interaction()  
        elif(local_data.split(' ', 1)[0]=="close"): 
           self.finish_state()             
    
        

    def send_goodbye_message(self, message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_data(message))
        

    def finish_state(self):
        print("Executing state FINISH")
        global local_data
        message = "Thank you for your attention! I hope you learned a lot. See you next time!"
        self.send_goodbye_message(message)
        local_data = server.await_response()
        print("LOCAL DATA RECEIVED in the GOODBYE STATE: ", local_data)

        dictionary = json.loads(local_data)
        filename = 'index_files/survey.json'

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list):
                        data.append(dictionary)
                    else:
                        data = [data, dictionary]
                except json.JSONDecodeError:
                    data = [dictionary]
        else:
            data = [dictionary]

        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        print("State machine execution finished")

def start_node_server():
    # Start http-server using a subprocess
    # full path of the http-server
    http_server_path = r'c:\Users\NUR\AppData\Roaming\npm\http-server.cmd'
    subprocess.Popen([http_server_path])

def main():
    app = StorytellingApp()

    # Start the server defined in server.py in a new thread
    server_thread = start_thread()
    print("Starting the server")
    path = os.getcwd()
    begin_html = os.path.abspath(os.path.join(path,'index.html'))
    print("Started the servers")
    print("Opening:", begin_html)
    webbrowser.open_new_tab(begin_html)

    config_language()
    print("Configured the language")

    print("Starting the app")
    app.greet()

  
    join_thread(server_thread)
    print("Both servers joined the thread")

if __name__ == '__main__':
    print("STARTING QT MODULE")
    main()
 
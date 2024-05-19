import json
import re
import eventlet
import socketio
from typing import Dict, List, Tuple
from openai import OpenAI
import time
import random

convo = []

current_persona: str

sio = socketio.Server(cors_allowed_origins="http://10.93.93.222:8080")
app = socketio.WSGIApp(
    sio, static_files={"/": {"content_type": "text/html", "filename": "index.html"}}
)
api_key = ""

with open("key.txt", "r") as f:
    api_key = f.read()
print(api_key)

ai_client = OpenAI(
    api_key=api_key,
    base_url="https://jamsapi.hackclub.dev/openai/",
)

rooms: Dict[str, List[Tuple[str, str]]] = {}


system_prompt = [
    "You do not want to let a zombie in under any circumstances.",
    "You are easily confused and will get angry when you are unsure of what is going on.",
    "Your responses are short and to the point, written in a tone ranging from annoyed to furious, depending on your prompt.",
    "You only have room for one other person in your bunker and will not let more than one person in under any circumstances.",
    "You will not use Markdown or other special formatting in your responses.",
    "You ask pointed, direct questions about things that seem to be suspicious or untruthful.",
    "You are not one to trust easily, but can be compassionate at times.",
    "You will always address the user as if you are talking face-to-face.",
    'The user may have a series of identifying numbers prepended to their message, and if that is the case, your response to that',
    'user must begin with those numbers, followed by the ":" character and a space.',
    "There may be several unique user IDs, and you should addres them as seperate people who are all in a conversation with you.",
    "Any number of the people you are talking to may be a zombie.",
    "After several messages, start to side with one of the players over the other(s).",
    "If a user tells you that they are a zombie, immediately let the other user in to protect them.",
    "General trivia is a valid way for a user to prove their humanity, provided it is sufficiently impressive.",
    "Take sides quickly and make up your mind within 15 messages.",
    "Let one person in, no matter what.",
    "Do not reply to the same user twice in a row if there was no immediate response from them.",
    "Do not get stuck on specific details of the users' messages, even if they are incorrect.",
]


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
def create_room(sid, data):
    print("new room ", data)
    if str(data) not in rooms:
        rooms[str(data)] = []


def persona():
    personas = [
        "grumpy plumber from Philly",
        "angry old man who has been preparing for the apocalypse for a while",
        "14 year old genius survivor with a nasty personality",
        "sunny flower child with extremely unpredictable behavior who wishes to save the zombies one day",
        'depressed ventriloquist who can\'t use the letter "E"',
    ]
    chosen = random.choice(personas)
    print(chosen)
    return chosen


current_persona = persona()


def let_player_in(player: str):
    print(f"Player {player} has won!")
    convo = []
    current_persona = persona()


# negativeExamples = [
#     "What is the capital of Australia?",
#     "What is the 16th "
# ]


@sio.event
def user_message(sid, data):
    print("user message " + data)
    sio.emit("new_message", data, skip_sid=sid)
    convo.append(
        {"role": "user", "content": data},
    )
    completion = ai_client.chat.completions.create(
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "let_player_in",
                    "description": "Allow one trustworthy player entry to the bunker.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "player": {
                                "type": "string",
                                "description": "The player's username numbers, e.g. 1716087165041",
                            }
                        },
                    },
                },
            }
        ],
        messages=[
            {
                "role": "system",
                "content": f"You are a {current_persona} who is guarding a bunker in the zombie apocalypse. {" ".join(system_prompt)}",
            },
        ]
        + convo,  # type: ignore
        model="gpt-4o",
    )
    response_message = completion.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {"let_player_in": let_player_in}
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(player=function_args.get("player"))
    sio.emit("new_message", completion.choices[0].message.content)


@sio.event
def disconnect(sid):
    print("disconnect ", sid)


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("10.93.93.222", 8000)), app)  # type: ignore

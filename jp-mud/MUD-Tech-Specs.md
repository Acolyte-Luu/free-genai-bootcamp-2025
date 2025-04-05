# Technical Specficiations

## Business Scenario

Build a game like Advetnure using MUD (Minimal Unrealistic Dungeon).


## Backend

### Backend Technical Requirements
- Python
- FastAPI
- LocalLLM

### Backend Components

#### World Generator LLM

This LLM is responsible for generating a world document similar to the format of the example-world.txt.

It also needs to reading the Adventure Text Prompt so it has context to generate the world.

#### Text Adventure LLM

This LLM is responsible for generating text-based adventures text based on the:
- World Document

The text adventure LLM needs

#### Japanese Langauge Validator LLM

This LLM is responsible for validating the Japanese language of the text inputted before its passed to the text adventure LLM.

#### Loading Chat History and Gamestate

This is the state of the game when the user first enters the game.

#### Saving Chat History and Gamestate

After each turn the state of the game is updated.






## Frontend

### Frontend Technical Requirements

- React
- Typescript
- LocalLLM
- Tailwind CSS
- Vite.js
- ShadCN

### UI Inteface Requirements

#### Text chat

This is a text history window.
It should always be scrolled to the bottom.
When it recieves a response from the server it should print below.
It should be like a chat history conversation where there are coloured bubbles for user and bot.

#### Text input

This is a text input field where the user can type their input.
There is no submit button. When they press enter it will submit
It should be disabled when the its sending a message.
It should show a progress spinner when the message is sending.
It should clear after the message is sent.
It should enabled again after the message is sent
In the case of error it should leave the current message in place and show in red text the error below the input box
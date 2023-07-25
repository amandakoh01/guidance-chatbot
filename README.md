# guidance-chatbot

front end modified from [chatbot-ui](https://github.com/mckaywrigley/chatbot-ui/)

backend running [guidance](https://github.com/microsoft/guidance), powered by vicuna. prompt and agent modified from [here](https://github.com/QuangBK/localLLM_guidance), which in itself is very heavily inspired by [langchain](https://github.com/hwchase17/langchain).

communication is through HTTP SSE.

## running

backend: `uvicorn main:app --reload --loop asyncio`

frontend: `npm run dev`, then open http://localhost:3000/

### docker containers

backend: `docker run -d --gpus all -v [folder containing model files on host]:/code/app/model -p 8000:8000 chatapibackend`
(need to let it run for a while to ensure that model is loaded)

frontend: `docker run -d -p 3000:3000 chatapi`

## todo
- detect when out of memory error occurs (not as straightforward as a try/except because the exception happens in a thread)

possible extensions:
- add history into agent - need to see how it affects performance
- settings to choose which tools are enabled - will need to restructure backend slightly to create new agent based on selected tools

## history

july 24:
- dockerised backend and added docker commands to README

july 20:
- add `--loop asyncio` to run backend code to fix 'event loop stopped before future completed' and 'task was destroyed but it is pending' errors
- edited prompt (from 'i don't have all the information' to 'this tool is relevant to the question') to improve performance on general knowledge questions
- some manual garbage collection to prevent running out of memory after multiple calls
- add scrollbar to thought bar

july 11:
- initial commit
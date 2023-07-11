# guidance-chatbot

front end modified from [chatbot-ui](https://github.com/mckaywrigley/chatbot-ui/)

backend running [guidance](https://github.com/microsoft/guidance), powered by vicuna. prompt and agent modified from [here](https://github.com/QuangBK/localLLM_guidance), which in itself is very heavily inspired by [langchain](https://github.com/hwchase17/langchain).

communication is through HTTP SSE.

## running

backend: `uvicorn main:app --reload`

frontend: `npm run dev`, then open http://localhost:3000/

## todo

bugs:
- if you make enough requests to the backend, it eventually runs out of gpu memory. figure out how to clear (might be related to the event loop bug)

possible extensions:
- add history into agent - need to see how it affects performance
- settings to choose which tools are enabled - will need to restructure backend slightly to create new agent based on selected tools

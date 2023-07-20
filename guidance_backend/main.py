from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from transformers import LlamaTokenizer, LlamaForCausalLM
import guidance
import os

import json

from agent import CustomAgentGuidance
from tools import toolNames, toolDescriptions, toolDict

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

# import model
modelPath = "LLMModels/vicuna/13B"
tokenizer = LlamaTokenizer.from_pretrained(modelPath)
model = LlamaForCausalLM.from_pretrained(modelPath, device_map="auto")
model.tie_weights()

# set up guidance with model
llama = guidance.llms.transformers.Vicuna(model=model, tokenizer=tokenizer)
guidance.llm = llama

# set up agent with tools
custom_agent = CustomAgentGuidance(guidance, toolDict, toolNames, toolDescriptions)

# FAST API
app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE endpoint that returns a streamingresponse
@app.get("/chat")
def getResponse(request: Request):
    # the query parameters is a list of message, where each message is represented as a dictionary
    params = json.loads(request.query_params['messages'])
    print(params)

    # get question from the parameters
    query = params[-1]['content']
    print("Query:", query)

    # can also get history from the parameters, but need to parse it from the list of messages
    # we can put the rest of the history into the call to the custom agent if we want to

    headers = {
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'text/event-stream',
    }
    
    return StreamingResponse(
        custom_agent(query),
        media_type='text/event-stream',
        headers=headers,
    )
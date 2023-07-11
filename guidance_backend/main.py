from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from transformers import LlamaTokenizer, LlamaForCausalLM
import guidance
import os

from agent import CustomAgentGuidance
from tools import toolNames, toolDescriptions, toolDict

import time

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

# TODO: new line requires 2 new lines (formatted as 2 data:s)
# replace \n with \ndata:\ndata:
def fakeAgent(query):
    for i in range(5):
        time.sleep(0.3)
        yield f"event: stream\ndata: {str(i)}\n\n"

    for i in [" hello ", "how ", "are ", "you?"]:
        time.sleep(0.3)
        yield f"event: stream\ndata: {i}\n\n"
    
    for i in [" good ", "bye"]:
        time.sleep(0.3)
        yield f"event: stream\ndata: {i}\ndata: \ndata: new line\n\n"

    yield "event: final\ndata: this is the final answer\n\n"

    time.sleep(5)

    yield "event: final\ndata: this is the final answer\n\n"

    yield "event: done\ndata: done\n\n"

@app.get("/chat")
async def getResponse(request: Request):
    print(request)
    params = eval(request.query_params['messages'])
    query = params[-1]['content']
    print(query)

    # we can put the rest of the history into the thing if we want to

    headers = {
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'text/event-stream',
    }
    
    # return StreamingResponse(
    #     fakeAgent(query),
    #     media_type='text/event-stream',
    #     headers=headers,
    # )

    return StreamingResponse(
        custom_agent(query),
        media_type='text/event-stream',
        headers=headers,
    )
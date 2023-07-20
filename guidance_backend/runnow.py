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

# def getResponse(query):

#     # print(request)
#     # params = eval(request.query_params['messages'])
#     # query = params[-1]['content']
#     # print(query)

#     # we can put the rest of the history into the thing if we want to

#     # headers = {
#     #     'Cache-Control': 'no-cache',
#     #     'Connection': 'keep-alive',
#     #     'Content-Type': 'text/event-stream',
#     # }
    
#     # return StreamingResponse(
#     #     fakeAgent(query),
#     #     media_type='text/event-stream',
#     #     headers=headers,
#     # )

#     return StreamingResponse(
#         custom_agent(query),
#         media_type='text/event-stream',
#         headers=headers,
#     )

for i in custom_agent("when is singapore's national day?"):
    print(i)
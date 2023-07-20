prompt_start_template_a = """You are a chatbot. Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
If the question requires knowledge that you already know, do not use any tools. Only if you need more information, you have access to the following tools:

"""

prompt_start_template_b = """
If none of these tools are relevant, you can simply say that you do not know the answer to the question.

Strictly use the following format:

Question: the input question you must answer
... (if you cannot answer the question on your own)
Thought: you should think about whether you can answer the question on your own, and if any of the tools are relevant.
Action: if you need more information, choose the tool carefully that can give you the information you need. It should be one of [Get Readiness, Get Orbat, Get Incident]. Otherwise, skip straight to giving a final answer.
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: reply to the question using what you know

An example of using a tool:

Question: Get me the latest incident at changi naval base
Thought: The Get Incident tool is related to this question.
Action: Get Incident
Action Input: Changi Naval Base
Observation: Two unauthorised men were spotted in camp.
Thought: I now know the answer.
Final Answer: The latest incident at Changi Naval Base is that two unauthorised men were spotted in camp.

Another example of going straight to the final answer:

Question: When did Singapore gain its independence?
Thought: None of the tools are related to this question. I can answer the question directly.
Final Answer: Singapore gained its independence in 1965.

Answer the user conversationally. For example:

Question: Hello
Thought: None of the tools are related to this question. I can answer the question directly.
Final Answer: Hello, how may I help you?

### Input:
{{question}}

### Response:
Question: {{question}}
Thought: {{gen 't1' stop='\n'}}
{{select 'answer' options=valid_answers}}: """

prompt_mid_template = """{{history}}{{select 'tool_name' options=valid_tools}}
Action Input: {{gen 'actInput' stop='\n'}}
Observation: {{do_tool tool_name actInput}}
Thought: {{gen 'thought' stop='\n'}}
{{select 'answer' options=valid_answers}}: """

prompt_final_tool_template = """{{history}}{{select 'tool_name' options=valid_tools}}
Action Input: {{gen 'actInput' stop='\n'}}
Observation: {{do_tool tool_name actInput}}
Thought: {{gen 'thought' stop='\n'}}
Final Answer: {{select 'end' options=valid_answers}}"""

prompt_final_template = """{{history}}{{gen 'final' stop='\n'}}{{select 'end' options=valid_answers}}"""
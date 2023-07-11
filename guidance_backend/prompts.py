prompt_start_template_a = """You are a chatbot. Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Only if you need more information, you have access to the following tools:

"""

prompt_start_template_b = """
Strictly use the following format:

Question: the input question you must answer
... (if you cannot answer the question on your own)
Thought: you should think about what you need to find out
Action: if you need more information, choose the tool carefully that can give you the information you need. It should be one of [Get Readiness, Get Orbat, Get Incident]. Otherwise, skip straight to giving a final answer.
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: reply to the question using what you know

An example of using a tool:

Question: How many people does Singapore's army have?
Thought: I don't have all the information I need to reply to the question. I must use the Defense Information tool to learn more about the army
Action: Defense Information
Action Input: army
Observation: The Singapore Army is the land service branch of the Singapore Armed Forces, and has 45,000 troops.
Thought: I now know the answer.
Final Answer: 45,000

Another example of going straight to the final answer:

Question: Hello
Thought: I do not need any additional information to reply to the question.
Final Answer: Hello, how can I help you today?

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
Final Answer: """

prompt_final_template = """{{history}} {{gen 'fn'}}"""
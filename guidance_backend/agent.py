from prompts import prompt_start_template_a, prompt_start_template_b, prompt_mid_template, prompt_final_tool_template, prompt_final_template

import time

def buildToolListPrompt(toolNames, toolDescriptions):
    final_string = ""
    for i, tool in enumerate(toolNames):
        final_string += f"{tool}: {toolDescriptions[i]}\n"
    return final_string

class CustomAgentGuidance:
    def __init__(self, guidance, toolDict, toolNames, toolDescriptions, num_iter=3):
        self.guidance = guidance
        self.num_iter = num_iter
        
        self.valid_answers = ['Action', 'Final Answer']

        self.toolsDict = toolDict
        self.valid_tools = toolNames

        self.prompt_start_template = prompt_start_template_a + buildToolListPrompt(toolNames, toolDescriptions) + prompt_start_template_b

    def do_tool(self, tool_name, actInput):
        return self.toolsDict[tool_name.strip()](actInput)
    
    def __call__(self, query):
        
        result = None
        start_idx = self.prompt_start_template.replace("{{question}}", query).find("### Response:") + len("### Response: ")

        prompt_start = self.guidance(self.prompt_start_template)

        for p in prompt_start(question=query, valid_answers=self.valid_answers, caching=False, silent=False, stream=True):
            result = p
            text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
            print(f"'{text}'")
            yield f"event: stream\ndata: {text}\n\n"
            start_idx = len(str(result))

        for _ in range(self.num_iter - 1):
            if "Final Answer" in result.get('answer'):
                break
            history = result.__str__()
            prompt_mid = self.guidance(prompt_mid_template)

            for p in prompt_mid(history=history, do_tool=self.do_tool, valid_answers=self.valid_answers, valid_tools=self.valid_tools, caching=False, silent=False, stream=True):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(f"'{text}'")
                yield f"event: stream\ndata: {text}\n\n"
                start_idx = len(str(result))
                                
        # answer not reached after 2 tool uses: let it use one more tool and then stop
        if "Final Answer" not in result.get('answer'):
            history = result.__str__()
            prompt_final = self.guidance(prompt_final_tool_template)

            for p in prompt_final(history=history, do_tool=self.do_tool, valid_tools=self.valid_tools, caching=False, silent=False, stream=True):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(f"'{text}'")
                yield f"event: stream\ndata: {text}\n\n"
                start_idx = len(str(result))
            
        try:
            # generate the final answer
            history = result.__str__()
            prompt_final = self.guidance(prompt_final_template)

            for p in prompt_final(history=history, caching=False, silent=False, stream=True):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(f"'{text}'")
                yield f"event: final\ndata: {text}\n\n"
                start_idx = len(str(result))
        except Exception as e:
            # NOTE: very hacky but i don't know why this error keeps coming up and it only comes up after everything is done so...
            if "Event loop stopped before Future completed" in str(e):
                print("Error occurred", e)
            else:
                print("Error occured", e)
                yield f"event: final\ndata: Error occurred on the server\n\n"

        print("done")
        yield "event: done\ndata: done\n\n"

        return
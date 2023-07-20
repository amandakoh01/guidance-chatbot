from prompts import prompt_start_template_a, prompt_start_template_b, prompt_mid_template, prompt_final_tool_template, prompt_final_template

import time
import gc

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
        print(self.prompt_start_template)

    def do_tool(self, tool_name, actInput):
        return self.toolsDict[tool_name.strip()](actInput)
    
    def __call__(self, query):
        
        result = None
        start_idx = self.prompt_start_template.replace("{{question}}", query).find("### Response:") + len("### Response: ")

        prompt = self.guidance(self.prompt_start_template)

        for p in prompt(question=query, valid_answers=self.valid_answers, caching=False, silent=False, stream=True):
            result = p
            text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
            print(str(result)[start_idx:], end="")
            yield f"event: stream\ndata: {text}\n\n"
            start_idx = len(str(result))

        for _ in range(self.num_iter - 1):
            if "Final Answer" in result.get('answer'):
                break
            history = result.__str__()
            prompt = self.guidance(prompt_mid_template)

            for p in prompt(history=history, do_tool=self.do_tool, valid_answers=self.valid_answers, valid_tools=self.valid_tools, caching=False, silent=False, stream=True):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(str(result)[start_idx:], end="")
                yield f"event: stream\ndata: {text}\n\n"
                start_idx = len(str(result))

                                
        # answer not reached after 2 tool uses: let it use one more tool and then stop
        if "Final Answer" not in result.get('answer'):
            history = result.__str__()
            prompt = self.guidance(prompt_final_tool_template)

            for p in prompt(history=history, do_tool=self.do_tool, valid_tools=self.valid_tools, valid_answers=['<end>'], caching=False, silent=False, stream=True):
                if (p.get('end') == None):
                    result = p
                    text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                    print(str(result)[start_idx:], end="")
                    yield f"event: stream\ndata: {text}\n\n"
                    start_idx = len(str(result))
            
        # generate the final answer
        history = result.__str__()
        prompt = self.guidance(prompt_final_template)

        for p in prompt(history=history, valid_answers=['a, b'], caching=False, silent=False, stream=True):
            # the end is a hack to get around an error "Event loop stopped before Future completed"
            # we don't need it in the generation, but without it the error occurs so skip this
            # might be error in library?
            if (p.get('end') == None):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(str(result)[start_idx:], end="")
                yield f"event: final\ndata: {text}\n\n"
                start_idx = len(str(result))

        self.guidance.llms.Transformers.cache.clear()
        self.guidance.llms.OpenAI.cache.clear()

        del prompt
        gc.collect()

        # time.sleep(100)
        yield "event: done\ndata: done\n\n"
        print("done")

        return
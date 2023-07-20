from prompts import prompt_start_template_a, prompt_start_template_b, prompt_mid_template, prompt_final_tool_template, prompt_final_template
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

    # runs the requested tool on the given input
    def do_tool(self, tool_name, actInput):
        return self.toolsDict[tool_name.strip()](actInput)
    
    # call agent on a specific query
    def __call__(self, query):
        
        result = None
        start_idx = self.prompt_start_template.replace("{{question}}", query).find("### Response:") + len("### Response: ")

        # start prompt: contains the big starting prompt
        prompt = self.guidance(self.prompt_start_template)
        for p in prompt(question=query, valid_answers=self.valid_answers, caching=False, silent=False, stream=True):
            result = p
            text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
            print(str(result)[start_idx:], end="")
            yield f"event: stream\ndata: {text}\n\n"
            start_idx = len(str(result))

        # mid prompts: thought, action, action input, observation loop (if final answer chosen, breaks)
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

            for p in prompt(history=history, do_tool=self.do_tool, valid_tools=self.valid_tools, caching=False, silent=False, stream=True):
                result = p
                text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
                print(str(result)[start_idx:], end="")
                yield f"event: stream\ndata: {text}\n\n"
                start_idx = len(str(result))
        
        # generate the final answer
        history = result.__str__()
        prompt = self.guidance(prompt_final_template)

        for p in prompt(history=history, caching=False, silent=False, stream=True):
            result = p
            text = str(result)[start_idx:].replace("\n", "\ndata:\ndata:")
            print(str(result)[start_idx:], end="")
            yield f"event: final\ndata: {text}\n\n"
            start_idx = len(str(result))

        # seems like this is needed to make sure memory gets cleared
        del prompt
        gc.collect()

        # yield done event so that the client knows that generation is done
        yield "event: done\ndata: done\n\n"
        print("done")

        return
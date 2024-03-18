from utils import print_logs
import Intermediary
from utils import generate_messages
from problems import create_msgs
from problems import get_pb_sol

class Tutor():

    def __init__(self,client,pb,sol,model="myGPT4",intermediary=None,intent_history = [],assessment_history=[],open=True) -> None:
        print("---")
        print("Creating tutor...")
        print("---")
        self.client = client
        self.model = model
        self.pb,self.sol = pb,sol
        self.open = open
        self.intermediary = Intermediary.Intermediary(client = self.client,model = self.model, intent_history = intent_history, assessment_history = assessment_history) if intermediary is None else intermediary
        

    def get_response(self,messages_student,messages_tutor,max_tokens=1500):
        print("\n---")
        print("tutor called")
        prompt,intent,assessment = self.intermediary.get_prompt(self.pb,self.sol,messages_student,messages_tutor,open=self.open)
        #prompt.append({"role": "system", "content": "Ask the student to find by themself a problem with their answer without giving any hint"})
        print("prompt generated:")
        #print_logs(prompt)
        

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=prompt,
            max_tokens=max_tokens
        )
        response = completion.choices[0].message.content

        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens

        response = response.replace("\(","$").replace("\)","$").replace("\[","$$").replace("\]","$$")
        print("tutor answers:")
        print(response)
        print("---")
        return response, total_tokens, prompt_tokens, completion_tokens, intent, assessment
#!/usr/bin/env python3
import sys
from get_key import get_client
import itertools
import json

import Student,Tutor,Intermediary,IntentSelector,Assessor,PromptGenerator
from problems import create_msgs,get_pb_sol


def simulate(intermediary_code,n=15,topic='country',level='10th grade student',confusion="lost and unsure how to proceed. You have never done this kind of problem before",emotion=None,suffix="",pbopen=True):
    pb,sol = get_pb_sol(topic)
    client = get_client()
    eq_topic = {"pythagoras":"Z","country":"Y","consistency":"X"}
    str_topic = eq_topic[topic]
    eq = {1:"A",2:"B",3:"C",4:"D"}
    str_code = eq[intermediary_code]
    outfile = f"{str_code}{str_topic}{suffix}"#f"1{topic}_{level}_{confusion[:4]}_{emotion}{suffix}"
    student_model = "myGPT4"
    tutor_model = "myGPT4"
    

    messages_tutor = ["Hello! I am your tutor. Can you walk me through your solution?"]
    messages_student = []
    intent_history = []
    assessment_history = []
    
    
    if intermediary_code == 1:
        # flexible system
        intermediary = Intermediary.EmptyIntermediary(client=client,model=tutor_model, intent_history = intent_history, assessment_history = assessment_history)
    elif intermediary_code == 2:
        # full system
        intermediary = Intermediary.Intermediary(client=client,model=tutor_model, intent_history = intent_history, assessment_history = assessment_history)
    elif intermediary_code == 3:
        # baseline
        intermediary = Intermediary.NextStepIntermediary(client=client,model=tutor_model, intent_history = intent_history, assessment_history = assessment_history)
    else:
        # LLM chooses
        intermediary = Intermediary.LLMIntermediary(client=client,model=tutor_model, intent_history = intent_history, assessment_history = assessment_history)
    


    student = Student.Student(client=client, pb=pb, level = level, confusion = confusion, emotion = emotion, model = student_model)
    tutor = Tutor.Tutor(client=client, pb=pb,sol=sol, model = tutor_model, assessment_history=assessment_history,open=pbopen, intermediary=intermediary)
    cum_total_tokens = 0
    cum_cost = 0

    for turn in range(n):
        print("Turn: ", turn)
        student_response, student_total_tokens, student_prompt_tokens, student_completion_tokens = student.get_response(messages_student,messages_tutor,max_tokens=500)
        print("Student:", student_response)
        messages_student.append(student_response)
        lowercase = student_response.lower()
        if "goodbye" in lowercase or "bye" in lowercase or "see you" in lowercase or "see ya" in lowercase or lowercase == '':
            break
        tutor_response, tutor_total_tokens, tutor_prompt_tokens, tutor_completion_tokens, intent, assessment = tutor.get_response(messages_student,messages_tutor,max_tokens=500)
        print("Tutor:", tutor_response)
        messages_tutor.append(tutor_response)
        intent_history.append(intent)
        assessment_history.append(assessment)

        total_tokens = student_total_tokens + tutor_total_tokens
        cum_total_tokens += total_tokens

        # from https://openai.com/pricing#language-models
        cost = 0
        if student_model == "myGPT35":
            cost = student_total_tokens * 0.002 / 1000
        else:
            cost = (student_prompt_tokens * 0.03 + student_completion_tokens * 0.06) / 1000
        
        if tutor_model == "myGPT35":
            cost += tutor_total_tokens * 0.002 / 1000
        else:
            cost += (tutor_prompt_tokens * 0.03 + tutor_completion_tokens * 0.06) / 1000
        print("Cost: ", cost)
        cum_cost += cost

    print("\n")
    print("Cumulative cost: ", cum_cost)
    print(turn, " turns")
    for msg_t,msg_s in itertools.zip_longest(messages_tutor,messages_student):
        print("Tutor: ",msg_t)
        print("")
        print("Student: ",msg_s)

    combined_messages = \
    {
        "student": messages_student,
        "tutor": messages_tutor,
        "intents": [[intent.name for intent in intent_list] for intent_list in intent_history],
        "assessments": assessment_history,
        "total_cost": cum_cost,
        "pb": pb,
        "sol": sol
    }
    # Write to a JSON file
    with open(f'{outfile}.json', 'w') as f:
        json.dump(combined_messages, f,indent=4)

    return cum_cost

if __name__ == "__main__":
    cost = 0
    # 4 conditions: 1. Full flexible, 2. System, 3. Cst Intent, 4. LLM Intent Selector
    for intermediary_code in range(1,5):
        for testnb in range(0,3):
            for tpc,description,openended in [("consistency","10th grade student who has never heard of variance and standard deviation",True),("pythagoras","10th grade student",False),("country","10th grade student",True)]:
                cost+=simulate(intermediary_code,level=description,topic = tpc,suffix=f"{testnb+1}_BIS",n=13,pbopen=openended)
                print(f"Total cost so far: {cost}, {tpc}, {testnb}")
            
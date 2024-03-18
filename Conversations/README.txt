The generated conversations used for the human evaluation and strategy fidelity evaluation. `json` contains the conversations in a format readable by code and `pdf` contains the same conversation in format, displayed in the human evaluation form. 

The naming convention used is:

`{VERSION}{PROBLEM}{INSTANCE}.pdf`

With the following correspondence between {VERSION} and the names used in the thesis: 

A : "No Intent" (V2)
B : "Full System" (V1)
C : "Constant Intent Selector" (V3)
D : "LLM Intent Selector" (V4)

the following correspondence between {NAME} and the testing problems:

X : "Consistency"
Y : "Country"
Z : "Pythagoras"

For each verison and each problem, we generated three sample conversations numbered from 1 to 3 with {INSTANCE}.

The problem statements and their solution can be found on this GitHub repository.
The different conversations can also be loaded in the web-app. For this, refer to this repository's main README file.

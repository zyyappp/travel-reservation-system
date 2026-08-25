#module name  : selection_helper.py
#date created : 13th August 2026
#created by   : 
#imported     : InquirerPy
#amendment    :
#remark       : Selection, Searching, Checkbox UI

from InquirerPy import inquirer


def select(message, choices, height = 10): 

    prompt = inquirer.select(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()

    

def search(message, choices, height = 10): 

    prompt = inquirer.fuzzy(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()

def checkbox(message, choices, height=10):

    prompt = inquirer.checkbox(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()
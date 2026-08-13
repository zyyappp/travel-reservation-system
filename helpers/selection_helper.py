from InquirerPy import inquirer


def select(message, choices, height = 10): 

    prompt = inquirer.select(
            message=message,
            choices=choices,
            height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()

    

def search(message, choices, height = 10): 

    prompt = inquirer.fuzzy(
            message=message,
            choices=choices,
            height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()
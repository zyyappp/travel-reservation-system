from InquirerPy import inquirer


select = lambda message, choices, height = 10: inquirer.select(
            message=message,
            choices=choices,
            height=height
        ).execute()

search = lambda message, choices, height = 10: inquirer.fuzzy(
            message=message,
            choices=choices,
            height=height
        ).execute()
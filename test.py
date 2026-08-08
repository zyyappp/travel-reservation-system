import questionary

country = questionary.select(
    "Choose a country to visit:",
    choices=[
        questionary.Choice("North America", sep=True), # Visual separator
        "Canada",
        "Mexico",
        questionary.Choice("Europe", sep=True), # Visual separator
        "United Kingdom",
        "Germany",
        "France"
    ]
).ask()

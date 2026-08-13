from features.city import select_city

class User:
    def __init__(self, id, user, password):
        self.id = id
        self.user = user
        self.password = password
        self.city = select_city(id)

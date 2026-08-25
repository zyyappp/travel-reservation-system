from features.city import select_city

class User:
    def __init__(self, id, user, password, hotel, attractions, reservations):
        self.id = id
        self.user = user
        self.password = password
        self.city = select_city(id)
        self.hotel_filter = hotel
        self.attractions_filter = attractions
        self.reservations_filter = reservations

        

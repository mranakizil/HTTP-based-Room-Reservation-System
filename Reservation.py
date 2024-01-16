import json

class Reservation:
    def __init__(self, roomname, activityname, day, hour, duration):
        self.roomname = roomname
        self.activityname = activityname
        self.day = day
        self.hour = hour
        self.duration = duration
        self.reservation_id = None
        self.index = None


    def add_room_reservation(self, conn, room_index):
        reservation_info = {}
        reservation_info["day"] = self.day
        reservation_info["hour"] = self.calculate_hours()
        reservation_info["duration"] = self.duration

        with open("rooms.json",'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details

            if room_index != -1:
                file_data["rooms"][room_index]["reservation_info"].append(reservation_info)
                response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                response += b'<html><body>Reservation added.</body></html>'
                conn.send(response)
            else:
                response = b'HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n'
                response += b'<html><body>Reservation could not added. Room does not exist in the database.</body></html>'
                conn.send(response)
           
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
            # Send a successful response
           

    def add_activity_reservation(self, conn, activity_index):

        with open("activities.json",'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # if room does not exist, add the room to the database
            if activity_index == -1:
                file_data["activities"].append(self.activityname)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
            # Send a successful response
            response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += b'<html><body>activity Reservation added.</body></html>'
            conn.send(response)

    def add_reservation(self, conn, room_index, activity_index,  res_room_index, res_activity_index):
        reservation_info_list = []
        reservation_info = {}
        reservation_info["activity"] = self.activityname
        reservation_info["day"] = self.day
        reservation_info["hour"] = self.calculate_hours()
        reservation_info["duration"] = self.duration
        reservation_info_list.append(reservation_info)

        with open("reservations.json",'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
           
            # Join new_data with file_data inside emp_details
            if room_index == -1 or activity_index == -1:
                response = b'HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n'
                response += b'<html><body>Room or Activity does not exist.</body></html>'
                conn.send(response)
            else:
                if res_room_index != -1:
              
                    if self.roomname == file_data["reservations"][res_room_index]["room"] and self.day == file_data["reservations"][res_room_index]["reservation_info"][res_activity_index]["day"] and self.calculate_hours() == file_data["reservations"][res_room_index]["reservation_info"][res_activity_index]["hour"]:
                        # If the room is already reserved, send a Forbidden response
                        response = b'HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n'
                        response += b'<html><body>Room, day, and hours already reserved.</body></html>'
                        conn.send(response)
                else:
                    reservation_id = self.get_reservation_id()
                    file_data["reservation_ids"].append(reservation_id)
                    reservation_info["reservation_id"] = reservation_id
                    if res_room_index != -1:
                        file_data["reservations"][res_room_index]["reservation_info"].append(reservation_info_list)
                        response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                        response += b'<html><body>Reservation added.</body></html>'
                        conn.send(response)
                    else:
                        info_dict = {}
                        info_dict["room"] = self.roomname
                        info_dict["reservation_info"] = [reservation_info]
                        file_data["reservations"].append(info_dict)
                        response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                        response += b'<html><body>Reservation added.</body></html>'
                        conn.send(response)
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
          
            
    def calculate_hours(self):
        hours = []
        for i in range(0, self.duration):
            hours.append(self.hour + i)
        return hours

    def get_reservation_id(self):
        reservation_id = -1
        with open("reservations.json",'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            i = 1
            while True:
                if i not in file_data["reservation_ids"]:
                    reservation_id = i
                    break
                i = i + 1

            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent = 4)
          
        return reservation_id


    def setReservationId(self, reservation_id):
        self.reservation_id = reservation_id
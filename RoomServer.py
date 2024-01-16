import socket
import json

from Reservation import *
from Room import *

database_file = 'rooms.json'
class RoomServer:
    def __init__(self):
        self.rooms = []

    def fill_rooms_list(self):
        # Extract the value of the name query parameter
        # JSON file
        try:
            f = open (''.join(database_file), "r")
            # Reading from file
            data = json.loads(f.read())

            # Iterating through the json list
            for roomname in data['rooms']:
                self.rooms.append(roomname)
        except json.JSONDecodeError:
            # open the file in write mode
            with open(database_file, 'w') as file:
                # write the data to the file as JSON
                data = {"rooms": []}
                json.dump(data, file)
        # Check if the room already exists in the database

    def does_room_exist(self, name):
        room_index = -1
        for i in range (0, len(self.rooms)):
            if name == self.rooms[i]["name"]:
                room_index = i
                break
        return room_index

    def check_availability(self, conn, room_index, name, day):
        f = open (database_file, "r")
        data_json = json.loads(f.read())

        if room_index == -1:
            response = b'HTTP/1.1 404 Forbidden\nContent-Type: text/html\n\n'
            response += b'<html><body>Room not found.</body></html>'
            conn.send(response) 
        elif day not in ['1', '2', '3', '4', '5', '6', '7']:
            response = b'HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n'
            response += b'<html><body>Day is not valid.</body></html>'
            conn.send(response)
        else:
            unavailable_hours = []
            for i in range(0, len(data_json["rooms"])):
                compared_name = data_json["rooms"][i]["name"]
                for j in range(0, len(data_json["rooms"][i]["reservation_info"])): 
                    compared_day = data_json["rooms"][i]["reservation_info"][j]["day"]
                    
                    if compared_day == int(day) and compared_name == name:
                        unavailable_hours = data_json["rooms"][i]["reservation_info"][j]["hour"]
                        
            available_hours = []
           
            for i in range(9, 17):
                available_hours.append(i)
            for unavailable_hour in unavailable_hours:
                available_hours.remove(unavailable_hour)
            # Get the available hours for the specified room and day
            response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += b'<html><body>Reservation available. Available hours:</body></html>\n\n'
             # Convert the list to a string and add each element on a new line
            list_str = ', '.join(str(available_hour) for available_hour in available_hours)

            # Add the list string to the HTML
            response += list_str.encode('utf-8')

            response += b'</body></html>\n\n'
            conn.send(response)


    def list_availability(self, conn, name, room_index):
        f = open (database_file, "r")
        data_json = json.loads(f.read())

        if room_index == -1:
            response = b'HTTP/1.1 404 Forbidden\nContent-Type: text/html\n\n'
            response += b'<html><body>Room not found.</body></html>'
            conn.send(response) 
        else:

            days = []
            unavailable_hours = []
            for i in range(0, 7):
                days.append([])
           
                
            for i in range(0, len(data_json["rooms"])):
                compared_name = data_json["rooms"][i]["name"]
               
                for j in range(0, len(data_json["rooms"][i]["reservation_info"])):
                    day_index = data_json["rooms"][i]["reservation_info"][j]["day"]
                    unavailable_hours += data_json["rooms"][i]["reservation_info"][j]["hour"]
                if compared_name == name:
                    days[day_index - 1] = list(dict.fromkeys(unavailable_hours))
           # Get the available hours for the specified room and day
            response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
            response += b'<html><body>Reservation available. Available hours:<br>'
            days_dict = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
            all_available_hours = []
            for day_index in range(0, len(days)):
                available_hours = []
                for i in range(9, 17):
                    available_hours.append(i)
        
                for unavailable_hour in days[day_index]:
                    available_hours.remove(unavailable_hour)
                all_available_hours.append(available_hours)

            for i, available_hours in enumerate(all_available_hours):
                response += f'{days_dict[i + 1]}: {available_hours}<br>'.encode('utf-8')

            response += b'</body></html>\n\n'

            conn.send(response)
                        

    def main(self):
        # Set up the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8080))
        server_socket.listen()

        # Create the database file if it does not exist
        open(database_file, 'a').close()

        while True:
            # Accept incoming connections
            conn, addr = server_socket.accept()

            # Receive data from the client
            data = conn.recv(1024).decode("utf-8")

            # Parse the query parameters from the request
            request_lines = data.split("\n")
            request_line = request_lines[0]
            request_parts = request_line.split(" ")
            request_method = request_parts[0]
            request_uri = request_parts[1]
            query_parts = request_uri.split("?")

            if not request_uri == '/favicon.ico':
                query_string = query_parts[1]
                query_parameters = query_string.split("&")
                params = {}
                for param in query_parameters:
                    key, value = param.split("=")
                    params[key] = value

                name = params["name"]
                room = Room(name)
            
                roomServer = RoomServer()
                roomServer.fill_rooms_list()
                room.index =  roomServer.does_room_exist(name)
            
                if request_method == 'GET':
                
                    if request_uri.startswith('/add'):
                        if  room.index != -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n <html><body>Room already exists.</body></html>'
                            conn.send(response)
                        else:
                            room.add_room(conn, database_file)
                    elif request_uri.startswith('/remove'):
                        if  room.index == -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n <html><body>Room does not exist.</body></html>'
                            conn.send(response)
                        else:
                            f = open (database_file, "r")
                            data_json = json.loads(f.read())
                            room.remove_room(conn, data_json, room.index)
                    elif request_uri.startswith('/reserve'):
                        day = int(params["day"])
                        hour = int(params["hour"])
                        duration = int(params["duration"])
                        # Validate the input values
                        if day < 1 or day > 7 or hour < 9 or hour > 17 or duration < 1 or duration + hour > 17:
                            # If any of the values are invalid, send a Bad Request response
                            conn.send("HTTP/1.1 400 Bad Request\n\n".encode("utf-8"))
                            conn.close()
                            continue
                        # Check if the room is already reserved
                        reservation = Reservation(name, None, day, hour, duration)
                        is_room_reserved = False
                        if room.index != -1 and roomServer.rooms[room.index] != []:
                            for i in range(0, len(roomServer.rooms[room.index]["reservation_info"])):
                                if name == roomServer.rooms[room.index]["name"] and day == roomServer.rooms[room.index]["reservation_info"][i]["day"] and reservation.calculate_hours() == roomServer.rooms[room.index]["reservation_info"][i]["hour"]:
                                    # If the room is already reserved, send a Forbidden response
                                    is_room_reserved = True
                                    response = b'HTTP/1.1 403 Forbidden\nContent-Type: text/html\n\n'
                                    response += b'<html><body>Room already reserved.</body></html>'
                                    conn.send(response)
                                    
                        if not is_room_reserved:
                            if "name" in params and "day" in params and "hour" in params and "duration" in params:
                                day = int(params["day"])
                                hour = int(params["hour"])
                                duration = int(params["duration"])
                                room.setReservation(reservation)
                                room.reservation.add_room_reservation(conn, room.index)

                        elif "name" not in params or "day" not in params or "hour" not in params or "duration" not in params:
                            # If any of the required parameters are missing, send a Bad Request response
                            conn.send("HTTP/1.1 400 Bad Request\n\n".encode("utf-8"))
                            conn.close()
                            continue
                    elif request_uri.startswith('/checkavailability'):
                        name = params["name"]
                        day = params["day"]
                        roomServer.check_availability(conn, room.index, name, day)
                        # Send the response to the client
                        conn.close()

            

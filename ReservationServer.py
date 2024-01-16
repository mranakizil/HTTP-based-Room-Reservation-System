import socket
import json

from Reservation import *
from Room import *
from Activity import *
from ActivityServer import *
from RoomServer import *

database_file = 'reservations.json'
class ReservationServer:
    def __init__(self):
        self.reservations = []

    def fill_reservations_list(self):
        # Extract the value of the name query parameter
        try:
            f = open (''.join(database_file), "r")
            # Reading from file
            data = json.loads(f.read())

            # Iterating through the json list
            for reservationname in data['reservations']:
                self.reservations.append(reservationname)
        except json.JSONDecodeError:
            # open the file in write mode
            with open(database_file, 'w') as file:
                # write the data to the file as JSON
                data = {"reservation_ids": [], "reservations": []}
                json.dump(data, file)
        # Check if the room already exists in the database

    def does_reservation_exist(self, name):
        reservation_index = -1
        for i in range (0, len(self.reservations)):
            if name == self.reservations[i]["room"]:
                reservation_index = i
                break
        return reservation_index

    def get_room_index(self, name):
        room_index = -1
        for i in range (0, len(self.reservations)):
            if name == self.reservations[i]["room"]:
                room_index = i
                break
        return room_index

    def get_activity_index(self, activity):
        activity_index = -1
        for i in range (0, len(self.reservations)):
            for j in range (0, len(self.reservations[i]["reservation_info"])):
                if activity == self.reservations[i]["reservation_info"][j]["activity"]:
                    activity_index = j
                    break
        return activity_index
  

    def main(self):
        # Set up the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8082))
        server_socket.listen()

        roomServer = RoomServer()
        roomServer.fill_rooms_list()
    

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

                        
                if request_method == 'GET':
                
                    if request_uri.startswith('/reserve'):
                        roomname = params["room"]
                        room = Room(roomname)
                        room.index =  roomServer.does_room_exist(room.name)  
                        
                        activityname = params["activity"]
                        activity = Activity(activityname)
                    
                        reservationServer = ReservationServer()
                        reservationServer.fill_reservations_list()
                        reservation_index =  reservationServer.does_reservation_exist(roomname)
            
                        activityServer = ActivityServer()
                        activityServer.fill_activities_list()


                        day = int(params["day"])
                        hour = int(params["hour"])
                        duration = int(params["duration"])

                        if activityServer.does_activity_exist(activity.name) == -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n<html><body>Activity does not exist.</body></html>'
                            conn.send(response)
                        
                        activity.index = activityServer.does_activity_exist(activity.name)

                        if roomServer.does_room_exist(room.name) == -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n <html><body>Room does not exist.</body></html>'
                            conn.send(response)
                        

                        # Validate the input values
                        if day < 1 or day > 7 or hour < 9 or hour > 17 or duration < 1 or duration + hour > 17:
                            # If any of the values are invalid, send a Bad Request response
                            response = b'HTTP/1.1 400 Bad Request\n\Content-Type: text/html\n\n'
                            response += b'<html><body>Any of the values are invalid.</body></html>'
                            conn.send(response)
                            conn.close()
                            continue                                                         
                                
                        if "room" in params and "activity" in params and "day" in params and "hour" in params and "duration" in params:
                            day = int(params["day"])
                            hour = int(params["hour"])
                            duration = int(params["duration"])
                            reservation = Reservation(room.name, activity.name, day, hour, duration)
                            room.setReservation(reservation)
                            # reservation.add_room_reservation(conn, room.index)
                            # reservation.add_activity_reservation(conn, activity.index)
                            reservation.index = reservation_index
                            reservation.add_reservation(conn, room.index, activity.index, reservationServer.get_room_index(room.name), reservationServer.get_activity_index(activity.name))

                        elif "room" not in params or "activity" not in params or "day" not in params or "hour" not in params or "duration" not in params:
                            # If any of the required parameters are missing, send a Bad Request response
                            response = b'HTTP/1.1 400 Bad Request\n\Content-Type: text/html\n\n'
                            response += b'<html><body>Required parameters are missing.</body></html>'
                            conn.send(response)
                            conn.close()
                            continue
                    elif request_uri.startswith('/listavailability'):
                        roomname = params["room"]
                        room = Room(roomname)
                        room.index =  roomServer.does_room_exist(room.name)  
                        
                        if len(params) == 1:
                            roomname = params["room"]
                            room = Room(roomname)
                            roomServer.list_availability(conn, roomname, room.index)
                        elif len(params) == 2:
                            day = params["day"]
                            roomname = params["room"]
                            room = Room(roomname)
                            roomServer.check_availability(conn, room.index, roomname, day)
                            # Send the response to the client
                            response = b'HTTP/1.1 200 OK\n\Content-Type: text/html\n\n'
                            # response += b'<html><body>All available day and hours: .</body></html>'
                            conn.send(response)
                            conn.close()
                        else:
                            print("error")   

                    elif request_uri.startswith('/display'):                          
                        reservation_id = int(params["id"])

                        with open("reservations.json",'r+') as file:
                            # First we load existing data into a dict.
                            file_data = json.load(file)

                            if reservation_id in file_data["reservation_ids"]:
                                for i in range (0, len(file_data["reservation_ids"])):
                                    if reservation_id == file_data["reservations"][i]["reservation_info"][0]["reservation_id"]:
                                        # print(file_data["reservations"][i])
                                        # Send the response to the client
                                        response = b'HTTP/1.1 200 OK\n\Content-Type: text/html\n\n'

                                        # Get the reservation info
                                        response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                                        response += b'<html><body>Reservation id found. Reservation info:<br>'
                                        response += f'{file_data["reservations"][i]}<br>'.encode('utf-8')
                                        response += b'</body></html>\n\n'
                                        conn.send(response)
                            else:
                                response = b'HTTP/1.1 404 Not Found\n\Content-Type: text/html\n\n'
                                response += b'<html><body>Reservation id not found.</body></html>'
                                conn.send(response)
                                conn.close()
                                                   
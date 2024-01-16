import socket
import json

from Activity import *

database_file = 'activities.json'

class ActivityServer:
    def __init__(self):
        self.activities = []

    def fill_activities_list(self):
        try: 
            # Extract the value of the name query parameter
            # JSON file
            f = open (''.join(database_file), "r")
            # Reading from file
            data = json.loads(f.read())

            # Iterating through the json list
            for activityname in data['activities']:
                self.activities.append(activityname)
        except json.JSONDecodeError:
            # open the file in write mode
            with open(database_file, 'w') as file:
                # write the data to the file as JSON
                data = {"activities": []}
                json.dump(data, file)

    def does_activity_exist(self, name):
        activity_index = -1
        for i in range (0, len(self.activities)):
            if name == self.activities[i].get('name'):
                activity_index = i
                break
        return activity_index

        

    def main(self):
        # Set up the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8081))
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
                activity = Activity(name)
            
                activityServer = ActivityServer()
                activityServer.fill_activities_list()
                activity.index =  activityServer.does_activity_exist(name)
            
                if request_method == 'GET':
                
                    if request_uri.startswith('/add'):
                        if activity.index != -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n <html><body>Activity already exists.</body></html>'
                            conn.send(response)
                        else:
                            activity.add_activity(conn, database_file)
                    elif request_uri.startswith('/remove'):
                        if activity.index == -1:
                            # Return a 403 Forbidden response
                            response = b'HTTP/1.1 403 Forbidden\n\n <html><body>Activity does not exist.</body></html>'
                            conn.send(response)
                        else:
                            f = open (database_file, "r")
                            data_json = json.loads(f.read())
                            activity.remove_activity(conn, data_json, activity.index)
                    elif request_uri.startswith('/check'):
                        if activity.index == -1:
                            response = b'HTTP/1.1 404 Forbidden\nContent-Type: text/html\n\n'
                            response += b'<html><body>Activity not found.</body></html>'
                            conn.send(response)
                            continue
                        else:
                            response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
                            response += b'<html><body>Activity exists.</body></html>\n\n'
                            conn.send(response)
                        # Send the response to the client
                        conn.close()

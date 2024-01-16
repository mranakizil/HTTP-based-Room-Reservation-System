
import json

from Reservation import *

class Room:
  def __init__(self, name):
    self.name = name
    self.reservation = None
    self.index = None


  def add_room(self, conn, database_file):
    with open(database_file,'r+') as file:
      # First we load existing data into a dict.
      try:
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        info_dict = {}
        info_dict["name"] = self.name
        info_dict["reservation_info"] =  []
        file_data["rooms"].append(info_dict)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
        # Return a 200 OK response with an HTML body
        response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
        response += b'<html><body>Room added</body></html>'
        conn.send(response)
      except json.JSONDecodeError:
            pass


  def remove_room(self, conn, data, room_index):
    # Delete the element at index 1
    del data["rooms"][room_index]

    # Open the file in write mode
    with open('rooms.json', 'w') as f:
    # Use the json.dump() function to write the modified data back to the file
        json.dump(data, f, indent = 4)

    # Return a 200 OK response with an HTML body
    response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
    response += b'<html><body>Room removed</body></html>'
    conn.send(response)


  def setReservation(self, reservation):
    self.reservation = reservation



 
        
    



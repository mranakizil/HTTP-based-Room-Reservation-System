import json

class Activity:
  def __init__(self, name):
    self.name = name
    self.index = []


  def add_activity(self, conn, database_file):
    with open(database_file,'r+') as file:
      # First we load existing data into a dict.
      file_data = json.load(file)
      # Join new_data with file_data inside emp_details
      name_dict = {"name": self.name}
      file_data["activities"].append(name_dict)
      # Sets file's current position at offset.
      file.seek(0)
      # convert back to json.
      json.dump(file_data, file, indent = 4)
      # Return a 200 OK response with an HTML body
      response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
      response += b'<html><body>Activity added</body></html>'
      conn.send(response)


  def remove_activity(self, conn, data, activity_index):
    # Delete the element at index 1
    del data["activities"][activity_index]

    # Open the file in write mode
    with open('activities.json', 'w') as f:
    # Use the json.dump() function to write the modified data back to the file
        json.dump(data, f, indent = 4)

    # Return a 200 OK response with an HTML body
    response = b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'
    response += b'<html><body>Activity removed</body></html>'
    conn.send(response)

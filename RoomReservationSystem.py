"""
CSE4074 Computer Networks Programming Assignment
SOCKET PROGRAMMING HTTP - based Room Reservation

150119825 - Merve Rana Kizil
150517059 - Özge Saltan
"""

import threading
from RoomServer import *
from ActivityServer import *
from ReservationServer import *

def run_room_server():
    roomServer = RoomServer()
    roomServer.main()

def run_activity_server():
    activityServer = ActivityServer()
    activityServer.main()

def run_reservation_server():
    reservationServer = ReservationServer()
    reservationServer.main()

# Create and start a thread for each main method
thread1 = threading.Thread(target=run_room_server)
thread2 = threading.Thread(target=run_activity_server)
thread3 = threading.Thread(target=run_reservation_server)

thread1.start()
thread2.start()
thread3.start()

# Wait for all threads to finish
thread1.join()
thread2.join()
thread3.join()

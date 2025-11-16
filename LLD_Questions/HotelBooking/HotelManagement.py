from HotelBookingSystem import Guest, Reservation, Room
from threading import Lock
from typing import Dict, Optional
from datetime import date

class HotelManagement:
    _instance=None

    def __new__(cls):
        if cls._instance is None:
            cls._instance=super().__new__(cls)
            cls._instance.guests : Dict[str, Guest]={}
            cls._instance.rooms : Dict[str, Room]={}
            cls._instance.reservations : Dict[str,Reservation]={}
            cls._instance.lock=Lock()
        return cls._instance
    
    def add_guests(self, guest:Guest):
        self.guests[guest.get_id()]=guest

    def get_guest(self, id)->Optional[Guest]:
        return self.guests.get(id);

    def add_rooms(self, room:Room):
        self.rooms[room.get_room_number()]=room
    
    def get_room(self, room:int):
        return self.rooms[room]
    
    def book_room(self, guest:Guest, room:Room, checkin:date, checkout:date, payment:int)->str:
        with self.lock:
            reservation=Reservation(guest, room, checkin, checkout, payment)
            id=reservation.get_id()
            if(reservation.reserve()):
                print(f"Room no {room.get_room_number()} has been booked")
                self.reservations[id]=reservation
                return id
            else:
                print("Room unavailable")
                return None
    
    def cancel_reservation(self, guest:Guest,reservation_id:str):
        with self.lock:
            reservation=self.reservations.get(reservation_id)
            if reservation and reservation.cancel(guest):
                print("Reservation cancelled")
                del self.reservations[reservation_id]
            else:
                print("Not your booking")

    def check_in(self, reservation_id:str):
        with self.lock:
            reservation=self.reservations.get(reservation_id)
            if reservation:
                if reservation.get_room().checkin():
                    print(f"{reservation.get_guest().get_name()} Checked in room no {reservation.get_room().get_room_number()}")
            else:
                print("No reservation found")
    
    def check_out(self, reservation_id:str):
        with self.lock:
            reservation=self.reservations.get(reservation_id)
            if reservation:
                if reservation.get_room().checkout():
                    print(f"{reservation.get_guest().get_name()} Checked out room of {reservation.get_room().get_room_number()}")
            else:
                print("No reservation found")



    
    
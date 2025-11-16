from HotelManagement import HotelManagement
from HotelBookingSystem import Guest, Room, RoomType
from datetime import date

class HotelManagementDemo:
    @staticmethod
    def run():
        hotel_management_system = HotelManagement()

        # Create guests
        guest1 = Guest("John Doe", "1234567890", "john@example.com")
        guest2 = Guest("Jane Smith", "9876543210", "jane@example.com")
        hotel_management_system.add_guests(guest1)
        hotel_management_system.add_guests(guest2)

        # Create rooms
        room1 = Room(RoomType.single, "R001", 100.0)
        room2 = Room(RoomType.double, "R002", 200.0)
        hotel_management_system.add_rooms(room1)
        hotel_management_system.add_rooms(room2)

        # Book a room
        check_in_date = date.today()
        check_out_date = check_in_date.replace(day=check_in_date.day + 3)
        reservation1 = hotel_management_system.book_room(guest1, room1, check_in_date, check_out_date, 1)
        # if reservation1:
        #     print(f"Reservation created: {reservation1.id}")
        # else:
        #     print("Room not available for booking.")

        reservation2 = hotel_management_system.book_room(guest2, room2, check_in_date, check_out_date, 1)
        # if reservation2:
        #     print(f"Reservation created: {reservation2.id}")
        # else:
        #     print("Room not available for booking.")

         # Check-in
        hotel_management_system.check_in(reservation1)
        # print(f"Checked in: {reservation1.id}")

        # Check-out and process payment
        hotel_management_system.check_out(reservation1)
        # print(f"Checked out: {reservation1.id}")

        # Cancel a reservation
        hotel_management_system.cancel_reservation(reservation2, guest2)
        # hotel_management_system.cancel_reservation(reservation1, guest1)

        # print(f"Reservation cancelled: {reservation1.id}")

if __name__=='__main__':
    HotelManagementDemo.run()



    
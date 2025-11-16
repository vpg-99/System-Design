from enum import Enum as Enum
import uuid
from abc import ABC, abstractmethod
from threading import Lock
from datetime import date


class RoomType(Enum):
    single="SINGLE"
    double="DOUBLE"
    suite="SUITE"
    deluxe="DELUXE"

class RoomStatus(Enum):
    available="AVAILABLE"
    booked="BOOKED"
    occupied="OCCUPIED"

class ReservationStatus(Enum):
    confirmed="CONFIRMED"
    cancelled="CANCELLED"


class Guest:
    def __init__(self, name:str, phone:str, email:str):
        self.id=str(uuid.uuid4())
        self.name=name
        self.phone=phone
        self.email=email
    
    def get_id(self)->str:
        return self.id
    
    def get_name(self)->str:
        return self.name
    
    def get_phone(self)->str:
        return self.phone
    
    def get_address(self)->str:
        return self.address

class Room:
    def __init__(self, type:RoomType, number:int, price:float):
        self.number=number
        self.type=type
        self.status=RoomStatus.available
        self.price=price
        self.lock=Lock()

    def book(self)->bool:
        with self.lock:
            if self.status==RoomStatus.available:
                self.status=RoomStatus.booked
                return True
            return False

    def checkin(self)->bool:
        with self.lock:
            if self.status == RoomStatus.booked:
                self.status=RoomStatus.occupied
                return True
            return False

    def checkout(self)->bool:
        with self.lock:
            if self.status==RoomStatus.occupied:
                self.status=RoomStatus.available
                return True
            return False

    def get_type(self)->RoomType:
        return self.type

    def get_status(self)->RoomStatus:
        return self.status
    
    def get_room_number(self)->int:
        return self.number
    
    def get_price(self)->float:
        return self.price

class Reservation:
    def __init__(self, guest:Guest, room:Room, checkin:date, checkout:date, payment:int):
        self.id=str(uuid.uuid4())
        self.guest=guest
        self.room=room
        self.checkin=checkin
        self.checkout=checkout
        self.status=ReservationStatus.confirmed
        self.payment_manager=PaymentManager()
        self.payment_type=payment
        self.lock=Lock()

    def get_id(self)->str:
        return self.id
    
    def get_room(self)->Room:
        return self.room
    
    def get_guest(self)->Guest:
        return self.guest
    
    def reserve(self)->bool:
        with self.lock:
            if self.room.get_status()==RoomStatus.available:
                if(self.room.book()):
                    if PaymentManager().pay(self.payment_type, ((self.checkout-self.checkin).days)*self.room.get_price()):
                        return True
            return False

    def cancel(self, guest:Guest)->bool:
        with self.lock:
            if  self.guest.get_id()==guest.get_id():
                if self.status==ReservationStatus.confirmed:
                    self.status=ReservationStatus.cancelled
                    self.room.checkout()
                    return True
            return False

# Strategy patterm 
class Payment(ABC):
    @abstractmethod
    def pay(self, price:float)->bool:
        pass

class PaymentManager:
    def __init__(self):
        self.paymentMethods=[CreditCardPayment(), UPIPayment(), CashPayment()]

    def pay(self, id:int, price:float)->bool:
        if id>=0 and id<len(self.paymentMethods):
            method=self.paymentMethods[id]
            return method.pay(price)
        return False
            
# Payment type -1 Concrete class
class CreditCardPayment:
    def pay(self, price:float)->bool:
        if price>0:
            print(f"Payment of {price} completed by CreditCard")
            return True
        return False

# Payment type -2 Concrete class
class UPIPayment:
    def pay(self, price:float)->bool:
        if price>0:
            print(f"Payment of {price} completed by UPI")
            return True
        return False
# Payment type -3 Concrete class
class CashPayment:
    def pay(self, price:float)->bool:
        if price>0:
            print(f"Payment of {price} completed by Cash")
            return True
        return False
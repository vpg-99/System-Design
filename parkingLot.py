"""Parking Lot Management System
This module provides classes and methods to manage a parking lot with multiple floors,
different vehicle types, and parking strategies.
"""
"""
Entities: ParkingSpot: the smallest entity, spot where the vehicle is parked. Has spot id, vehicle type, isParked
         ParkingFloor: each floor has multiple parking spots, 2D array of parking spots. Has methods to park, remove vehicle, get free spots count
         ParkingManager: manages parking strategies, has methods to park vehicle using different strategies
         SearchManager: manages search functionality, has methods to index and search vehicles
         Solution: main class that uses ParkingManager and SearchManager to provide parking lot functionalities

         Strategy Pattern for parking strategies:
            ParkingStrategy: interface for parking strategies
            NearestParkingStrategy: parks vehicle in the nearest available spot
            MostFreeSpotsParkingStrategy: parks vehicle in the floor with most free spots
            ParkingManager: manages parking strategies, has methods to park vehicle using different strategies
"""



"""
Interface for parking strategies
"""
class ParkingStrategy:
    def park(self, floors:list['ParkingFloor'], vehicle_type:int)->str:
        pass

class Solution:
    def init(self, helper, parking: list[list[list[int]]]):
        """
        Initialize the parking lot with the given helper and parking structure.
        """
        self.vehicle_types = [2, 4]
        self.helper = helper
        self.park_manager = ParkingManager()
        self.search_manager = SearchManager()
        # helper.println(f"going to initialize floors {len(parking)}")
        self.floors = [ParkingFloor(i, parking[i], self.vehicle_types, helper) for i in range(len(parking))]

    def park_vehicle(self, vehicle_type:int, vechicle_number:str,ticket_id:str,parking_strategy:int)->str:
        spot_id=self.park_manager.park(self.floors, vehicle_type, parking_strategy)
        if spot_id!="":
            self.search_manager.index(vechicle_number, ticket_id, spot_id)
        return spot_id
    
    def remove_vehicle(self, spot_id:str)->int:
        floor, row, col=map(int, spot_id.split("-"))
        return self.floors[floor].remove(row, col)
    
    def get_free_spots_count(self, floor:int,vehicle_type:int)->int:
        return self.floors[floor].get_free_spots_count(vehicle_type)

    def search_vehicle(self, query:str)->str:
        return self.search_manager.search(query)

class SearchManager:
    def __init__(self):
        self.cache={}
    
    def search(self, query)->str:
        return self.cache.get(query,"")
    
    def index(self, vehicle_number:str, ticket_id:str, spot_id:str)->None:
        self.cache[ticket_id]=spot_id
        self.cache[vehicle_number]=spot_id


class ParkingFloor:
    def __init__(self, floor:int, parking_floor:list[list[int]], vehicle_types:list[int]):
        """
        Initialize a parking floor.

        :param floor: Floor number
        :param parking_floor: 2D list representing parking spots on the floor
        :param vehicle_types: List of vehicle types that can be parked on this floor
        """
        self.parking_spots=[[None for _ in range(len(parking_floor[0]))] for _ in range(len(parking_floor ))]
        self.free_spots_count={vehicle_type:0 for vehicle_type in vehicle_types}

        for row in range(len(parking_floor)):
            for col in range(len(parking_floor[0])):
                if parking_floor[row][col]!=0:
                    vehicle_type=parking_floor[row][col]
                    spot_id=f"{floor}-{row}-{col}"
                    self.parking_spots[row][col]=ParkingSpot(spot_id, vehicle_type)
                    self.free_spots_count[vehicle_type]+=1
        
        def get_free_spots_count(self, vehicle_type:int)->int:
            return self.free_spots_count.get(vehicle_type, 0)
        
        def park(self, vehicle_type:int)->str:
            if self.free_spots_count.get(vehicle_type,0)==0:
                return ""
            for row in self.parking_spots:
                for spot in row:
                    if spot and spot.get_vehicle_type()==vehicle_type and not spot.is_parked():
                        spot.park_vehicle()
                        self.free_spots_count[vehicle_type]-=1
                        return spot.get_spot_id()
            return ""
        
        def remove(self, row:int, col:int)->bool:
            if row<0 or row>parking_floor.len() or col<0 or col>=parking_floor[0].len() or self.parking_spots[row][col].is_parked()==False:
                return False
            spot=self.parking_spots[row][col]
            spot.remove_vehicle()
            self.free_spots_count[spot.get_vehicle_type()]+=1
            return True

class ParkingSpot:
    def __init__(self, spot_it:str, vehicle_type:int):
        """
        Initialize a parking spot.

        :param spot_id: Spot ID. floor-row-column
        :param vehicle_type: Type of the vehicle 2 or 4 wheeler
        """
        self.spot_id=spot_it
        self.vehicle_type=vehicle_type
        self.is_spot_parked=False
        
    def is_parked(self)->bool:
        return self.is_spot_parked
    
    def park_vehicle(self)->None:
        self.is_spot_parked=True

    def remove_vehicle(self)->None:
        self.is_spot_parked=False
    
    def get_spot_id(self)->str:
        return self.spot_id
    
    def get_vehicle_type(self)->int:
        return self.vehicle_type
    
"""
Manages and implements parking strategies
"""
class ParkingManager:
    def __init__(self):
        """
        Initialize the park manager with parking strategies.
        """
        self.algorithms = [NearestParkingStrategy(), MostFreeSpotsParkingStrategy()]

    def park(self, floors: list, vehicle_type: int, parking_strategy: int) -> str:
        """
        Park a vehicle using the specified strategy.
        
        Args:
            floors (List[ParkingFloor]): The list of parking floors.
            vehicle_type (int): The vehicle type.
            parking_strategy (int): The parking strategy to use.

        Returns:
            str: The spot ID where the vehicle is parked.
        """
        if 0 <= parking_strategy < len(self.algorithms):
            strategy = self.algorithms[parking_strategy]
            return strategy.park(floors, vehicle_type)
        return ""
    
"""Strategy 1
"""
class NearestParkingStrategy(ParkingStrategy):
    def park(self, floors:list['ParkingFloor'], vehicle_type:int)->str:
        for floor in floors:
            spot_id=floor.park(vehicle_type)
            if spot_id!="":
                return spot_id
        return ""
    
"""
Strategy 2
"""
class MostFreeSpotsParkingStrategy(ParkingStrategy):
    def park(self, floors:list['ParkingFloor'], vehicle_type:int)->str:
        max_free_spots=-1
        selected_floor=None
        for floor in floors:
            free_spots_count=floor.get_free_spots_count(vehicle_type)
            if free_spots_count>max_free_spots:
                max_free_spots=free_spots_count
                selected_floor=floor
        if selected_floor:
            spot_id=selected_floor.park(vehicle_type)
            if spot_id!="":
                return spot_id
        return ""

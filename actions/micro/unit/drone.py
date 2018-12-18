"""Everything related to scouting with drones goes here"""


class Drone:
    """Ok for now, maybe can be replaced later for zerglings"""

    def __init__(self, main):
        self.controller = main
        self.drones = None
        self.rush_scout = False

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.drones = local_controller.drones
        return self.drones and local_controller.iteration % 2000 == 75 and not local_controller.close_enemy_production

    async def handle(self):
        """It sends 2 drone to scout the map, for rushes or proxies"""
        local_controller = self.controller
        drones = local_controller.drones
        scout = drones.closest_to(local_controller.start_location)
        expansion_locations = local_controller.ordered_expansions
        for point in expansion_locations[2:]:
            local_controller.add_action(scout.move(point, queue=True))
        if not self.rush_scout:
            self.rush_scout = True
            local_controller.add_action(drones.random.move(expansion_locations[-1], queue=True))

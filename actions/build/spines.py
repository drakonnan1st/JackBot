"""Everything related to building logic for the spines goes here"""
from sc2.constants import SPINECRAWLER


class BuildSpines:
    """New placement untested"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        return (
            local_controller.building_requirement(SPINECRAWLER, local_controller.pools.ready)
            and local_controller.townhalls
            and local_controller.close_enemy_production
            and len(local_controller.spines) < 4
            and local_controller.already_pending(SPINECRAWLER) < 2
        )

    async def handle(self):
        """Build the spines on the first base near the ramp in case there is a proxy"""
        local_controller = self.controller
        await local_controller.build(
            SPINECRAWLER,
            near=local_controller.furthest_townhall_to_map_center.position.towards(
                local_controller.main_base_ramp.depot_in_middle, 14
            ),
        )
        return True

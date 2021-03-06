"""Everything related to building logic for the pools goes here"""
from sc2.constants import SPAWNINGPOOL


class BuildPool:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Should this action be handled"""
        local_controller = self.controller
        return local_controller.can_build_unique(SPAWNINGPOOL, local_controller.pools) and (
            len(local_controller.townhalls) >= 2
            or local_controller.close_enemy_production
            or local_controller.time > 145
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(SPAWNINGPOOL, position)
            return True
        if local_controller.townhalls:
            await local_controller.build(SPAWNINGPOOL, near=self.hardcoded_position())
            return True

    def hardcoded_position(self):
        """Previous placement"""
        local_controller = self.controller
        return local_controller.furthest_townhall_to_map_center.position.towards_with_random_angle(
            local_controller.game_info.map_center, -10
        )

"""Everything related to building logic for the hydralisk den goes here"""
from sc2.constants import HYDRALISKDEN


class BuildHydraden:
    """Ok for now"""

    def __init__(self, ai):
        self.controller = ai

    async def should_handle(self):
        """Build the hydraden"""
        local_controller = self.controller
        return (
            local_controller.can_build_unique(HYDRALISKDEN, local_controller.hydradens, local_controller.lairs)
            and not local_controller.close_enemy_production
            and not local_controller.floating_buildings_bm
            and len(local_controller.townhalls) >= 3
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not places it near a pool"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(HYDRALISKDEN, position)
            return True
        await local_controller.build(HYDRALISKDEN, near=local_controller.pools.first)
        return True
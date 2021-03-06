"""Upgrading zergling speed"""
from sc2.constants import RESEARCH_ZERGLINGMETABOLICBOOST, ZERGLINGMOVEMENTSPEED


class UpgradeMetabolicBoost:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_pools = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_pools = local_controller.pools.ready.idle
        return local_controller.can_upgrade(ZERGLINGMOVEMENTSPEED, RESEARCH_ZERGLINGMETABOLICBOOST, self.selected_pools)

    async def handle(self):
        """Execute the action of upgrading zergling speed"""
        self.controller.add_action(self.selected_pools.first(RESEARCH_ZERGLINGMETABOLICBOOST))
        return True

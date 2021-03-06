"""Upgrading zerglings atk speed"""
from sc2.constants import RESEARCH_ZERGLINGADRENALGLANDS, ZERGLINGATTACKSPEED


class UpgradeAdrenalGlands:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_pools = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_pools = local_controller.pools.ready.idle
        return (
            local_controller.can_upgrade(ZERGLINGATTACKSPEED, RESEARCH_ZERGLINGADRENALGLANDS, self.selected_pools)
            and local_controller.hives
        )

    async def handle(self):
        """Execute the action of upgrading zergling atk speed"""
        self.controller.add_action(self.selected_pools.first(RESEARCH_ZERGLINGADRENALGLANDS))
        return True

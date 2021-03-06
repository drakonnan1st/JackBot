"""Upgrading hydras atk speed"""
from sc2.constants import EVOLVEGROOVEDSPINES, RESEARCH_GROOVEDSPINES


class UpgradeGroovedSpines:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_dens = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_dens = local_controller.hydradens.ready.noqueue.idle
        return (
            local_controller.can_upgrade(EVOLVEGROOVEDSPINES, RESEARCH_GROOVEDSPINES, self.selected_dens)
            and not local_controller.floating_buildings_bm
        )

    async def handle(self):
        """Execute the action of upgrading hydras atk speed"""
        self.controller.add_action(self.selected_dens.first(RESEARCH_GROOVEDSPINES))
        return True

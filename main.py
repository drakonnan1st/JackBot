"""SC2 zerg bot by JackBot team(Helfull, Matuiss, Niknoc) with huge help of Thommath, Tweakimp and Burny"""
import sc2
from sc2.constants import HATCHERY
from sc2.position import Point2
from actions.anti_cheese.defend_proxies import DefendProxies
from actions.anti_cheese.defend_worker_rush import DefendWorkerRush
from actions.build.cavern import BuildCavern
from actions.build.creep_spread import CreepControl
from actions.build.creep_tumor import CreepTumor
from actions.build.evochamber import BuildEvochamber
from actions.build.expansion import BuildExpansion
from actions.build.extractor import BuildExtractor
from actions.build.hive import BuildHive
from actions.build.hydraden import BuildHydraden
from actions.build.lair import BuildLair
from actions.build.pit import BuildPit
from actions.build.pool import BuildPool
from actions.build.spines import BuildSpines
from actions.build.spire import BuildSpire
from actions.build.spores import BuildSpores
from actions.macro.building_positioning import BuildingPositioning
from actions.macro.cancel_building import Buildings
from actions.macro.distribute_workers import DistributeWorkers
from actions.micro.block_expansions import BlockExpansions
from actions.micro.micro_main import ArmyControl
from actions.micro.unit.drone import Drone
from actions.micro.unit.overlord import Overlord
from actions.micro.unit.overseer import Overseer
from actions.micro.unit.queen import QueensAbilities
from actions.train.hydras import TrainHydralisk
from actions.train.mutalisk import TrainMutalisk
from actions.train.overlord import TrainOverlord
from actions.train.overseer import TrainOverseer
from actions.train.queen import TrainQueen
from actions.train.ultralisk import TrainUltralisk
from actions.train.worker import TrainWorker
from actions.train.zergling import TrainZergling
from actions.upgrades.adrenalglands import UpgradeAdrenalGlands
from actions.upgrades.burrow import UpgradeBurrow
from actions.upgrades.chitinous_plating import UpgradeChitinousPlating
from actions.upgrades.evochamber import UpgradeEvochamber

# from actions.upgrades.pneumatized_carapace import UpgradePneumatizedCarapace
from actions.upgrades.hydra_atk_speed import UpgradeGroovedSpines
from actions.upgrades.hydra_speed import UpgradeMuscularAugments
from actions.upgrades.metabolicboost import UpgradeMetabolicBoost
from actions.upgrades.anabolic_synthesis import UpgradeUltraliskSpeed
from data_container import DataContainer


# noinspection PyMissingConstructor
class JackBot(sc2.BotAI, DataContainer, CreepControl, BuildingPositioning, BlockExpansions):
    """It makes periodic attacks with good surrounding and targeting micro, it goes hydras mid-game
     and ultras end-game"""

    def __init__(self, debug=False):
        CreepControl.__init__(self)
        DataContainer.__init__(self)
        self.debug = debug
        self.iteration = self.add_action = None
        self.unit_commands = (
            BlockExpansions(self),
            DefendWorkerRush(self),
            DefendProxies(self),
            DistributeWorkers(self),
            ArmyControl(self),
            QueensAbilities(self),
            CreepTumor(self),
            Drone(self),
            Overseer(self),
            Overlord(self),
            Buildings(self),
        )
        self.train_commands = (
            TrainOverlord(self),
            TrainWorker(self),
            TrainQueen(self),
            TrainUltralisk(self),
            TrainZergling(self),
            TrainOverseer(self),
            TrainMutalisk(self),
            TrainHydralisk(self),
        )
        self.build_commands = (
            BuildPool(self),
            BuildExpansion(self),
            BuildExtractor(self),
            BuildEvochamber(self),
            BuildCavern(self),
            BuildPit(self),
            BuildHive(self),
            BuildLair(self),
            BuildSpines(self),
            BuildSpores(self),
            BuildSpire(self),
            BuildHydraden(self),
        )
        self.upgrade_commands = (
            UpgradeChitinousPlating(self),
            UpgradeMetabolicBoost(self),
            UpgradeAdrenalGlands(self),
            UpgradeEvochamber(self),
            # UpgradePneumatizedCarapace(self),
            UpgradeBurrow(self),
            UpgradeGroovedSpines(self),
            UpgradeMuscularAugments(self),
            UpgradeUltraliskSpeed(self),
        )
        self.ordered_expansions, self.building_positions, self.locations, self.actions = [], [], [], []

    def set_game_step(self):
        """It sets the interval of frames that it will take to make the actions, depending of the game situation"""
        if self.ground_enemies:
            if len(self.ground_enemies) >= 15:
                self.client.game_step = 2
            elif len(self.ground_enemies) >= 5:
                self.client.game_step = 4
            else:
                self.client.game_step = 6
        else:
            self.client.game_step = 8

    async def on_unit_created(self, unit):
        """Prepares all the building locations near a new expansion"""
        if unit.type_id is HATCHERY:
            await self.prepare_building_positions(unit)

    async def on_step(self, iteration):
        """Calls used units here, so it just calls it once per loop"""
        self.iteration = iteration
        self.prepare_data()
        self.set_game_step()
        self.actions = []
        self.add_action = self.actions.append
        if not iteration:
            self.locations = list(self.expansion_locations.keys())
            self.prepare_expansions()
            self.split_workers()
        await self.run_commands(self.unit_commands)
        await self.run_commands(self.train_commands)
        await self.run_commands(self.build_commands)
        await self.run_commands(self.upgrade_commands)
        if self.actions:
            if self.debug:
                print(self.actions)
            await self.do_actions(self.actions)

    async def run_commands(self, commands):
        """Group all requirements and execution for a class logic"""
        for command in commands:
            if await command.should_handle():
                if self.debug:
                    print(f"Handling: {command.__class__}")
                await command.handle()

    def can_train(self, unit_type, requirement=True, larva=True):
        """Global requirements for creating an unit"""
        return (not larva or self.larvae) and self.can_afford(unit_type) and self.can_feed(unit_type) and requirement

    def building_requirement(self, unit_type, requirement=True):
        """Global requirements for building every structure"""
        return requirement and self.can_afford(unit_type)

    def can_build_unique(self, unit_type, building, requirement=True):
        """Global requirements for building unique buildings"""
        return (
            not self.already_pending(unit_type)
            and self.can_afford(unit_type)
            and not building
            and self.building_requirement(unit_type, requirement)
        )

    def can_upgrade(self, upgrade, research, host_building):
        """Global requirements for upgrades"""
        return not self.already_pending_upgrade(upgrade) and self.can_afford(research) and host_building

    def prepare_expansions(self):
        """Prepare all expansion locations and put it in order based on distance"""
        start = self.start_location
        waypoints = [point for point in list(self.expansion_locations)]
        waypoints.sort(key=lambda p: (p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2)
        self.ordered_expansions = [Point2((p[0], p[1])) for p in waypoints]

    def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            self.add_action(drone.gather(self.state.mineral_field.closest_to(drone)))

    async def is_morphing(self, base, cancel):
        """Check if there is a lair morphing by checking the available abilities"""
        return cancel in await self.get_available_abilities(base)

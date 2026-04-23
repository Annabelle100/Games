from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import random


Hex = Tuple[int, int]


class Layer(str, Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class Resource(str, Enum):
    ORE = "ore"
    FLUX = "flux"
    FIBER = "fiber"
    EMBER = "ember"


class PieceType(str, Enum):
    CORE = "core"
    KEYSTONE = "keystone"
    RELAY = "relay"
    REFRACTOR = "refractor"


@dataclass
class Piece:
    owner: int
    piece_type: PieceType


@dataclass
class PlayerState:
    player_id: int
    resources: Dict[Resource, int] = field(default_factory=lambda: {
        Resource.ORE: 2,
        Resource.FLUX: 1,
        Resource.FIBER: 1,
        Resource.EMBER: 0,
    })
    instability: int = 0
    pressure: int = 0
    blueprint_hand: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)


@dataclass
class BuildGhost:
    owner: int
    piece_type: PieceType
    hex_coord: Hex


class RuleViolation(ValueError):
    pass


class ChronoforgeStrataGame:
    """Core deterministic rules engine for Chronoforge Strata."""

    BUILD_COST = {
        PieceType.KEYSTONE: {Resource.ORE: 1, Resource.FIBER: 1},
        PieceType.RELAY: {Resource.ORE: 1, Resource.FLUX: 1},
        PieceType.REFRACTOR: {Resource.FIBER: 1, Resource.EMBER: 1},
    }

    def __init__(self, num_players: int, seed: Optional[int] = None) -> None:
        if not 2 <= num_players <= 5:
            raise ValueError("Chronoforge Strata supports 2 to 5 players.")
        self.num_players = num_players
        self.random = random.Random(seed)
        self.round = 1
        self.current_player = 0

        self.board_cells: Set[Hex] = self._generate_hex_board(radius=5)
        self.layers: Dict[Layer, Dict[Hex, Piece]] = {
            Layer.PAST: {},
            Layer.PRESENT: {},
            Layer.FUTURE: {},
        }
        self.future_ghosts: List[BuildGhost] = []
        self.resonance_links: Set[Tuple[int, Hex, Layer, Layer]] = set()
        self.players: Dict[int, PlayerState] = {
            pid: PlayerState(player_id=pid) for pid in range(num_players)
        }

        self._place_starting_cores()

    @staticmethod
    def _generate_hex_board(radius: int) -> Set[Hex]:
        cells: Set[Hex] = set()
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                cells.add((q, r))
        return cells

    @staticmethod
    def neighbors(coord: Hex) -> List[Hex]:
        q, r = coord
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
        return [(q + dq, r + dr) for dq, dr in dirs]

    def _place_starting_cores(self) -> None:
        # distribute cores on board edge in deterministic clockwise-ish order
        edge_cells = sorted(
            [c for c in self.board_cells if self._hex_distance((0, 0), c) == 5],
            key=lambda x: (self._angle_key(x), x[0], x[1]),
        )
        step = len(edge_cells) // self.num_players
        for pid in range(self.num_players):
            hex_coord = edge_cells[(pid * step) % len(edge_cells)]
            self.layers[Layer.PRESENT][hex_coord] = Piece(pid, PieceType.CORE)

    @staticmethod
    def _hex_distance(a: Hex, b: Hex) -> int:
        aq, ar = a
        bq, br = b
        return max(abs(aq - bq), abs(ar - br), abs((aq + ar) - (bq + br)))

    @staticmethod
    def _angle_key(coord: Hex) -> float:
        q, r = coord
        x = q + r / 2
        y = (3 ** 0.5) * r / 2
        return (3.1415926535 + __import__("math").atan2(y, x)) % (2 * 3.1415926535)

    def _require_cell(self, hex_coord: Hex) -> None:
        if hex_coord not in self.board_cells:
            raise RuleViolation(f"Invalid hex {hex_coord}.")

    def _spend_resources(self, player_id: int, cost: Dict[Resource, int]) -> None:
        p = self.players[player_id]
        for res, amount in cost.items():
            if p.resources[res] < amount:
                raise RuleViolation(f"Player {player_id} lacks {res.value}.")
        for res, amount in cost.items():
            p.resources[res] -= amount

    def mine(self, player_id: int, hex_coord: Hex) -> None:
        self._require_cell(hex_coord)
        piece = self.layers[Layer.PRESENT].get(hex_coord)
        if not piece or piece.owner != player_id:
            raise RuleViolation("Mine requires your piece on Present layer.")
        reward = [Resource.ORE, Resource.FLUX, Resource.FIBER, Resource.EMBER][self.round % 4]
        self.players[player_id].resources[reward] += 1

    def build(self, player_id: int, layer: Layer, piece_type: PieceType, hex_coord: Hex) -> None:
        if piece_type == PieceType.CORE:
            raise RuleViolation("Cannot build a Core.")
        self._require_cell(hex_coord)
        if hex_coord in self.layers[layer]:
            raise RuleViolation("Hex already occupied in this layer.")
        self._spend_resources(player_id, self.BUILD_COST[piece_type])
        self.layers[layer][hex_coord] = Piece(player_id, piece_type)

    def shift(self, player_id: int, layer: Layer, source: Hex, target: Hex) -> None:
        self._require_cell(source)
        self._require_cell(target)
        if target not in self.neighbors(source):
            raise RuleViolation("Shift target must be adjacent.")
        p = self.layers[layer].get(source)
        if not p or p.owner != player_id:
            raise RuleViolation("No movable piece at source.")
        if p.piece_type == PieceType.CORE:
            raise RuleViolation("Architect Core cannot move.")
        if target in self.layers[layer]:
            raise RuleViolation("Target occupied.")
        self.layers[layer][target] = p
        del self.layers[layer][source]

    def project(self, player_id: int, piece_type: PieceType, hex_coord: Hex) -> None:
        if piece_type == PieceType.CORE:
            raise RuleViolation("Cannot project a Core.")
        self._require_cell(hex_coord)
        self._spend_resources(player_id, {Resource.FLUX: 1})
        self.future_ghosts.append(BuildGhost(player_id, piece_type, hex_coord))

    def retrofit(self, player_id: int, hex_coord: Hex) -> None:
        self._require_cell(hex_coord)
        piece = self.layers[Layer.PAST].get(hex_coord)
        if not piece or piece.owner != player_id:
            raise RuleViolation("Retrofit needs your Past piece.")
        if piece.piece_type not in (PieceType.KEYSTONE, PieceType.RELAY):
            raise RuleViolation("Only Keystone/Relay can retrofit.")
        self._spend_resources(player_id, {Resource.ORE: 1, Resource.FIBER: 1})
        piece.piece_type = PieceType.RELAY if piece.piece_type == PieceType.KEYSTONE else PieceType.KEYSTONE

        present = self.layers[Layer.PRESENT].get(hex_coord)
        if present and present.owner != player_id and present.piece_type != piece.piece_type:
            self.players[player_id].instability += 1
            self.players[present.owner].instability += 1
            self.players[present.owner].pressure += 1

    def resonate(self, player_id: int, lower: Layer, upper: Layer, hex_coord: Hex) -> None:
        if (lower, upper) not in ((Layer.PAST, Layer.PRESENT), (Layer.PRESENT, Layer.FUTURE)):
            raise RuleViolation("Resonance only between adjacent layers.")
        low_piece = self.layers[lower].get(hex_coord)
        up_piece = self.layers[upper].get(hex_coord)
        if not low_piece or not up_piece:
            raise RuleViolation("Both layers need pieces on same hex.")
        if low_piece.owner != player_id or up_piece.owner != player_id:
            raise RuleViolation("Resonance requires ownership on both pieces.")
        self.resonance_links.add((player_id, hex_coord, lower, upper))

    def stabilize(self, player_id: int) -> None:
        p = self.players[player_id]
        if sum(p.resources.values()) < 2:
            raise RuleViolation("Need any 2 resources to stabilize.")
        to_spend = 2
        for res in (Resource.ORE, Resource.FLUX, Resource.FIBER, Resource.EMBER):
            while p.resources[res] > 0 and to_spend > 0:
                p.resources[res] -= 1
                to_spend -= 1
            if to_spend == 0:
                break
        p.instability = max(0, p.instability - 1)

    def resolve_cascade_phase(self) -> None:
        for ghost in self.future_ghosts:
            if ghost.hex_coord in self.layers[Layer.PRESENT]:
                self.players[ghost.owner].instability += 1
                continue
            if ghost.hex_coord not in self.layers[Layer.FUTURE]:
                self.layers[Layer.PRESENT][ghost.hex_coord] = Piece(ghost.owner, ghost.piece_type)
        self.future_ghosts.clear()

    def resolve_stability_check(self) -> None:
        for pid, p in self.players.items():
            if p.pressure >= 3:
                if p.resources[Resource.FLUX] >= 2:
                    p.resources[Resource.FLUX] -= 2
                else:
                    p.instability += 1
                p.pressure = 0

            if p.instability >= 5:
                present_cells = [c for c, piece in self.layers[Layer.PRESENT].items() if piece.owner == pid and piece.piece_type != PieceType.CORE]
                if present_cells:
                    drop = self.random.choice(present_cells)
                    del self.layers[Layer.PRESENT][drop]
                if p.blueprint_hand:
                    p.blueprint_hand.pop(self.random.randrange(len(p.blueprint_hand)))
                p.instability = max(0, p.instability - 2)

    def continuity_links(self, player_id: int) -> int:
        pp = {(pid, hx) for pid, hx, lo, hi in self.resonance_links if pid == player_id and lo == Layer.PAST and hi == Layer.PRESENT}
        pf = {(pid, hx) for pid, hx, lo, hi in self.resonance_links if pid == player_id and lo == Layer.PRESENT and hi == Layer.FUTURE}
        return len({hx for (_, hx) in pp} & {hx for (_, hx) in pf})

    def controlled_keystones_present(self, player_id: int) -> int:
        return sum(1 for piece in self.layers[Layer.PRESENT].values() if piece.owner == player_id and piece.piece_type == PieceType.KEYSTONE)

    def apex_conditions_met(self, player_id: int) -> bool:
        anchor = self.controlled_keystones_present(player_id) >= 4
        continuity = self.continuity_links(player_id) >= 2
        core_cells = [c for c, p in self.layers[Layer.PRESENT].items() if p.owner == player_id and p.piece_type == PieceType.CORE]
        identity = bool(core_cells) and self.players[player_id].instability < 5
        return anchor and continuity and identity

    def apex_score(self, player_id: int) -> int:
        p = self.players[player_id]
        return (
            2 * self.controlled_keystones_present(player_id)
            + 3 * self.continuity_links(player_id)
            + p.resources[Resource.EMBER]
        )

    def end_round(self) -> None:
        self.resolve_cascade_phase()
        self.resolve_stability_check()
        self.round += 1
        self.current_player = (self.current_player + 1) % self.num_players


if __name__ == "__main__":
    game = ChronoforgeStrataGame(num_players=2, seed=7)
    print("Chronoforge Strata engine initialized")
    print(f"Board cells: {len(game.board_cells)}")
    for pid in range(game.num_players):
        print(f"Player {pid} resources: {game.players[pid].resources}")

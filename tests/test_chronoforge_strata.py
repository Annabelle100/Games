import unittest

from src.chronoforge_strata import ChronoforgeStrataGame, Layer, PieceType, Resource, RuleViolation


class TestChronoforgeStrata(unittest.TestCase):
    def setUp(self):
        self.game = ChronoforgeStrataGame(2, seed=1)

    def _find_empty_present_hex(self):
        occupied = set(self.game.layers[Layer.PRESENT].keys())
        for cell in self.game.board_cells:
            if cell not in occupied:
                return cell
        raise AssertionError("No empty present cell")

    def test_board_has_91_cells(self):
        self.assertEqual(len(self.game.board_cells), 91)

    def test_build_and_shift(self):
        hex_a = self._find_empty_present_hex()
        self.game.build(0, Layer.PRESENT, PieceType.KEYSTONE, hex_a)
        target = next(c for c in self.game.neighbors(hex_a) if c in self.game.board_cells and c not in self.game.layers[Layer.PRESENT])
        self.game.shift(0, Layer.PRESENT, hex_a, target)
        self.assertIn(target, self.game.layers[Layer.PRESENT])
        self.assertEqual(self.game.layers[Layer.PRESENT][target].piece_type, PieceType.KEYSTONE)

    def test_project_and_cascade(self):
        hex_a = self._find_empty_present_hex()
        self.game.project(0, PieceType.RELAY, hex_a)
        self.game.resolve_cascade_phase()
        self.assertIn(hex_a, self.game.layers[Layer.PRESENT])
        self.assertEqual(self.game.layers[Layer.PRESENT][hex_a].owner, 0)

    def test_resonate_requires_ownership(self):
        hex_a = self._find_empty_present_hex()
        self.game.build(0, Layer.PAST, PieceType.KEYSTONE, hex_a)
        self.game.build(0, Layer.PRESENT, PieceType.RELAY, hex_a)
        self.game.resonate(0, Layer.PAST, Layer.PRESENT, hex_a)
        self.assertEqual(len(self.game.resonance_links), 1)

    def test_stabilize_spends_two_resources(self):
        p = self.game.players[0]
        start_total = sum(p.resources.values())
        p.instability = 2
        self.game.stabilize(0)
        self.assertEqual(sum(p.resources.values()), start_total - 2)
        self.assertEqual(p.instability, 1)

    def test_invalid_build_core(self):
        hex_a = self._find_empty_present_hex()
        with self.assertRaises(RuleViolation):
            self.game.build(0, Layer.PRESENT, PieceType.CORE, hex_a)


if __name__ == "__main__":
    unittest.main()

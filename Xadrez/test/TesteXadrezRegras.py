import unittest
import Xadrez.XadrezRegras
import Xadrez.XadrezIA

class TesteXadrez(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gameState = Xadrez.XadrezRegras.GameState()
        cls.board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                     ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
                     ['--', '--', '--', '--', '--', '--', '--', '--'],
                     ['--', '--', '--', '--', '--', '--', '--', '--'],
                     ['--', '--', '--', '--', '--', '--', '--', '--'],
                     ['--', '--', '--', '--', '--', '--', '--', '--'],
                     ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
                     ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

    def test_ifWhiteIsFirstToMove(self):
        self.assertEqual(True, self.gameState.whiteToMove)

    def test_isInitialScoreMaterialEqualZero(self):
        self.assertEqual(0, Xadrez.XadrezIA.scoreMaterial(self.board))

if __name__ == '__main__':
    unittest.main()

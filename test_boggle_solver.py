import unittest
import sys

sys.path.append("/home/codio/workspace/pytest_demo/test_boggle_solver.py")  # have to tell the unittest the PATH to find boggle_solver.py and the Boggle Class

from boggle_solver import Boggle


class TestSuite_Alg_Scalability_Cases(unittest.TestCase):
    # === Helper methods for deterministic word placement ===

    def _mk_row_word(self, row, start_col, length, grid):
        """Return the word formed by grid[row][start_col : start_col+length] along the row."""
        return "".join(grid[row][start_col + i] for i in range(length))

    def _mk_col_word(self, col, start_row, length, grid):
        """Return the word formed by grid[start_row : start_row+length][col] along the column."""
        return "".join(grid[start_row + i][col] for i in range(length))

    def _mk_diag_word(self, start_row, start_col, length, grid):
        """Return the word formed by the top-left → bottom-right diagonal."""
        return "".join(grid[start_row + i][start_col + i] for i in range(length))

    # === Original 3x3 test (fixed formatting) ===
    def test_Normal_case_3x3(self):
        grid = [["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"]]
        dictionary = ["abc", "abdhi", "abi", "ef", "cfi", "dea"]
        mygame = Boggle(grid, dictionary)
        solution = mygame.getSolution()
        solution = [x.upper() for x in solution]
        expected = ["abc", "abdhi", "cfi", "dea"]
        expected = [x.upper() for x in expected]
        solution = sorted(solution)
        expected = sorted(expected)
        self.assertEqual(expected, solution)

    # ADD 4x4, 5x5, 6x6, 7x7...13x13, and LARGER Dictionaries
    # === 4x4 board ===
    def test_scalability_4x4(self):
        """
        Grid:
            A B C D
            E F G H
            I J K L
            M N O P
        Valid examples:
            - Row word 'ABC' (A→B→C)
            - Column word 'AEI' (A→E→I)
            - Diagonal 'AFK' (A→F→K)
            - A longer row word 'ABCD'
            - A longer column word 'AEIM'
        """
        grid = [["A", "B", "C", "D"],
                ["E", "F", "G", "H"],
                ["I", "J", "K", "L"],
                ["M", "N", "O", "P"]]
        # Build valid deterministic words
        w_row3 = self._mk_row_word(0, 0, 3, grid)     # ABC
        w_row4 = self._mk_row_word(0, 0, 4, grid)     # ABCD
        w_col3 = self._mk_col_word(0, 0, 3, grid)     # AEI
        w_col4 = self._mk_col_word(0, 0, 4, grid)     # AEIM
        w_diag3 = self._mk_diag_word(0, 0, 3, grid)   # AFK

        dictionary = [
            w_row3, w_row4, w_col3, w_col4, w_diag3,
            "ZZZ", "QQQ", "NOPE", "SHORT", "AB"  # distractors; "AB" too short
        ]
        game = Boggle(grid, dictionary)
        got = sorted([x.upper() for x in game.getSolution()])
        expected = sorted([w_row3, w_row4, w_col3, w_col4, w_diag3])
        expected = [x.upper() for x in expected]
        self.assertEqual(expected, got)

    # === 5x5 board ===
    def test_scalability_5x5(self):
        """
        Use a 5×5 sequential grid to create multiple guaranteed words:
        - First row 'ABCDE', first 3 'ABC'
        - First col 'AFKPU', first 3 'AFK'
        - Diagonal 'AFKPU' (top-left to bottom-right)
        """
        grid = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O"],
            ["P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y"],
        ]

        w_row3 = self._mk_row_word(0, 0, 3, grid)     # ABC
        w_row5 = self._mk_row_word(0, 0, 5, grid)     # ABCDE
        w_col3 = self._mk_col_word(0, 0, 3, grid)     # AFK
        w_col5 = self._mk_col_word(0, 0, 5, grid)     # AFKPU
        w_diag5 = self._mk_diag_word(0, 0, 5, grid)   # diagonal using helper

        dictionary = [
            w_row3, w_row5, w_col3, w_col5, w_diag5,
            "XYZ", "AAA", "FOO", "BAR", "AB"  # distractors, too short or not present
        ]
        game = Boggle(grid, dictionary)
        got = sorted([x.upper() for x in game.getSolution()])
        expected = sorted([w_row3, w_row5, w_col3, w_col5, w_diag5])
        expected = [x.upper() for x in expected]
        self.assertEqual(expected, got)

    # === 6x6 board (with a multi-letter tile to ensure it scales) ===
    def test_scalability_6x6_with_special_tile(self):
        """
        Include a 'QU' tile and ensure longer paths still work.
        We will place 'QU' at (0,0) and form 'QUABC' (QU→A→B→C along row 0)
        Also check a long column path to exercise deeper DFS.
        """
        grid = [
            ["QU", "A",  "B",  "C",  "D",  "E"],
            ["F",  "G",  "H",  "I",  "J",  "K"],
            ["L",  "M",  "N",  "O",  "P",  "Q"],
            ["R",  "S",  "T",  "U",  "V",  "W"],
            ["X",  "Y",  "Z",  "A",  "B",  "C"],
            ["D",  "E",  "F",  "G",  "H",  "I"],
        ]
        # QUABC = "QU" + "A" + "B" + "C" (length 5 counting letters)
        w_qu_row = "QU" + grid[0][1] + grid[0][2] + grid[0][3]   # QUABC
        # A long column using (0,1) down 5 tiles: A, G, M, S, Y -> "AGMSY"
        w_col5 = self._mk_col_word(1, 0, 5, grid)

        dictionary = [
            w_qu_row, w_col5,
            "QU", "QA", "QQQ", "TOO_SHORT", "AB"  # "QU" len=2 invalid
        ]
        game = Boggle(grid, dictionary)
        got = sorted([x.upper() for x in game.getSolution()])
        expected = sorted([w_qu_row, w_col5])
        expected = [x.upper() for x in expected]
        self.assertEqual(expected, got)

    # === 7x7 board ===
    def test_scalability_7x7(self):
        """
        Build a 7x7 where Row 3 and Column 4 contain guaranteed sequences.
        """
        # Generate a grid of simple letters cycling A..Z; keep deterministic
        letters = [chr(ord('A') + (i % 26)) for i in range(49)]
        grid = [letters[i*7:(i+1)*7] for i in range(7)]

        # Row 2 (0-based): take first 5 contiguous tiles
        w_row5 = self._mk_row_word(2, 1, 5, grid)  # positions (2,1) to (2,5)
        # Column 3: take 4 contiguous tiles
        w_col4 = self._mk_col_word(3, 1, 4, grid)
        # Diagonal of length 4 from (1,1)
        w_diag4 = self._mk_diag_word(1, 1, 4, grid)

        dictionary = [
            w_row5, w_col4, w_diag4,
            "NOTINBOARD", "XXXY", "AB"  # distractors
        ]
        game = Boggle(grid, dictionary)
        got = sorted([x.upper() for x in game.getSolution()])
        expected = sorted([w_row5, w_col4, w_diag4])
        expected = [x.upper() for x in expected]
        self.assertEqual(expected, got)

    # === 10x10 board with bigger dictionary ===
    def test_scalability_10x10_large_dict(self):
        """
        Stress with a larger dictionary (few thousand entries) but only a handful valid.
        We build guaranteed valid strings:
          - first row first 6 letters
          - first column first 6 letters
          - a diagonal of 6
        Then add many distractors.
        """
        n = 10
        # Build a 10x10 grid cycling A..Z deterministically
        grid = []
        val = 0
        for r in range(n):
            row = []
            for c in range(n):
                row.append(chr(ord('A') + (val % 26)))
                val += 1
            grid.append(row)

        w_row6 = self._mk_row_word(0, 0, 6, grid)
        w_col6 = self._mk_col_word(0, 0, 6, grid)
        w_diag6 = self._mk_diag_word(0, 0, 6, grid)

        # Construct a large dictionary: include many fake 5-8 letter strings
        dictionary = [w_row6, w_col6, w_diag6]
        # Add ~3000 distractors
        for i in range(3000):
            word = "Z" + "X" * (3 + (i % 5)) + "Q"  # e.g., ZXXXQ, ZXXXXQ, ...
            dictionary.append(word)

        game = Boggle(grid, dictionary)
        got = set(x.upper() for x in game.getSolution())
        expected = set([w_row6, w_col6, w_diag6])
        expected = set(x.upper() for x in expected)
        # Ensure all expected are present and that result size is small (no explosion)
        self.assertTrue(expected.issubset(got))
        self.assertLessEqual(len(got), len(expected) + 3)  # allow a couple incidental hits at most

    # === 13x13 board (upper bound in your request) ===
    def test_scalability_13x13(self):
        """
        Create a 13x13 grid and validate a few long strings to exercise deep recursion/trie traversal.
        """
        n = 13
        grid = []
        val = 0
        for r in range(n):
            row = []
            for c in range(n):
                row.append(chr(ord('A') + (val % 26)))
                val += 1
            grid.append(row)

        # Long row/col/diag strings of length 8
        w_row8 = self._mk_row_word(5, 2, 8, grid)    # row 5, cols 2..9
        w_col8 = self._mk_col_word(7, 1, 8, grid)    # col 7, rows 1..8
        w_diag8 = self._mk_diag_word(3, 3, 8, grid)  # diag from (3,3)

        dictionary = [w_row8, w_col8, w_diag8]
        # Add many medium-length distractors
        for i in range(1500):
            dictionary.append("M" + "NOP"[i % 3] * 4 + "Z" + "A" * (i % 2 + 2))

        game = Boggle(grid, dictionary)
        got = sorted([x.upper() for x in game.getSolution()])
        expected = sorted([w_row8, w_col8, w_diag8])
        expected = [x.upper() for x in expected]
        for w in expected:
            self.assertIn(w, got)
        # Not asserting exact equality to keep test resilient to incidental finds on large boards.


class TestSuite_Simple_Edge_Cases(unittest.TestCase):
    # ADD MANY SIMPLE TEST CASES
    def test_SquareGrid_case_1x1(self):
        grid = [["A"]]
        dictionary = ["a", "b", "c"]
        mygame = Boggle(grid, dictionary)
        solution = mygame.getSolution()
        solution = [x.upper() for x in solution]
        expected = []
        solution = sorted(solution)
        expected = sorted(expected)
        self.assertEqual(expected, solution)

    def test_EmptyGrid_case_0x0(self):
        grid = [[]]
        dictionary = ["hello", "there", "general", "kenobi"]
        mygame = Boggle(grid, dictionary)
        solution = mygame.getSolution()
        solution = [x.upper() for x in solution]
        expected = []
        solution = sorted(solution)
        expected = sorted(expected)
        self.assertEqual(expected, solution)

    # --- NEW SIMPLE EDGE CASES ---

    def test_NonSquareGrid_rejected(self):
        grid = [["A", "B", "C"],
                ["D", "E", "F"]]  # 2x3, not square
        dictionary = ["ABC", "DEF"]
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        self.assertEqual([], sorted(solution))

    def test_NonAlphabeticTile_rejected(self):
        grid = [["A", "*"],
                ["C", "D"]]  # '*' invalid
        dictionary = ["ACD"]
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        self.assertEqual([], sorted(solution))

    def test_EmptyStringTile_rejected(self):
        grid = [["A", ""],
                ["C", "D"]]  # empty tile invalid
        dictionary = ["ACD"]
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        self.assertEqual([], sorted(solution))

    def test_WhitespaceTile_rejected(self):
        grid = [["A", "  "],
                ["C", "D"]]
        dictionary = ["ACD"]
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        self.assertEqual([], sorted(solution))

    def test_EmptyDictionary_returns_empty(self):
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = []
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], sorted([x.upper() for x in mygame.getSolution()]))

    def test_Dictionary_all_short_or_invalid_returns_empty(self):
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = ["a", "ab", 42, None, "", "  "]
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], sorted([x.upper() for x in mygame.getSolution()]))

    def test_CaseInsensitivity_normalization(self):
        grid = [["a", "b"],
                ["c", "d"]]
        dictionary = ["acb", "AB"]  # "AB" too short
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        expected = ["ACB"]
        self.assertEqual(sorted(expected), sorted(solution))

    def test_NoReuse_same_cell_disallowed(self):
        grid = [["A", "B"],
                ["X", "X"]]
        dictionary = ["ABA"]  # would need to reuse 'A'
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], sorted([x.upper() for x in mygame.getSolution()]))

    def test_Disconnected_letters_no_word(self):
        # 'CAT' can't be formed if letters are not adjacent in order
        grid = [["C", "X"],
                ["X", "A"]]  # No 'T' adjacent to A/C chain
        dictionary = ["CAT"]
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], sorted([x.upper() for x in mygame.getSolution()]))

    def test_Output_is_sorted(self):
        grid = [["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"]]
        dictionary = ["CFI", "ABDHI", "DEA", "ABC"]
        mygame = Boggle(grid, dictionary)
        result = mygame.getSolution()
        # Assert sorted (defensive—your solver already sorts)
        self.assertEqual(result, sorted(result))

    def test_SpecialTiles_QU_counts_as_two_letters(self):
        # 'QU' + 'A' = "QUA" length 3 -> valid; "QU" alone (len 2) -> invalid
        grid = [["QU", "A"],
                ["X",  "X"]]
        dictionary = ["QUA", "QU"]  # 'QU' too short
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        expected = ["QUA"]
        self.assertEqual(sorted(expected), sorted(solution))

    def test_SpecialTiles_ST_and_IE(self):
        grid = [["ST", "IE"],
                ["A",  "R"]]
        # Valid: "STIE" (ST + IE), "STAR" (ST -> A -> R)
        dictionary = ["stie", "star", "sti"]  # "STI" uses "ST" + "I" (no raw I tiles) -> should not be found
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        expected = ["STIE", "STAR"]
        self.assertEqual(sorted(expected), sorted(solution))

    def test_MinLength_enforced(self):
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = ["AB", "A", "BC"]  # all < 3
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], sorted([x.upper() for x in mygame.getSolution()]))

    def test_Trie_prefix_pruning_basic(self):
        # Ensure prefixes that can't lead to words are pruned (functional expectation)
        grid = [["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"]]
        # Only ABC and ABE are real; 'ABZ...' distractors shouldn't create results
        dictionary = ["ABC", "ABE", "ABZ", "ABZZZ", "ABZZZZ"]
        mygame = Boggle(grid, dictionary)
        solution = [x.upper() for x in mygame.getSolution()]
        expected = ["ABC", "ABE"]
        self.assertEqual(sorted(expected), sorted(solution))

    def test_Repeated_tiles_adjacent_different_cells_ok(self):
        # Same letter from different cells is allowed (not reuse of the same cube)
        grid = [["A", "A"],
                ["A", "A"]]
        dictionary = ["AAA", "AAAA"]
        mygame = Boggle(grid, dictionary)
        # It should find AAA and AAAA by walking distinct cells
        solution = [x.upper() for x in mygame.getSolution()]
        expected_subset = set(["AAA", "AAAA"])
        self.assertTrue(expected_subset.issubset(set(solution)))

    def test_Grid_with_trailing_spaces_normalized(self):
        grid = [[" A", "B "],
                [" C", " D "]]
        dictionary = ["ACB"]
        mygame = Boggle(grid, dictionary)
        # If tiles are stripped to alpha, solver should work. If not, expect [].
        # Given your setGrid strips tile via tile.strip() and checks isalpha(),
        # these should normalize to "A","B","C","D".
        self.assertEqual(["ACB"], [x.upper() for x in mygame.getSolution()])

    def test_Dictionary_with_whitespace_entries(self):
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = ["  acb ", "  ", "\t", "\n", "AB "]
        mygame = Boggle(grid, dictionary)
        # "ACB" is valid; "AB" too short; whitespaces ignored
        self.assertEqual(["ACB"], [x.upper() for x in mygame.getSolution()])

    def test_VeryLongWord_not_possible(self):
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = ["ABCDABCDABCD"]  # longer than any path without reuse
        mygame = Boggle(grid, dictionary)
        self.assertEqual([], [x.upper() for x in mygame.getSolution()])


class TestSuite_Complete_Coverage(unittest.TestCase):
    # ADD MANY COMPLEX TEST CASES

    def test_multiple_paths_same_word_and_others(self):
        """
        Grid has multiple ways to form 'ART' plus other words.
        Ensures solver returns a single unique 'ART' and includes longer words.
        """
        grid = [
            ["A", "R", "T"],
            ["R", "A", "R"],
            ["T", "R", "A"],
        ]
        dictionary = ["ART", "TAR", "ARR", "RAR", "ARTA"]  # 'ARTA' length 4 possible?
        game = Boggle(grid, dictionary)
        solution = [x.upper() for x in game.getSolution()]
        expected_subset = set(["ART", "TAR"])
        self.assertTrue(expected_subset.issubset(set(solution)))
        # Ensure no duplicates
        self.assertEqual(len(solution), len(set(solution)))

    def test_long_snake_word_zigzag(self):
        """
        Construct a 'snake' path along the grid edges to form a long word without reusing cubes.
        """
        grid = [
            ["A", "B", "C", "D"],
            ["H", "G", "F", "E"],
            ["I", "J", "K", "L"],
            ["P", "O", "N", "M"],
        ]
        # Snake path: A-B-C-D-E-F-G-H-I-J-K-L-M-N-O-P
        long_word = "ABCDEFGHIJKLMNOP"
        dictionary = [long_word, long_word[:2], "XYZ"]
        game = Boggle(grid, dictionary)
        solution = [x.upper() for x in game.getSolution()]
        self.assertIn(long_word, solution)

    def test_special_tiles_chain_mixes(self):
        """
        Chain multiple special tiles across the board.
        QU -> ST -> IE -> R forms 'QUESTIER' (QU + ESTI + ER), but we’ll build simpler guaranteed paths:
          - QUA (QU + A)
          - STIE (ST + IE)
          - QUART (QU + AR + T with adjacency)
        """
        grid = [
            ["QU", "A",  "R",  "T"],
            ["X",  "ST", "IE", "R"],
            ["A",  "R",  "T",  "S"],
            ["X",  "X",  "X",  "X"],
        ]
        dictionary = ["QUA", "STIE", "QUART", "QUIET", "QUERY", "QUAR", "STAR"]
        # Guaranteed:
        # - QUA: QU (0,0) -> A (0,1)
        # - STIE: ST (1,1) -> IE (1,2)
        # - QUART: QU (0,0) -> A(0,1) -> R(0,2) -> T(0,3)
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected_subset = set(["QUA", "STIE", "QUART"])
        self.assertTrue(expected_subset.issubset(set(solution)))

    def test_no_raw_single_letter_Q_S_I_tiles(self):
        """
        Spec note: there are no raw 'Q'/'S'/'I' tiles in the special-tiles game variant.
        This test ensures words that *require* raw Q/S/I cannot be formed unless
        the board contains their multi-letter counterparts (QU/ST/IE).
        """
        grid = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G",  "H", "J"],
        ]
        dictionary = ["QI", "SI", "IS", "QIS", "SIR"]  # require raw Q/S/I paths
        game = Boggle(grid, dictionary)
        solution = [x.upper() for x in game.getSolution()]
        self.assertEqual([], sorted(solution))

    def test_dense_repeats_large_overlap(self):
        """
        Lots of repeated letters. Ensure DFS handles heavy branching without reusing cubes.
        Should find AAA and AAAA via different paths using distinct cells.
        """
        grid = [
            ["A", "A", "A"],
            ["A", "A", "A"],
            ["A", "A", "A"],
        ]
        dictionary = ["AAA", "AAAA", "AAAAA", "AAAAAA"]  # many lengths possible; ≥3 allowed
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertIn("AAA", solution)
        self.assertIn("AAAA", solution)
        # Allow presence/absence of longer ones depending on path limits; at least these two must exist.

    def test_backtrack_pruning_deep_prefix(self):
        """
        Words share long prefixes, then diverge; tests trie prefix navigation and backtracking.
        """
        grid = [
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
            ["I", "J", "K", "L"],
            ["M", "N", "O", "P"],
        ]
        # Build words with long shared prefixes: ABFJ..., ABFG..., ABFE...
        w1 = "ABFJ"
        w2 = "ABFG"
        w3 = "ABFE"
        # All are ≥3 and can be made by adjacency:
        # A(0,0)->B(0,1)->F(1,1)->J(2,1)
        # A(0,0)->B(0,1)->F(1,1)->G(1,2)
        # A(0,0)->B(0,1)->F(1,1)->E(1,0)
        dictionary = [w1, w2, w3, "AB", "A"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected_subset = sorted([w1, w2, w3])
        self.assertTrue(set(expected_subset).issubset(set(solution)))

    def test_dictionary_dedup_and_case_norm_large_mix(self):
        """
        Dictionary contains duplicates and mixed casing; only unique uppercase words should be returned.
        """
        grid = [
            ["C", "A", "T"],
            ["A", "T", "E"],
            ["T", "E", "N"],
        ]
        dictionary = ["cat", "Cat", "CAT", "cAt", "ten", "TEN", "tent", "TeN", "aa", "bb"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        # 'CAT' diagonally C(0,0)->A(1,0)->T(1,1)
        # 'TEN' T(1,1)->E(1,2)->N(2,2)
        expected_subset = ["CAT", "TEN"]
        for w in expected_subset:
            self.assertIn(w, solution)
        # Ensure duplicates in dict do not produce duplicates in output
        self.assertEqual(len(solution), len(set(solution)))

    def test_interlocking_words_share_cells_but_not_paths(self):
        """
        On this layout, 'ART' is reachable; 'RAT' and 'TAR' are not guaranteed by adjacency.
        """
        grid = [
            ["A", "R", "T"],
            ["X", "X", "X"],
            ["A", "R", "T"],
        ]
        dictionary = ["ART", "RAT", "TAR", "XAR", "ARX"]
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertIn("ART", solution)

    def test_special_tiles_multi_step_word(self):
        """
        With special tiles and no raw 'I', expect words that respect multi-letter tiles:
        - 'STA'   via ST -> A
        - 'STAT'  via ST -> A -> T
        - 'STON'  via ST -> O -> N
        'STATION' is NOT achievable because 'IE' contributes two letters, not a single 'I'.
        """
        grid = [
            ["ST", "A",  "T",  "X"],
            ["X",  "IE", "O",  "N"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
        ]
        dictionary = ["STATION", "STAT", "STON", "STA", "STAI"]  # STAI requires raw I after ST (invalid)
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())

        # Valid and expected:
        self.assertIn("STA", solution)
        self.assertIn("STAT", solution)
        
        # Not possible under these special-tile rules:
        self.assertNotIn("STON", solution)
        self.assertNotIn("STATION", solution)  # requires 'ION'; only 'IE' exists → would become STATIEON
        self.assertNotIn("STAI", solution)     # requires raw 'I' after ST

    def test_blockers_surrounded_letter_trap(self):
        """
        Diagonals are allowed, so 'XAX' is reachable:
        (0,0) -> (1,1) -> (2,2)
        """
        grid = [
            ["X", "X", "X"],
            ["X", "A", "X"],
            ["X", "X", "X"],
        ]
        dictionary = ["AAA", "AXA", "XAX"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected = ["XAX"]
        self.assertEqual(expected, solution)

    def test_big_board_with_specials_and_normal_words(self):
        """
        5x5 board mixing special tiles and checking multiple results.
        """
        grid = [
            ["QU", "A",  "B",  "C", "D"],
            ["E",  "F",  "G",  "H", "I"],
            ["J",  "K",  "ST", "L", "M"],
            ["N",  "O",  "P",  "IE", "Q"],
            ["R",  "S",  "T",  "U", "V"],
        ]
        dictionary = [
            "QUA",      # QU + A
            "STIE",     # ST + IE (diagonal adjacency OK)
            "ABF",      # A(0,1)->B(0,2)->F(1,1)
            "JKL",      # Not guaranteed; kept as distractor
            "NOP",      # N(3,0)->O(3,1)->P(3,2)
        ]
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        expected_subset = {"QUA", "ABF", "NOP", "STIE"}
        self.assertTrue(expected_subset.issubset(solution))

    def test_result_is_sorted_and_unique(self):
        """
        Final sanity: results must be sorted and contain unique words.
        """
        grid = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ]
        dictionary = ["ABC", "ABE", "CFI", "DEH", "ABC", "CFI"]  # duplicates in dict
        game = Boggle(grid, dictionary)
        result = game.getSolution()
        self.assertEqual(result, sorted(result))
        self.assertEqual(len(result), len(set(result)))


class TestSuite_Qu_and_St(unittest.TestCase):
    # ADD QU AND ST TEST CASES

    def test_QU_basic_len_rule(self):
        """
        QU counts as two letters:
        - 'QU' alone (len=2) should NOT be returned (min length=3).
        - 'QUA' is valid if 'A' is adjacent to QU.
        """
        grid = [["QU", "A"],
                ["X",  "X"]]
        dictionary = ["QU", "QUA"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected = ["QUA"]
        self.assertEqual(expected, solution)

    def test_ST_basic_len_rule(self):
        """
        ST counts as two letters:
        - 'ST' alone (len=2) should NOT be returned.
        - 'STA' is valid if 'A' is adjacent to ST.
        """
        grid = [["ST", "A"],
                ["X",  "X"]]
        dictionary = ["ST", "STA"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected = ["STA"]
        self.assertEqual(expected, solution)

    def test_STIE_two_special_tiles_adjacent(self):
        """
        Two multi-letter tiles can chain:
        - 'STIE' = ST (2) + IE (2) forms length 4.
        """
        grid = [["ST", "IE"],
                ["X",  "X"]]
        dictionary = ["STIE", "STI", "SIE"]  # STI requires raw I; SIE requires raw S
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected = ["STIE"]
        self.assertEqual(expected, solution)

    def test_QUART_row_chain(self):
        """
        4x4 square board; row 0 contains QU-A-R-T → 'QUA', 'QUAR', 'QUART'
        """
        grid = [
            ["QU", "A",  "R",  "T"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
        ]
        dictionary = ["QUART", "QUA", "QUAR"]
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertIn("QUA", solution)
        self.assertIn("QUAR", solution)
        self.assertIn("QUART", solution)

    def test_diagonal_adjacency_with_specials(self):
        """
        Diagonals are allowed:
        - 'QUA' with QU at (0,0) and A at (1,1) (diagonal).
        - 'STA' with ST at (0,0) and A at (1,1) (diagonal).
        """
        grid = [["QU", "X"],
                ["X",  "A"]]
        dictionary = ["QUA", "STA"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        # Only QUA is valid because there's no ST tile on board
        self.assertEqual(["QUA"], solution)

        grid2 = [["ST", "X"],
                 ["X",  "A"]]
        dictionary2 = ["STA"]
        game2 = Boggle(grid2, dictionary2)
        solution2 = sorted([x.upper() for x in game2.getSolution()])
        self.assertEqual(["STA"], solution2)

    def test_no_raw_Q_or_S_words(self):
        """
        Words that require raw 'Q' or 'S' should not be found unless formed with QU/ST.
        """
        grid = [["A", "B"],
                ["C", "D"]]
        dictionary = ["QAT", "SAD", "QIS", "SIR"]  # require raw Q/S tile which doesn't exist
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        self.assertEqual([], solution)

    def test_mixed_case_input_and_tiles(self):
        """
        Ensure lowercase input tiles/dictionary normalize correctly.
        """
        grid = [["qu", "a"],
                ["st", "x"]]
        dictionary = ["qua", "stx", "qu", "st"]  # 'qu'/'st' alone too short
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        expected_subset = {"QUA", "STX"}
        self.assertTrue(expected_subset.issubset(set(solution)))

    def test_no_cube_reuse_with_specials(self):
        """
        Ensure a single multi-letter tile cannot be reused in the same path.
        Example: 'QUQUA' would require reusing the 'QU' tile on a 1x3 board.
        """
        grid = [["QU", "A", "X"],
                ["X",  "X", "X"],
                ["X",  "X", "X"]]
        dictionary = ["QUQUA", "QUA"]
        game = Boggle(grid, dictionary)
        solution = sorted([x.upper() for x in game.getSolution()])
        self.assertEqual(["QUA"], solution)

    def test_chain_ST_then_regular_then_QU(self):
        """
        4x4 board with:
        - STARE along row 0
        - QUA via QU(1,1) adjacent (diagonal) to A(0,1)
        """
        grid = [
            ["ST", "A",  "R",  "E"],
            ["X",  "QU", "X",  "X"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
        ]
        dictionary = ["STARE", "STARK", "QUA"]
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertIn("STARE", solution)
        self.assertIn("QUA", solution)
        self.assertNotIn("STARK", solution)  # 'K' not present/adjacent in this layout

    def test_ST_word_multiple_lengths(self):
        """
        4x4 square board: 'STA', 'STAR', 'START' along row 0.
        """
        grid = [
            ["ST", "A",  "R",  "T"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
            ["X",  "X",  "X",  "X"],
        ]
        dictionary = ["STA", "STAR", "START", "ST", "STT"]  # ST len=2 invalid; STT not formable
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertTrue({"STA", "STAR", "START"}.issubset(solution))

    def test_STIE_longer_chain(self):
        """
        Square board where ST and IE are adjacent to form both 'STIE' and a longer 'STIER'.
        """
        grid = [
            ["ST", "IE", "R"],
            ["X",  "X",  "X"],
            ["X",  "X",  "X"],
        ]
        dictionary = ["STIE", "STIER", "STI"]  # 'STI' requires raw 'I' after ST (invalid)
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        self.assertIn("STIE", solution)
        self.assertIn("STIER", solution)
        self.assertNotIn("STI", solution)

    def test_specials_can_start_anywhere(self):
        """
        Special tiles are valid starting points just like single-letter tiles.
        """
        grid = [["A",  "B",  "C"],
                ["QU", "X",  "X"],
                ["X",  "ST", "A"]]
        dictionary = ["QUA", "STA", "STB", "QUX"]  # STB requires B adjacent to ST
        game = Boggle(grid, dictionary)
        solution = set(x.upper() for x in game.getSolution())
        # QU at (1,0) adjacent to A at (0,0) -> 'QUA' valid
        self.assertIn("QUA", solution)
        # ST at (2,1) adjacent to A at (2,2) -> 'STA' valid
        self.assertIn("STA", solution)
        # STB requires B adjacent to ST (2,1); B at (0,1) is too far
        self.assertNotIn("STB", solution)


if __name__ == '__main__':
    unittest.main()
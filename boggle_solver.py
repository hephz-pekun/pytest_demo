'''
Name: Iyanuoluwa Hephzibah Olanipekun
SID: 004003879
'''
class Boggle:
    def __init__(self, grid, dictionary):
        self.grid = []
        self.dictionary = []
        self.solution = []
        
# Internal helpers for later steps
        self._n = 0                 # Board size (N)
        self._neighbors = None      # Precomputed neighbors (later step) -- done
        self._dict_set = set()      # optional --- step 2
        self._prefixes = set()      # optional -- step 3
        self._trie_root = None


        # Initialize using setters (includes validation & normalization)
        self.setGrid(grid)
        self.setDictionary(dictionary)

    
    def _compute_neighbors(self):
        """
        Purpose:
            Precompute the 8-directional neighbors for each cell in the NxN grid.
            This speeds up DFS by avoiding recalculating bounds checks repeatedly.

            A neighbor is any adjacent cell including diagonals. For a cell (r, c),
            valid neighbors are (r+dr, c+dc) where dr and dc are in {-1, 0, 1}
            except the pair (0, 0).

        Arguments:
            None

        Returns:
            None

        Side Effects:
            - Sets `self._neighbors` to a 2D list where `self._neighbors[r][c]`
              is a list of (nr, nc) tuples that are valid neighbors of (r, c).

        Error Handling:
            - If the grid is invalid or empty (`self._n == 0`), sets `self._neighbors` to None.
        """
        n = self._n
        if n <= 0 or not self.grid:
            self._neighbors = None
            return

        # Initialize neighbor structure
        neighbors = [[[] for _ in range(n)] for _ in range(n)]
        directions = (-1, 0, 1)

        for r in range(n):
            for c in range(n):
                cell_neighbors = []
                for dr in directions:
                    for dc in directions:
                        if dr == 0 and dc == 0:
                            continue  # skip the cell itself
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            cell_neighbors.append((nr, nc))
                neighbors[r][c] = cell_neighbors

        self._neighbors = neighbors

    
    def _build_prefixes(self):
        """
        Purpose:
            Build a set of all possible prefixes from the current dictionary.
            This allows fast pruning during DFS:
            - If the current path string is not a prefix of any word, we can stop exploring it.

        Arguments:
            None

        Returns:
            None

        Side Effects:
            - Sets `self._prefixes` to a set of strings that represent all prefixes
              of words in `self.dictionary`.
            - Example: For word "APPLE", we add "A", "AP", "APP", "APPL", "APPLE".

        Error Handling:
            - If the dictionary is empty, sets `self._prefixes` to an empty set.
        """
        self._prefixes = set()
        if not self.dictionary:
            return

        for word in self.dictionary:
            # word is already uppercase and len >= 3 from setDictionary
            for i in range(1, len(word) + 1):
                self._prefixes.add(word[:i])


    def setGrid(self, grid):
        """
        Purpose:
            Validate and normalize the provided grid. Ensures the grid is:
            - Non-empty
            - Square (NxN)
            - Each tile is a non-empty alphabetical string
            - All tiles normalized to uppercase (e.g., "qu" -> "QU")

            Note on special tiles:
            The solver (in later steps) will treat tiles like "QU", "ST", and "IE"
            as multi-letter tiles. Here we simply normalize them as uppercase strings.
            We do NOT split them in this step.

        Arguments:
            grid (list[list[str]]): The candidate grid to set. Expected as a 2D list
                                    where each element is a string tile.

        Returns:
            None

        Side Effects:
            - Sets `self.grid` to a normalized copy of the input.
            - Sets `self._n` to the board size.

        Error Handling:
            - If invalid, sets `self.grid` to [] and `self._n` to 0.
        """


        # Basic structural checks
        if not isinstance(grid, list) or len(grid) == 0:
            self.grid = []
            self._n = 0
            self._neighbors = None
            self.solution = []
            return

        n = len(grid)

        # Ensure all rows are lists and count equals n (square grid)
        for row in grid:
            if not isinstance(row, list) or len(row) != n:
                self.grid = []
                self._n = 0
                self._neighbors = None
                self.solution = []
                return

        # Validate and normalize each tile
        normalized = []
        for r in range(n):
            row_norm = []
            for c in range(n):
                tile = grid[r][c]
                # Each tile must be a string
                if not isinstance(tile, str):
                    self.grid = []
                    self._n = 0
                    self._neighbors = None
                    self.solution = []
                    return
                tile = tile.strip()
                # No empty tiles
                if tile == "":
                    self.grid = []
                    self._n = 0
                    self._neighbors = None
                    self.solution = []
                    return
                # Must be purely alphabetic (no digits/symbols)
                if not tile.isalpha():
                    self.grid = []
                    self._n = 0
                    self._neighbors = None
                    self.solution = []
                    return
                # Normalize to uppercase for consistent matching later
                row_norm.append(tile.upper())
            normalized.append(row_norm)

        # If we reach here, grid is valid
        self.grid = normalized
        self._n = n

        # Recompute neighbors whenever grid changes
        self._compute_neighbors()

        # Reset solution cache since the board changed
        self.solution = []


    def setDictionary(self, dictionary):
        '''
        Purpose:
            Validate and normalize the provided dictionary:
              - Keep only strings
              - Normalize to uppercase
              - Keep only words of length >= 3 (Boggle rule)
              - Deduplicate for efficient searching

        Arguments:
            dictionary (list[str]): Candidate list of words.

        Returns:
            None

        Side Effects:
            - Sets `self.dictionary` to a normalized list (unique, uppercase, len>=3).
            - Prepares `self._dict_set` for O(1) membership checks (later steps).
            - Clears `self._prefixes` (to be rebuilt in later steps).
            - Resets `self.solution` cache.

        Error Handling:
            - If invalid or empty input, sets `self.dictionary` to [] and `_dict_set` to empty set.
'''

        if not isinstance(dictionary, list) or len(dictionary) == 0:
            self.dictionary = []
            self._dict_set = set()
            self._prefixes = set()
            self._trie_root = None
            self.solution = []
            return

        norm_set = set()
        for w in dictionary:
            if isinstance(w, str):
                w_up = w.strip().upper()
                # Filter out empty and words shorter than 3 (Boggle rule)
                if len(w_up) >= 3 and w_up.isalpha():
                    norm_set.add(w_up)

        # Store as a list (spec asks for an "array of words") and a set for fast lookup
        self.dictionary = sorted(norm_set)  # sorting is optional but gives stable order
        self._dict_set = set(self.dictionary)
        self._build_trie()

        # Build prefixes for pruning (Step 2)
        self._build_prefixes = set()

        # Reset solution cache since dictionary changed
        self.solution = []

    def _build_trie(self):
        """
        Purpose:
            Build a Trie from the current normalized dictionary (uppercase, len >= 3).
            The trie supports efficient prefix and whole-word checks during DFS.

        Arguments:
            None

        Returns:
            None

        Side Effects:
            - Sets `self._trie_root` to the root TrieNode of the dictionary.
            - Clears any previously existing trie by overwriting `self._trie_root`.

        Error Handling:
            - If the dictionary is empty, sets `self._trie_root` to None.
        """
        if not self.dictionary:
            self._trie_root = None
            return

        root = TrieNode()
        for word in self.dictionary:
            # word is already validated: uppercase, alphabetic, len >= 3
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_word = True  # Mark end of a valid dictionary word
        self._trie_root = root

    def _trie_has_prefix(self, prefix):
        """
        Purpose:
            Check if there exists any dictionary word that starts with `prefix`.

        Arguments:
            prefix (str): The uppercase candidate prefix built during DFS.

        Returns:
            bool: True if `prefix` is a prefix of at least one dictionary word;
                  False otherwise.

        Notes:
            - Runs in O(len(prefix)) by traversing the trie.
            - If the trie is not built or empty, returns False for any non-empty prefix.
        """
        if not prefix:
            return True  # empty string is trivially a prefix
        if self._trie_root is None:
            return False
        node = self._trie_root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def _trie_has_word(self, word):
        """
        Purpose:
            Check if `word` is exactly a dictionary word.

        Arguments:
            word (str): The uppercase candidate word built during DFS.

        Returns:
            bool: True if `word` is exactly in the dictionary; False otherwise.

        Notes:
            - Runs in O(len(word)) by traversing the trie.
        """
        if not word or self._trie_root is None:
            return False
        node = self._trie_root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_word

    def getSolution(self):
        """
        Purpose:
            Return the list of found words. In later steps, this will:
              - Validate inputs again
              - Build prefixes
              - Run DFS over the board to find all valid words
            For Step 1, it only returns an empty list because search is not implemented yet.

        Arguments:
            None

        Returns:
            list[str]: Found words (currently empty until search is implemented).
        """

        if self._n == 0 or not self.grid or self._neighbors is None:
            return []
        # We need either a trie or a non-empty dictionary to search
        if self._trie_root is None or not self.dictionary:
            return []


        found = set()  # use a set to avoid duplicates
        visited = set()  # reused per path

        # DFS from every starting cell
        for r in range(self._n):
            for c in range(self._n):
                self._dfs_trie_node(r, c,self._trie_root, [], visited, found)
 
        # Store and return a stable, sorted list
        self.solution = sorted(found)
        return self.solution

    def _dfs_trie_node(self, r, c, node, parts, visited, found):
        """
        Purpose:
            Optimized DFS that carries the current Trie node to avoid recomputing
            prefix checks. For the tile at (r, c), we attempt to follow its letters
            through `node.children` one by one. If any letter is missing, we prune.

        Arguments:
            r (int): Current row.
            c (int): Current column.
            node (TrieNode): Current position in the Trie representing the path so far.
            parts (list[str]): Accumulated tile strings (we join them only when needed).
            visited (set[tuple[int,int]]): Coordinates visited in the current path.
            found (set[str]): Accumulates discovered words.

        Returns:
            None (results are recorded in `found`).
        """
        # Attempt to consume this tile's letters from the current node.
        # Note: A tile may contribute multiple letters (e.g., "QU").
        tile = self.grid[r][c]
        next_node = node
        
        for ch in tile:
            if ch not in next_node.children:
                return  # prune: current prefix cannot lead to any word
            next_node = next_node.children[ch]

        # Tile accepted; update path
        parts.append(tile)

        # If the trie node marks a full word and total length >= 3, record it
        # Compute total length efficiently
        total_len = sum(len(p) for p in parts)
        if total_len >= 3 and next_node.is_word:
            found.add(''.join(parts))

        # Mark cell as visited and explore neighbors
        visited.add((r, c))
        for (nr, nc) in self._neighbors[r][c]:
            if (nr, nc) not in visited:
                self._dfs_trie_node(nr, nc, next_node, parts, visited, found)
        visited.remove((r, c))

        # Backtrack: remove last tile
        parts.pop()


class TrieNode:
    """
    Purpose:
        Represents a single node in a Trie (prefix tree).
        Each node stores:
          - children: mapping from uppercase letter -> TrieNode
          - is_word: whether this node terminates a full dictionary word

    Arguments:
        None

    Returns:
        A new TrieNode with empty children and is_word=False.
    """
    def __init__(self):
        self.children = {}   # dict: char -> TrieNode
        self.is_word = False
    

'''
def _expect_equal(name, actual, expected):
    """
    Purpose:
        Compare actual vs expected (as sorted lists) and print result.
    Arguments:
        name (str): Test name for display.
        actual (list[str]): Actual results from getSolution().
        expected (list[str]): Expected results.
    Returns:
        None
    """
    a = sorted(actual)
    e = sorted(expected)
    ok = (a == e)
    print("[{}] {}".format("PASS" if ok else "FAIL", name))
    if not ok:
        print("  Expected: {}".format(e))
        print("  Got     : {}".format(a))
    # Spacer for readability
    # print("")


def run_edge_case_tests():
    """
    Purpose:
        Execute a series of edge case tests for the Boggle solver.
        This assumes the Boggle class is defined in this file.
    Arguments:
        None
    Returns:
        None
    """
    print("=== Running Edge Case Tests ===")

    # 1) Empty grid -> []
    grid = []
    dictionary = ["ABC"]
    game = Boggle(grid, dictionary)
    _expect_equal("Empty grid", game.getSolution(), [])

    # 2) Non-square grid -> []
    grid = [["A", "B", "C"],
            ["D", "E", "F"]]
    dictionary = ["ABC", "DEF"]
    game = Boggle(grid, dictionary)
    _expect_equal("Non-square grid", game.getSolution(), [])

    # 3) Non-string tile -> []
    grid = [["A", 5],
            ["C", "D"]]
    dictionary = ["ACD"]
    game = Boggle(grid, dictionary)
    _expect_equal("Non-string tile in grid", game.getSolution(), [])

    # 4) Empty tile -> []
    grid = [["A", ""],
            ["C", "D"]]
    dictionary = ["ACD"]
    game = Boggle(grid, dictionary)
    _expect_equal("Empty tile in grid", game.getSolution(), [])

    # 5) Non-alphabetic tile -> []
    grid = [["A", "*"],
            ["C", "D"]]
    dictionary = ["ACD"]
    game = Boggle(grid, dictionary)
    _expect_equal("Non-alphabetic tile in grid", game.getSolution(), [])

    # 6) Empty dictionary -> []
    grid = [["A", "B"],
            ["C", "D"]]
    dictionary = []
    game = Boggle(grid, dictionary)
    _expect_equal("Empty dictionary", game.getSolution(), [])

    # 7) Dictionary with only invalid/short/non-strings -> []
    grid = [["A", "B"],
            ["C", "D"]]
    dictionary = ["a", "ab", 42, None, ""]
    game = Boggle(grid, dictionary)
    _expect_equal("Dictionary only short/invalid", game.getSolution(), [])

    # 8) Normalization: mixed-case grid/dict; words < 3 excluded
    grid = [["a", "b"],
            ["c", "d"]]
    dictionary = ["A", "Ac", "acb", "DE"]  # "A" and "Ac" too short; "ACB" is findable
    game = Boggle(grid, dictionary)
    _expect_equal("Normalization & min length", game.getSolution(), ["ACB"])

    # 9) Diagonal adjacency allowed (C->A->T along diagonal)
    grid = [["C", "X", "X"],
            ["X", "A", "X"],
            ["X", "X", "T"]]
    dictionary = ["CAT", "CA", "AT"]  # Only "CAT" should appear (len>=3)
    game = Boggle(grid, dictionary)
    _expect_equal("Diagonal adjacency", game.getSolution(), ["CAT"])

    # 10) No tile reuse within a path: "ABA" should NOT appear (only one A exists)
    grid = [["A", "B"],
            ["X", "X"]]
    dictionary = ["ABA"]
    game = Boggle(grid, dictionary)
    _expect_equal("No tile reuse", game.getSolution(), [])

    # 11) Multi-letter tile QU (counts as 2 letters) -> "QUA" valid (len=3)
    grid = [["QU", "A"],
            ["X",  "X"]]
    dictionary = ["QUA", "QU"]  # "QU" is only len=2 so excluded; only "QUA" expected
    game = Boggle(grid, dictionary)
    _expect_equal("Multi-letter QU", game.getSolution(), ["QUA"])

    # 12) Multi-letter tile ST + neighbors -> "STAR"
    grid = [["ST", "A"],
            ["R",  "X"]]
    dictionary = ["STAR", "STA"]
    game = Boggle(grid, dictionary)
    # Both "STAR" and "STA" are len>=3; both valid
    _expect_equal("Multi-letter ST", game.getSolution(), ["STA", "STAR"])

    # 13) Multi-letter tile IE -> "TIE"
    grid = [["T", "IE"],
            ["X", "X"]]
    dictionary = ["TIE", "TI"]  # "TI" is too short; only "TIE" expected
    game = Boggle(grid, dictionary)
    _expect_equal("Multi-letter IE", game.getSolution(), ["TIE"])

    # 14) Duplicate paths to same word -> output only one instance
    grid = [["A", "R", "T"],
            ["A", "R", "T"],
            ["X", "X", "X"]]
    dictionary = ["ART"]
    game = Boggle(grid, dictionary)
    # Many possible paths, but only one "ART" should be returned
    _expect_equal("Duplicate paths produce unique word", game.getSolution(), ["ART"])

    # 15) Valid grid/dict but no matches -> []
    grid = [["A", "B"],
            ["C", "D"]]
    dictionary = ["ZZZ", "YYYY", "QQQ"]  # Not present
    game = Boggle(grid, dictionary)
    _expect_equal("No matches case", game.getSolution(), [])

    # 16) Special tiles should be uppercase-insensitive in input
    grid = [["qu", "a"],
            ["st", "ie"]]
    dictionary = ["QUA", "STIE"]  # "STIE" = "ST" + "IE"
    game = Boggle(grid, dictionary)
    _expect_equal("Special tiles input case-insensitive", game.getSolution(), ["QUA", "STIE"])

    print("=== Edge Case Tests Complete ===")
'''


def main():
    grid = [["A", "B", "C", "D"],
            ["E", "F", "G", "H"], 
            ["IE", "J", "K", "L"], 
            ["A", "B", "C", "D"]]

    dictionary = ["ABEF", "AFJIEEB", "DGKD", "DGKA"]

    mygame = Boggle(grid, dictionary)
    print(mygame.getSolution())   # <-- use getSolution(), do NOT call .solution()


if __name__ == "__main__":
    main()

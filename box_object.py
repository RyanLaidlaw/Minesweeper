class Box:
    """
    Represents a single box in the Minesweeper board.

    Attributes:
        content (str): The content of the box (None, Number, Mine, Flag).
        mine_neighbor_count (int): The number of mines a box is touching
        is_covered (bool): If the box has been revealed or not
        has_flag (bool): If the box has a flag or not
    """
    def __init__(self):
        self.content = None 
        self.mine_neighbor_count = 0
        self.is_covered = True
        self.has_flag = False
    
    def fill_with_mine(self):
        self.content = 'Mine'
    
    def is_mine(self) -> bool:
        return self.content == 'Mine'
    
    def set_number(self):
        self.content = 'Number'
    
    def is_number(self) -> bool:
        return self.content == 'Number'
    
    def clear_box(self):
        self.content = None
    
    def is_covered(self) -> bool:
        return self.is_covered
    
    def uncover(self):
        self.is_covered = False
    
    def cover(self):
        self.is_covered = True

    def increment_mine_neighbor_count(self):
        self.mine_neighbor_count += 1
    
    def decrement_mine_neighbor_count(self):
        self.mine_neighbor_count -= 1
    
    def get_mine_neighbor_count(self) -> int:
        return self.mine_neighbor_count
    
    def set_flag(self, flag):
        self.has_flag = flag
    
    def is_flag(self) -> bool:
        return self.content == 'Flag'

    def get_content(self) -> str:
        return self.content

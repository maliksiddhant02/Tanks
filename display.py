from support import *

# Display helper components, you can probably ignore these ---------------------
class DisplayException(Exception):
    """
    Custom exception so as not to accidentally trip any except statements one 
    may use. Consumes the current DisplayElement in addition to message in
    order to provide a useful stack trace.
    """
    def __init__(self, curr_element: "TextDisplayElement", message: str, 
                 *args, **kwargs):
        super().__init__(curr_element.get_trace() + message, *args, **kwargs)

class TextDisplayElement():
    """
    Base (Abstract) text gui element to display a rectangular block of text.
    Display works based on list of strings. String represents the content of a 
    row (top to bottom). The render method returns the block of text to display 
    this element. content will be justified so it is always the width and height
    specified by get_width and get_height respectively. If width and height
    are not specified, then width and height stretch to the longest column/row
    respectively. The display method prints render content. 

    The intention is for TextDisplayElement child classes to nest one-another
    in order to more easily lay out a text based GUI. This generally should be 
    achieved by the render method of an encompassing element calling the render 
    element of its nested elements before stitching the resulting content 
    together, calling its own justify method on the result, and returning.
    Elements should not change parent after construction.

    This class should not be instantiated directly, and should instead be 
    subclassed. Subclasses should override the render method with intended 
    functionality.
    """

    # Justification settings
    VJUST_TOP = "top"
    VJUST_BOTTOM = "bottom"
    VJUST_CENTER = "center" #if even sides left
    HJUST_LEFT = "left"
    HJUST_RIGHT = "right"
    HJUST_CENTER = VJUST_CENTER # if even sides top

    def __init__(self, 
                 parent: "TextDisplayElement | None",
                 width: int | None = None, 
                 height: int | None = None,
                 vjust: str = VJUST_CENTER,
                 hjust: str = HJUST_CENTER
    ):
        """
        Initialises a new TextDisplayElement.

        Args:
            parent (TextDisplayElement | None): Element this element is 
                    nested inside of, for the purpose of error tracing. Should 
                    not be changed after construction.
            width (int | None): Fixed width, or None to stretch to 
                    widest row. Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch 
                    to number of rows in content. Optional; Defaults to None.
            vjust (str): Vertical content justification.
                    Can either be "top", "bottom" or "center". Optional; 
                    Defaults to "center".
            hjust (str): Horizontal content justification. 
                    Can either be "left", "right" or "center".
                    Optional; Defaults to "center".
        """
        self._parent = parent
        self._fixwidth = width
        self._fixheight = height

        self.set_vjust(vjust)
        self.set_hjust(hjust)
        self._content = [] # Arbitrary element. Should be overriden in children.

    def get_content(self) -> list[str]:
        """
        Return this element's current content.

        Returns:
            list[str]: Content.
        """
        return self._content

    def get_parent(self) -> "TextDisplayElement":
        """
        Returns the parent of this element. Useful for stack tracing.

        Returns:
            TextDisplayElement: The element that this element is currently 
                    nested in.
        """
        return self._parent

    def set_width(self, width: int | None = None):
        """
        Set or remove fixed width. Removing fixed width means width stretches to
        widest row.

        Args:
            width (int | None): New fixed width, or None to remove 
                    fixed width. Optional; Defaults to None.
        """
        self._fixwidth = width

    def get_width(self) -> int:
        """
        Returns current content width.

        Returns:
            int: current content width.
        """
        if self._fixwidth:
            return self._fixwidth
        else:
            return max((len(row) for row in self._content), default= 0)
    
    def set_height(self, height: int | None = None):
        """
        Set or remove fixed height. Removing fixed height means height stretches 
        to number of content rows.

        Args:
            height (int | None): New fixed height, or None to 
                    remove fixed height. Optional; Defaults to None.
        """
        self._fixheight = height

    def get_height(self) -> int:
        """
        Returns current content height.

        Returns:
            int: current content height.
        """
        if self._fixheight:
            return self._fixheight
        else:
            return len(self._content)
        
    def set_vjust(self, vjust: str):
        if vjust not in (self.VJUST_TOP, self.VJUST_CENTER, self.VJUST_BOTTOM):
            raise DisplayException(self, 
                            "invalid vertical justification, please use "+ 
                             f"'{self.VJUST_TOP}', " +
                             f"'{self.VJUST_CENTER}', or " +
                             f"'{self.VJUST_BOTTOM}'"
            )
        self._vjust = vjust

    def set_hjust(self, hjust: str):
        if hjust not in (self.HJUST_LEFT, self.HJUST_CENTER, self.HJUST_RIGHT):
            raise DisplayException(self, 
                            "invalid horizontal justification, please use "+ 
                             f"'{self.HJUST_LEFT}', " +
                             f"'{self.HJUST_CENTER}', or " +
                             f"'{self.HJUST_RIGHT}'"
            )
        self._hjust = hjust
    
    def justify(self, content: list[str]) -> list[str]:
        """
        Return copy of given content padded such that it is rectangular with 
        the correct width and height. Content is justified according to the given
        justification settings.

        Args:
            content (list[str]): Content to pad/justifiy

        Raises:
            DisplayException: If content is too wide/tall for current fixed 
                    width/height

        Returns:
            list[str]: Padded and justified copy of given content.
        """
        # pad content horizonally
        to_render = []
        for line in content:
            hdiff = self.get_width() - len(line)
            if hdiff < 0:
                raise DisplayException(self, "Content too wide!")
            if self._hjust == self.HJUST_LEFT:
                to_render.append(line + (" " * hdiff))
            elif self._hjust == self.HJUST_RIGHT:
                to_render.append((" " * hdiff) + line)
            elif self._hjust == self.HJUST_CENTER:
                lpad = hdiff // 2
                rpad = hdiff - lpad
                to_render.append((" " * lpad) + line + (" " * rpad))

        # pad content vertically
        vdiff = self.get_height() - len(to_render)
        if vdiff < 0:
            raise DisplayException(self, "Content too tall!")
        if self._vjust == self.VJUST_TOP:
            to_render += [" " * self.get_width()] * vdiff
        elif self._vjust == self.VJUST_BOTTOM:
            to_render = ([" " * self.get_width()] * vdiff) + to_render
        elif self._vjust == self.VJUST_CENTER:
            tpad = vdiff // 2
            bpad = vdiff - tpad
            to_render = ([" " * self.get_width()] * tpad) + \
                    to_render + \
                    ([" " * self.get_width()] * bpad)
        
        return to_render
        
    def render(self) -> list[str]:
        """
        Return content that should be printed to display the content of this
        TextDisplayElement

        Returns:
            list[str]: Content to display. Each string in the given list is a 
                    row of content. The list is ordered with the first string 
                    being the topmost row, and the last string being the 
                    bottommost.

        """
        return self.justify(self.get_content())
    
    def display(self):
        """
        Print this TextDisplayElement to the screen.
        """
        print(str(self))

    def __str__(self): # For easier debugging
        return "\n".join(self.render())

    def __repr__(self): # For even easier debugging (and because I am lazy)
        return str(self)
    
    def get_trace(self) -> str:
        """
        Constructs the trace of nested elements that ends with this element.
        Used to see exactly what is throwing a given display error.

        Returns:
            str: String for use within DisplayExceptions to identify this 
                    element.
        """
        trace = f"{self.__class__.__name__} > "
        if self.get_parent():
            trace = self.get_parent().get_trace() + trace
        return trace


class BaseDisplay(TextDisplayElement):
    """
    Basic text display element. Takes manually specified content and displays it.
    """
    def __init__(self,
                 parent: TextDisplayElement | None,
                 content: list[str] | None = None, 
                 width: int | None = None, 
                 height: int | None = None, 
                 vjust: str = TextDisplayElement.VJUST_CENTER, 
                 hjust: str = TextDisplayElement.HJUST_CENTER
    ):
        """
        Initialises a BaseDisplay element.

        Args:
            parent (TextDisplayElement | None): Element this element is 
                    nested inside of, for the purpose of error tracing. Should 
                    not be changed after construction.
            content (list[str] | None): content to display, 
                    or None for empty content. Optional; Defaults to None.
            width (int | None): Fixed width, or None to stretch to content. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to content. 
                    Optional; Defaults to None.
            vjust (str): vertical justification setting. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): horizonatal justification setting. Can either be 
                    "left", "right" or "center". Optional; Defaults to "center".
        """
        super().__init__(parent, width, height, vjust, hjust)
        self._content = content if content else []

    def set_content(self, content: list[str]):
        """
        Set content to display.

        Args:
            content (list[str]): Content to display.
        """
        self._content = content

    def wrap_text(self, text: str) -> list[str]:
        """
        Attempts to break a given string into rows that would fit
        within this BaseDisplay element (breaking on spaces).
        Helpful for displaying arbitrary content. This will behave weirdly
        without a set width.

        Args:
            text (str): String to break into lines

        Returns:
            list[str]: Content containing string broken into lines that should
                    Fit within this TextDisplay element.
        """
        wrapped = []
        remaining = text
        while len(remaining) > self.get_width():
            # find space to break on
            space = remaining.rfind(" ", 0, self.get_width())
            wrapped.append(remaining[0:space])
            remaining = remaining[space+1:]
            if space == -1:
                break # give up and deal with consequences later
        wrapped.append(remaining)
        return wrapped
        

class VSplitDisplay(TextDisplayElement):
    """
    TextDisplayElement that displays the content of several TextDisplayElements
    in a vertical stack (top to bottom). Can be indexed directly to access 
    contained TextDisplayElements. Components should be added after construction
    via the .components() method or directly using the .append() method in order 
    to preserve parent assignment workflow.
    """
    def __init__(self, 
                 parent: TextDisplayElement | None,
                #  components: list[TextDisplayElement], # Breaks parent rel
                 width: int | None = None, 
                 height: int | None = None, 
                 vjust: str = TextDisplayElement.VJUST_CENTER, 
                 hjust: str = TextDisplayElement.HJUST_CENTER
    ):
        """
        Initialises a new VSplitDisplayElement.

        Args:
            parent (TextDisplayElement | None): Element this element is 
                    nested inside of, for the purpose of error tracing. Should 
                    not be changed after construction.
            width (int | None): Fixed width, or None to stretch to content. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to content. 
                    Optional; Defaults to None.
            vjust (str): vertical justification setting. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): horizonatal justification setting. Can either be 
                    "left", "right" or "center". Optional; Defaults to "center".
        """
        super().__init__(parent, width, height, vjust, hjust)
        self._components: list[TextDisplayElement] = []

    def components(self) -> list[TextDisplayElement]:
        """
        Return a reference to the list of displayed TextDisplayElements.

        Returns:
            list[TextDisplayElement]: displayed TextDisplayElements.
        """
        return self._components
    
    def __getitem__(self, index: int) -> TextDisplayElement:
        return self._components[index]

    def append(self, component: TextDisplayElement):
        """
        Directly append the given component to this display.

        Args:
            component (TextDisplayElement): Component to append.
        """
        self._components.append(component)

    def remove(self, component: TextDisplayElement):
        """
        Directly remove the given component to this display.

        Args:
            component (TextDisplayElement): Component to remove.
        """
        self._components.remove(component)

    def insert(self, index: int, component: TextDisplayElement):
        """
        Directly insert component at the specified index.

        Args:
            index (int): Index at which to insert.
            component (TextDisplayElement): Component to insert.
        """
        self._components.insert(index, component)

    def pop(self, index: int) -> TextDisplayElement:
        """
        Directly pop component at the specified index.

        Args:
            index (int): Index at which to pop.
        
        Returns:
            component (TextDisplayElement): popped component.
        """
        return self._components.pop(index)
    
    def index(self, component: TextDisplayElement) -> int:
        """
        Directly retrieve index of given component

        Args:
            component (TextDisplayElement): Component to grab index of.

        Returns:
            int: Index of component, or -1 if not found
        """
        return self._components.index(component)

    def get_width(self) -> int:
        if self._fixwidth:
            return self._fixwidth
        else:
            return max(
                (component.get_width() for component in self._components), 
                default= 0
            )
        
    def get_height(self) -> int:
        if self._fixheight:
            return self._fixheight
        else:
            return sum(
                (component.get_height() for component in self._components)
            )

    def render(self):
        content_stack = []
        for component in self._components:
            content_stack += component.render()
        return self.justify(content_stack)
    

class HSplitDisplay(TextDisplayElement):
    """
    TextDisplayElement that displays the content of several TextDisplayElements
    in a horizontal stack (left to right). Can be indexed directly to access 
    contained TextDisplayElements. Components should be added after construction
    via the .components() method or directly using the .append() method in order 
    to preserve parent assignment workflow.
    """
    def __init__(self, 
                 parent: TextDisplayElement | None,
                #  components: list[TextDisplayElement], # Breaks parent rel
                 width: int | None = None, 
                 height: int | None = None, 
                 vjust: str = TextDisplayElement.VJUST_CENTER, 
                 hjust: str = TextDisplayElement.HJUST_CENTER
    ):
        """
        Initialises a new HSplitDisplayElement.

        Args:
            parent (TextDisplayElement | None): Element this element is 
                    nested inside of, for the purpose of error tracing. Should 
                    not be changed after construction.
            components (list[TextDisplayElement]): TextDisplayElements to 
                    display, ordered left to right.
            width (int | None): Fixed width, or None to stretch to  content. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to content. 
                    Optional; Defaults to None.
            vjust (str): vertical justification setting. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): horizonatal justification setting. Can either be 
                    "left", "right" or "center". Optional; Defaults to "center".
        """
        super().__init__(parent, width, height, vjust, hjust)
        self._components: list[TextDisplayElement] = []

    def components(self) -> list[TextDisplayElement]:
        """
        Return a reference to the list of displayed TextDisplayElements.

        Returns:
            list[TextDisplayElement]: displayed TextDisplayElements.
        """
        return self._components
    
    def __getitem__(self, index: int) -> TextDisplayElement:
        return self._components[index]
    
    def append(self, component: TextDisplayElement):
        """
        Directly append the given component to this display.

        Args:
            component (TextDisplayElement): Component to append.
        """
        self._components.append(component)

    def remove(self, component: TextDisplayElement):
        """
        Directly remove the given component to this display.

        Args:
            component (TextDisplayElement): Component to remove.
        """
        self._components.remove(component)

    def insert(self, index: int, component: TextDisplayElement):
        """
        Directly insert component at the specified index.

        Args:
            index (int): Index at which to insert.
            component (TextDisplayElement): Component to insert.
        """
        self._components.insert(index, component)

    def pop(self, index: int) -> TextDisplayElement:
        """
        Directly pop component at the specified index.

        Args:
            index (int): Index at which to pop.
        
        Returns:
            component (TextDisplayElement): popped component.
        """
        return self._components.pop(index)
    
    def index(self, component: TextDisplayElement) -> int:
        """
        Directly retrieve index of given component

        Args:
            component (TextDisplayElement): Component to grab index of.

        Returns:
            int: Index of component, or -1 if not found
        """
        return self._components.index(component)
    

    def get_width(self) -> int:
        if self._fixwidth:
            return self._fixwidth
        else:
            return sum((component.get_width() for component in self._components))
        
    def get_height(self) -> int:
        if self._fixheight:
            return self._fixheight
        else:
            return max(
                (component.get_height() for component in self._components), 
                default= 0
            )

    def render(self):
        to_render = ["" for _ in range(self.get_height())]

        for component in self._components:
            new_content = component.render()
            # will need to pad vertically early
            vdiff = self.get_height() - len(new_content)
            if vdiff < 0:
                raise DisplayException(self, "Component is too tall!")
            if self._vjust == self.VJUST_TOP:
                new_content += [" " * component.get_width()] * vdiff
            elif self._vjust == self.VJUST_BOTTOM:
                new_content = [" " * component.get_width()] * vdiff + new_content
            elif self._vjust == self.VJUST_CENTER:
                tpad = vdiff // 2
                bpad = vdiff - tpad
                new_content = [" " * component.get_width()] * tpad + \
                        new_content + \
                        [" " * component.get_width()] * bpad
            
            #stitch lines together
            for line in range(self.get_height()):
                to_render[line] += new_content[line]

        return self.justify(to_render)

class AbstractGrid(VSplitDisplay):
    """
    Text Display element that maintains a grid layout (which you will find 
    useful often...). Named after Ashleigh's ever faithful Canvas wiget that was
    sunset along with the GUI third of the course, paving the way for this
    monstrosity. Requires a fixed width and height to function (but does not 
    need to be square). 
    
    If the specified width or height is not equally
    divisible by the grid size, then the division rounds down, and the grid is 
    centered in the allocated space. Instead of the usual justification options,
    specify if (in the event of a rectangular width + height) you want the grid
    cells to be square based on the shorter measurement (square) or stretch to
    be rectangular (stretch). Cells are all BaseDisplay elements set to center 
    content.

    Can be indexed directly [row][column] to access the cells, 
    equivilantly use the get_cell method.

    Important Note: Resizing the grid, or changing the number of rows/collumns 
    will wipe all content as the grid is reconstructed. 
    """

    # Alternate justification constants.
    GRID_SQUARE = "square"
    GRID_STRETCH = "stretch"

    def __init__(self, 
                 parent: TextDisplayElement | None,
                 dims: tuple[int, int], #row col
                 width: int, 
                 height: int, 
                 just: str = GRID_SQUARE
    ):
        """
        Initialise a new AbstractGrid component.

        Args:
            parent (TextDisplayElement | None): Element this element is 
                    nested inside of, for the purpose of error tracing. Should 
                    not be changed after construction.
            dims (tuple[int, int]): dimensions of grid (rows, columns)
            width (int): fixed width.
            height (int): fixed height.
            just (str): How grid should behave if width and height 
                are not equal. Can be either "square" or "stretch". Optional; 
                Defaults to "square".
        """
        super().__init__(parent, width, height)

        self._FIXED_GEO_ERR = DisplayException(
            self, "Grid must have fixed geometry") # Requires instance

        if not width and height:
            raise self._FIXED_GEO_ERR
        
        if just not in (self.GRID_SQUARE, self.GRID_STRETCH):
            raise DisplayException(self, 
                            "invalid grid justification, please use "+ 
                             f"'{self.GRID_SQUARE}', or" +
                             f"'{self.GRID_STRETCH}'"
            )
        self._grid_just = just
        self.set_dims(dims)

    def set_width(self, width: int): # warning: wipes
        if not width:
            raise self._FIXED_GEO_ERR
        super().set_width(width)
        self.set_dims(self._dims) # Reconstruct grid with new geometry
    
    def set_height(self, height: int):
        if not height:
            raise self._FIXED_GEO_ERR
        super().set_height(height)
        self.set_dims(self._dims) # Reconstruct grid with new geometry

    def get_dims(self) -> tuple[int, int]: # warning: wipes
        """
        Return grid dimensions.

        Returns:
            tuple[int, int]: (row, column) dimensions.
        """
        return self._dims

    def set_dims(self, dims: tuple[int, int]): #Warning, wipes content
        """
        Set dimensions and reconstruct grid using them (wiping content)

        Args:
            dims (tuple[int, int]): new grid dimensions (rows, columns)
        """
        self._dims = dims

        # Determine cell dims
        cell_height = self._fixheight // dims[0]
        cell_width = self._fixwidth // dims[1]

        self.components().clear()
        for _ in range(dims[0]):
            if self._grid_just == self.GRID_SQUARE:
                min_dim = min(cell_height, cell_width)
                cell_height = min_dim
                cell_width = min_dim

            row = HSplitDisplay(self, width=self.get_width(), 
                                height = cell_height)
            for _ in range(dims[1]):
                row.append(BaseDisplay(row, width=cell_width, 
                            height=cell_height))
                
            self.append(row)

    def get_cell(self, row: int, col: int) -> BaseDisplay:
        """
        Return the BaseDisplay cell at the given coordinate.

        Args:
            row (int): row index
            col (int): column index

        Returns:
            BaseDisplay: BaseDisplay element at cell.
        """
        return self[row][col]
# ------------------------------------------------------------------------------

DISPLAY_WIDTH = 80

TILE_MAP = {
    TILE_ID: ["?"], 
    FLOOR_ID: [], # Will be rendered as blank
    WALL_ID: ["+-+",
              "| |",
              "+-+"],
    ROCK_ID: ["##/",
              "#/#",
              "/##"],
    DESTROYED_ID: [], # Will be rendered as blank
}
TANK_MAP = {
    (-1, 0): [" ^ ", # Up
              "[ ]",
              "   "],
    (1, 0): ["   ", # Down
             "[ ]",
             " v "],
    (0, -1): ["   ", # Left
              "< ]",
              "   ",],
    (0, 1): ["   ", # Right
             "[ >",
            "   ",],    
}

def get_tank_display(heading: Heading, id: str) -> list[str]:
    """
    Helper to return the appropriate tank display.

    Preconditions: heading in the keyset of TANK_MAP; id is a single character.

    Args:
        heading (Heading): heading of tank to display.
        id (str): Character denoting the type of tank.

    Returns:
        str: 3x3 display composed of display with the center replaced with id.
    """
    display = TANK_MAP[heading].copy() # Copy as mutating
    display[1] = display[1][0] + id + display[1][2]
    return display
    



class BattlefieldView(AbstractGrid):
    """
    View component to display the game grid with entities on it.
    """
    CELL_SIZE = 3

    def __init__(self, parent: TextDisplayElement):
        """
        Initialise new BattlefieldView

        Args:
            parent (TextDisplayElement): Element this view is sitting in.
        """

        # Dummy initial dims, will be filled out upon adding tiles.
        super().__init__(parent, (1,1), 1, 1, AbstractGrid.GRID_SQUARE)

    def draw_tiles(self, tiles: list[list["Tile"]]):
        """
        Draws the current set of tiles ready for render.

        Precondition: tiles actually contains at least one tile.

        Args:
            tiles (list[list[Tile]]): Array of tiles structured into 
            rows.
        """

        # Reconfigure Size (Wiping existing content)
        rows = len(tiles)
        cols = max(len(row) for row in tiles) # Ideally things are rectangular.
        self.set_height(rows * self.CELL_SIZE)
        self.set_width(cols * self.CELL_SIZE)
        self.set_dims((rows, cols)) 

        # Actually draw
        for i,row in enumerate(tiles):
            for j,tile in enumerate(row):
                self.get_cell(i,j).set_content(TILE_MAP[str(tile)])

    def draw_entities(self, player: "Player", enemies: list["Enemy"]):
        """
        Draws entities on top of existing tiles. 
        
        Modifies existing display content, and thus assumes draw_tiles has been 
        called first. Player is drawn first, then enemies in order of priority
        (In case of overlap). Precondition: all entities to be drawn exist on 
        battlefield.

        Args:
            player (Player): Player to draw.
            enemies (list[Creature]): enemies to draw.
        """

        for tank in [player] + enemies:
            self.get_cell(*tank.get_position()).set_content(
                    get_tank_display(tank.get_heading(), tank.get_id())
            )

class StatView(HSplitDisplay):
    """
    Displays the player's current armour and remaining enemies.
    """
    STAT_HEIGHT = BattlefieldView.CELL_SIZE + 2
    ICON = "[P]"

    def __init__(self, parent: TextDisplayElement, width: int):
        """
        Initialise a new stats view

        Args:
            parent (TextDisplayElement): Parent of this statbar
            width (int): Allocated width
        """
        super().__init__(parent, width, self.STAT_HEIGHT, 
                         TextDisplayElement.VJUST_CENTER, 
                         TextDisplayElement.HJUST_CENTER)
        
        # Layout Bar
        left = HSplitDisplay(self, width//2, 
                             hjust = TextDisplayElement.HJUST_LEFT)
        icon = BaseDisplay(left, [self.ICON], width = self.STAT_HEIGHT)
        left.append(icon)
        self._armour_display = BaseDisplay(left) # want a handle on this
        left.append(self._armour_display)
        self.append(left)

        right = HSplitDisplay(self, width//2, 
                             hjust = TextDisplayElement.HJUST_RIGHT)
        self._enemy_display = BaseDisplay(right) # also want handle on this
        right.append(self._enemy_display)
        spacer = BaseDisplay(right, width=BattlefieldView.CELL_SIZE)
        right.append(spacer)
        self.append(right)

    def draw_stats(self, armour: int, enemy_count: int):
        """
        Draw the given game stats.

        Args:
            armour (int): Player's current armour.
            enemy_count (int): Remaining enemies.
        """
        self._armour_display.set_content(
            [f"Armour: {armour}"]
        )
        self._enemy_display.set_content(
            [f"Enemy Tanks Remaining: {enemy_count}"]
        )

class WTView(VSplitDisplay):
    """
    View class that displays a game of We Tank in a visually appealing format.
    """
    def __init__(self):
        """
        Initialise a new Keys and enemies view class
        """
        super().__init__(None, DISPLAY_WIDTH, 
                         vjust= TextDisplayElement.VJUST_TOP)
        banner = BaseDisplay(self, [
            "-"*DISPLAY_WIDTH,
            "We Tank!",
            "-"*DISPLAY_WIDTH,
        ])
        self.append(banner)
        self._battlefield = BattlefieldView(self)
        self.append(self._battlefield)
        self._stats = StatView(self, DISPLAY_WIDTH)
        self.append(self._stats)

    def draw_game(self, 
                    tiles: list[list["Tile"]], 
                    player: "Player",
                    enemies: list["Enemy"]
    ):
        """
        Print the current game state in a visually appealing format.

        If multiple entities exist at the same position, the draw order is the 
        player followed by each enemy in descending priority order.
        Preconditions: tiles contains at least one tile; and all tanks (player 
        and enemy) exist at positions that exist under the given set of tiles.

        Args:
            tiles (list[list[Tile]]): The structured set of tiles that compose 
                    the current Battlefield. 
            player (Player): The current player.
            enemies (list[Creature]): List of enemies that are currently 
                    alive within the game, in descending priorty order.
        """
        self._battlefield.draw_tiles(tiles)
        self._battlefield.draw_entities(player, enemies)
        self._stats.draw_stats(player.get_armour(), len(enemies))
        self.display()

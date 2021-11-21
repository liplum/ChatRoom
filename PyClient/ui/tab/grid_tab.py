import keys
from ui import panels as panels
from ui.controls import button
from ui.panels import gen_grid, column, stack
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox


class grid_tab(tab):

    def __init__(self, client: "client", tablist: tablist):
        super().__init__(client, tablist)
        self.grid = gen_grid(3, [column(15), column(20), column(18)])
        self.grid.on_content_changed.add(lambda _: self.client.mark_dirty())
        l1_1 = label("Label 1 1")
        l1_2 = label("Label 1 2")
        l2_1 = label("Label 2 1")
        l2_2 = label("Label 2 2")
        account_tbox = xtextbox(excepted_chars={keys.k_enter})
        account_tbox.space_placeholder = "_"
        account_stack = stack()
        account_stack.over_range = panels.expend
        account_stack.add(label("Account"))
        account_stack.add(account_tbox)
        account_stack.orientation = panels.horizontal
        b = button("Button", lambda: None)
        b.margin = 2
        # self.grid[0, 0] = account_stack
        self.grid[0, 0] = l1_1
        self.grid[0, 1] = button("A", lambda: None)
        self.grid[0, 2] = button("Button B", lambda: None)

        self.grid[1, 0] = l2_1
        self.grid[1, 1] = b
        self.grid[1, 2] = button("A", lambda: None)

        self.grid[2, 0] = label("Label 3 1")
        self.grid[2, 1] = button("A", lambda: None)
        self.grid[2, 2] = button("Close", lambda: self.client.stop())

        self.grid.elemt_interval_w = 5
        self.grid.elemt_interval_h = 1
        self.grid.left_margin = 15
        self.grid.top_margin = 3
        self.grid.switch_to_first_or_default_item()

    def draw_on(self, buf: buffer):
        self.grid.draw_on(buf)

    @property
    def title(self) -> str:
        return "grid tab"

    def on_input(self, char: chars.char):
        consumed = self.grid.on_input(char)
        if not consumed:
            if keys.k_down == char:
                self.grid.switch_to_first_or_default_item()


add_tabtype("grid_tab", grid_tab)

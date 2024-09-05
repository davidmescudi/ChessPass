class Menu:
    def __init__(self, display):
        self.display = display
        self.menu_items = ["Initialize", "Item 2", "Revoke Key"]
        self.submenu_items = ["Figure 1", "Figure 2", "Figure 3"] # later use stored keys to identify figures
        self.current_menu = self.menu_items
        self.selected_index = 0
        self.in_submenu = False
        self.display.mark_for_refresh()

    def navigate_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.current_menu)
        self.display.mark_for_refresh()
        self.update_display()

    def navigate_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.current_menu)
        self.display.mark_for_refresh()
        self.update_display()

    def select(self):
        if self.current_menu[self.selected_index] == "Revoke Key" and not self.in_submenu:
            self.current_menu = self.submenu_items
            self.selected_index = 0
            self.in_submenu = True
        else:
            print(f"Selected {self.current_menu[self.selected_index]}")
        self.display.mark_for_refresh()
        self.update_display()

    def go_back(self):
        if self.in_submenu:
            self.current_menu = self.menu_items
            self.selected_index = 0
            self.in_submenu = False
        self.display.mark_for_refresh()
        self.update_display()

    def update_display(self):
        self.display.show_menu(self.current_menu, self.selected_index)

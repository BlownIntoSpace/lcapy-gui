from lcapygui.ui.uimodelmph import UIModelMPH


class UIModelDnD(UIModelMPH):
    def __init__(self, ui):
        super(UIModelDnD, self).__init__(ui)

    def on_add_cpt(self, cpt_key):
        """
        Adds a component to the circuit after a key is pressed

        Explanation
        ===========
        If there are cursors present, it will place a component between them
        otherwise, the component will follow the cursor until the user left clicks

        :param str cpt_key: key pressed
        """
        if self.ui.debug:
            print(f"adding component at mouse position: {self.mouse_position}")
        # Get mouse positions
        mouse_x = self.mouse_position[0]
        mouse_y = self.mouse_position[1]
        if len(self.cursors) == 0:
            # create a new component at the mouse position
            cpt = self.cpt_create(cpt_key, mouse_x - 2, mouse_y, mouse_x + 2, mouse_y)
            self.ui.refresh()

            # Select the newly created component
            self.on_select(mouse_x, mouse_y)
            self.follow_mouse = True

        else:
            # add a new cursor at the grid position closest to the mouse
            self.add_cursor(round(mouse_x), round(mouse_y))

            # add the component like normal
            super().on_add_cpt(cpt_key)

    def on_left_click(self, x, y):
        """
        Performs operations on left-click

        Explanation
        ===========
        This function is called when the user left-clicks on the canvas.
        If a component is currently being dragged, it will drop the component
        Otherwise, it selects the component at the mouse position

        Parameters
        ==========
        :param float x: x position of the mouse
        :param float y: y position of the mouse
        """
        # drop the component in place after clicking
        if self.follow_mouse:
            self.follow_mouse = False
            self.on_select(x, y)
            self.cursors.remove()
            # Add cursors to the component
            cpt = self.selected
            self.add_cursor(cpt.gcpt.node1.pos.x, cpt.gcpt.node1.pos.y)
            node2 = cpt.gcpt.node2
            if node2 is not None:
                self.add_cursor(node2.pos.x, node2.pos.y)
        else:
            super().on_left_click(x, y)

    def on_right_click(self, x, y):
        """
        performs operations on right-click

        Explanation
        ===========
        This function is called when the user right-clicks on the canvas.
        If no component is selected, it will clear the cursors from the screen.
        Otherwise, it will show the selected components properties dialogue
        :param float x: x position of the mouse
        :param float y: y position of the mouse
        """
        super().on_right_click(x, y)
        if not self.selected:
            self.unselect()




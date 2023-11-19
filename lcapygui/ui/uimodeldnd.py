from lcapygui.ui.uimodelmph import UIModelMPH


class UIModelDnD(UIModelMPH):

    def __init__(self, ui):
        super().__init__(ui)
        self.mouse_pos = (0 ,0)

    def on_add_cpt(self, cpt_key):
        """
        Adds a component to the circuit after a key is pressed
        :param cpt_key: key pressed
        :return: None
        """
        super().on_add_cpt(cpt_key)




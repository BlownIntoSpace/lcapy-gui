import numpy as np
from typing import Union
from .component import Component


class VoltageSource(Component):
    """
    VoltageSource

    Parameters
    ----------

    value: Union[str, int, float]
        The value of the voltage source.
    """

    TYPE = "V"
    NAME = "Voltage Source"
    kinds = {'DC': 'dc', 'AC': 'ac', 'Step': 'step', 'Arbitrary': ''}

    def __init__(self, value: Union[str, int, float]):

        super().__init__(value)
        self.kind = 'DC'

    def draw(self, editor, layer):

        length = self.length()

        start = self.nodes[0].position
        end = self.nodes[1].position
        mid = 0.5 * self.along() * length + start

        RADIUS = 1.2 * editor.STEP * editor.SCALE
        OFFSET = 0.5 * editor.STEP * editor.SCALE

        # lead 1
        shift = self.along() * RADIUS
        layer.stroke_line(
            start[0], start[1],
            mid[0] - shift[0], mid[1] - shift[1]
        )

        # lead 2
        layer.stroke_line(
            mid[0] + shift[0], mid[1] + shift[1],
            end[0], end[1]
        )

        # circle
        layer.stroke_arc(
            mid[0], mid[1],
            RADIUS,
            0, 2 * np.pi
        )

        # plus/minus signs
        offset = (RADIUS - OFFSET) * self.along()
        v_shift = OFFSET * self.along()
        h_shift = OFFSET * self.orthog()

        # plus
        layer.stroke_line(
            mid[0] - offset[0] + v_shift[0] /
            2, mid[1] - offset[1] + v_shift[1]/2,
            mid[0] - offset[0] - v_shift[0] /
            2, mid[1] - offset[1] - v_shift[1]/2
        )
        layer.stroke_line(
            mid[0] - offset[0] + h_shift[0] /
            2, mid[1] - offset[1] + h_shift[1]/2,
            mid[0] - offset[0] - h_shift[0] /
            2, mid[1] - offset[1] - h_shift[1]/2
        )

        # minus
        layer.stroke_line(
            mid[0] + offset[0] + h_shift[0] /
            2, mid[1] + offset[1] + h_shift[1]/2,
            mid[0] + offset[0] - h_shift[0] /
            2, mid[1] + offset[1] - h_shift[1]/2
        )

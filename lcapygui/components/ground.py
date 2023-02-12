from .connection import Connection
from numpy import array


class Ground(Connection):
    """
    Ground connection
    """

    TYPE = "A"
    NAME = "Ground"

    def __draw_on__(self, editor, layer):

        # Height of stem
        h = 0.3

        paths = [array(((0, 0), (0, -h))),
                 array(((-0.2, -h), (0.2, -h))),
                 array(((-0.1, -h - 0.1), (0.1, -h - 0.1))),
                 array(((-0.05, -h - 0.2), (0.05, -h - 0.2)))]

        spaths = self._tf(paths, 2)
        for path in spaths:
            layer.stroke_path(path)

    def net(self, connections, step=1):

        return self.name + ' ' + self.nodes[0].name + '; down, ground'

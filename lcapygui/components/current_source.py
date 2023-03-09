from .bipole import BipoleComponent


class CurrentSource(BipoleComponent):

    type = 'I'
    kinds = {'dc': 'DC', 'ac': 'AC', 'step': 'Step',
             '': 'Arbitrary', 'noise': 'Noise', 's': ''}
    default_kind = ''

    @property
    def sketch_net(self):

        return self.type + ' 1 2 ' + self.kind + ' ' + '; right'

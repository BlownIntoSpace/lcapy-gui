from tkinter import Canvas, Tk, Frame, TOP, BOTH, BOTTOM, X, Button
from tkinter.ttk import Notebook
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from os.path import basename
from ..uimodelmph import UIModelMPH
from ..uimodeldnd import UIModelDnD
from .sketcher import Sketcher
from .drawing import Drawing
from .menu import MenuBar, MenuDropdown, MenuItem, MenuSeparator
from ...sketch_library import SketchLibrary


class LcapyTk(Tk):

    SCALE = 0.01

    GEOMETRY = '1200x800'
    # Note, need to reduce height from 8 to 7.2 to fit toolbar.
    FIGSIZE = (12, 7.2)

    NAME = 'lcapy-tk'

    def __init__(self, pathnames=None, uimodel_class=None, debug=0):

        from ... import __version__

        super().__init__()

        self.debug = debug
        self.version = __version__
        self.model = None
        self.canvas = None
        self.sketchlib = SketchLibrary()
        self.dialogs = {}

        # Select the UI model based on the command line argument
        # Defaults to UIModelMPH if the model is unknown

        if uimodel_class.lower() in ['uimodeldnd', 'dnd']:
            uimodel_class = UIModelDnD
        else:
            if self.debug:
                print('unknown model:', uimodel_class)
            uimodel_class = UIModelMPH

        self.uimodel_class = uimodel_class

        if self.debug:
            print('model: ', self.uimodel_class)

        # Title and size of the window
        self.title('Lcapy-tk ' + __version__)
        self.geometry(self.GEOMETRY)

        categories = {
            'Basic': ('c', 'i', 'l', 'p', 'r', 'v', 'w'),
            'Opamp': ('opamp', 'fdopamp', 'inamp'),
            'Transistor': ('q', 'j', 'm'),
            'Dependent source': ('e', 'f', 'g', 'h'),
            'Misc.': ('y', 'cpe', 'z', 'o', 'nr'),
            'Connection': ('0', '0V', 'sground', 'rground', 'cground',
                           'vdd', 'vss', 'vcc', 'vee',
                           'input', 'output', 'bidir')
        }

        items = []
        for cat in categories:
            if cat == 'Basic':
                for key in categories[cat]:
                    val = self.uimodel_class.component_map[key]
                    acc = key if len(key) == 1 else ''
                    items.append(MenuItem(val[1], command=self.on_add_cpt,
                                          arg=key, accelerator=acc))
                items.append(MenuSeparator())
            else:
                subitems = []

                for key in categories[cat]:
                    if cat == 'Connection':
                        val = self.uimodel_class.connection_map[key]
                        cmd = self.on_add_con
                    else:
                        val = self.uimodel_class.component_map[key]
                        cmd = self.on_add_cpt
                    acc = key if len(key) == 1 else ''
                    subitems.append(MenuItem(val[1], command=cmd,
                                             arg=key, accelerator=acc))
                menu = MenuDropdown(cat, 0, subitems)
                items.append(menu)

        component_menu_dropdown = MenuDropdown('Components', 0, items)

        menudropdowns = [
            MenuDropdown('File', 0,
                         [
                             MenuItem('Clone', self.on_clone),
                             MenuItem('New', self.on_new,
                                      accelerator='Ctrl+n'),
                             MenuItem('Open', self.on_load,
                                      accelerator='Ctrl+o'),
                             MenuItem('Open library', self.on_library,
                                      underline=6, accelerator='Ctrl+l'),
                             MenuItem('Save', self.on_save,
                                      accelerator='Ctrl+s'),
                             MenuItem('Save as', self.on_save_as,
                                      underline=1, accelerator='Alt+s'),
                             MenuItem('Export', self.on_export,
                                      accelerator='Ctrl+e'),
                             MenuItem('Screenshot',
                                      self.on_screenshot, underline=1),
                             MenuItem('Quit', self.on_quit,
                                      accelerator='Ctrl+q')
                         ]),

            MenuDropdown('Edit', 0,
                         [
                             MenuItem('Preferences', self.on_preferences),
                             MenuItem('Undo', self.on_undo,
                                      accelerator='Ctrl+z'),
                             MenuItem('Cut', self.on_cut,
                                      accelerator='Ctrl+x'),
                             MenuItem('Copy', self.on_copy,
                                      accelerator='Ctrl+c'),
                             MenuItem('Paste', self.on_paste,
                                      accelerator='Ctrl+v'),
                             MenuItem('Values', self.on_edit_values,
                                      accelerator='Ctrl+V')
                         ]),

            MenuDropdown('View', 0,
                         [

                             MenuItem('Expression', self.on_expression,
                                      accelerator='Ctrl+e'),
                             MenuItem('Circuitikz image', self.on_view,
                                      accelerator='Ctrl+u'),
                             MenuItem('Circuitikz macros',
                                      self.on_view_macros),
                             MenuItem('Simple netlist',
                                      self.on_simple_netlist),
                             MenuItem('Netlist', self.on_netlist),
                             MenuItem('Nodal equations',
                                      self.on_nodal_equations),
                             MenuItem('Mesh equations',
                                      self.on_mesh_equations),
                             MenuItem('Best fit', self.on_best_fit),
                             MenuItem('Default fit', self.on_default_fit),
                             MenuItem('Plots', self.on_plots),
                             MenuItem('Description', self.on_description),
                             MenuItem('Annotation', self.on_annotation),
                             MenuItem('Circuit graph ', self.on_circuitgraph)
                         ]),

            component_menu_dropdown,
            MenuDropdown('Create', 1,
                         [
                             MenuItem('State space',
                                      self.on_create_state_space),
                             MenuItem('Transfer function',
                                      self.on_create_transfer_function),
                             MenuDropdown('Twoport', 0,
                                          [
                                              MenuItem(
                                                  'A twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'B twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'G twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'H twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'S twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'T twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'Y twoport', self.on_create_twoport),
                                              MenuItem(
                                                  'Z twoport', self.on_create_twoport)
                                          ])
                         ]),
            MenuDropdown('Inspect', 0,
                         [
                             MenuItem('Voltage', self.on_inspect_voltage),
                             MenuItem('Current', self.on_inspect_current),
                             MenuItem('Thevenin impedance',
                                      self.on_inspect_thevenin_impedance),
                             MenuItem('Norton admittance',
                                      self.on_inspect_norton_admittance),
                             MenuItem('Noise voltage',
                                      self.on_inspect_noise_voltage),
                             MenuItem('Noise current',
                                      self.on_inspect_noise_current),
                         ]),
            MenuDropdown('Manipulate', 0,
                         [
                             MenuItem('Kill independent sources',
                                      self.on_manipulate_kill),
                             MenuItem('Remove independent sources',
                                      self.on_manipulate_remove_sources),
                             MenuItem('Laplace model', self.on_laplace_model),
                             MenuItem('Noise model', self.on_noise_model),
                             MenuItem('Expand components', self.on_expand)
                         ]),
            MenuDropdown('Help', 0,
                         [
                             MenuItem('Help', self.on_help,
                                      accelerator='Ctrl+h')
                         ])
        ]

        self.menubar = MenuBar(menudropdowns)
        self.menubar.make(self)

        # Notebook tabs
        self.notebook = Notebook(self)

        self.canvases = []

        self.canvas = None

        if pathnames is None:
            pathnames = []

        for pathname in pathnames:
            try:
                self.load(pathname)
            except FileNotFoundError:
                self.new(pathname)

        if pathnames == []:
            model = self.new()

    def clear(self, grid='on'):

        self.canvas.drawing.clear(grid)

    def display(self):

        self.mainloop()

    def enter(self, canvas):

        self.canvas = canvas
        self.model = canvas.model
        self.sketcher = canvas.sketcher

        if self.debug:
            print(self.notebook.tab(self.notebook.select(), "text"))

    def load(self, pathname):

        model = self.new()

        if pathname is None:
            return

        model.load(pathname)
        self.set_filename(pathname)

    def set_filename(self, pathname):

        filename = basename(pathname)
        self.set_canvas_title(filename)

    def create_canvas(self, name, model):

        tab = Frame(self.notebook)

        canvas = Canvas(tab)
        canvas.pack(side=TOP, expand=1)

        self.notebook.add(tab, text=name)
        self.notebook.pack(fill=BOTH, expand=1)

        # Add the figure to the graph tab
        fig = Figure(figsize=self.FIGSIZE, frameon=False)
        fig.subplots_adjust(left=0, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)

        graph = FigureCanvasTkAgg(fig, canvas)
        graph.draw()
        graph.get_tk_widget().pack(fill='both', expand=True)

        drawing = Drawing(self, fig, model, self.debug)
        canvas.drawing = drawing
        canvas.tab = tab
        canvas.sketcher = Sketcher(canvas.drawing.ax, self.debug)

        tab.canvas = canvas

        self.canvases.append(canvas)

        # Display x, y position of cursor
        drawing.ax.format_coord = lambda x, y: "x:{0:.1f}, y:{1:.1f}".format(
            x, y)

        toolbar = NavigationToolbar2Tk(graph, canvas, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=BOTTOM, fill=X)

        self.notebook.select(len(self.canvases) - 1)

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_selected)

        canvas.model = model

        figure = canvas.drawing.fig
        canvas.bp_id = figure.canvas.mpl_connect('button_press_event',
                                                 self.on_click_event)

        canvas.kp_id = figure.canvas.mpl_connect('key_press_event',
                                                 self.on_key_press_event)

        canvas.md_id = figure.canvas.mpl_connect('motion_notify_event',
                                                 self.on_mouse_event)

        self.enter(canvas)

        return canvas

    def new(self, name='untitled.sch'):

        model = self.uimodel_class(self)
        model.pathname = name
        canvas = self.create_canvas(name, model)
        self.model = model
        return model

    def on_add_con(self, conname):

        if self.debug:
            print('Adding connection ' + conname)

        self.model.on_add_con(conname)

    def on_add_cpt(self, cptname):

        if self.debug:
            print('Adding component ' + cptname)

        self.model.on_add_cpt(cptname)

    def on_annotation(self, *args):

        # TODO: add args
        # TODO: need to support voltage and current labels
        cct = self.model.circuit.annotate_voltages(None)
        self.model.on_show_new_circuit(cct)

    def on_best_fit(self, *args):

        self.model.on_best_fit()

    def on_circuitgraph(self, *args):

        # TODO, save to png file and then display file
        self.model.circuit.cg.draw('/tmp/cg.png')
        self.show_image_dialog(
            '/tmp/cg.png', title='Circuit graph ' + self.model.pathname)

    def on_click_event(self, event):

        if event.xdata is None or event.ydata is None:
            # Can this happen?
            return

        if self.debug:
            print('Button event %s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))

        if event.dblclick:
            if event.button == 1:
                self.model.on_left_double_click(event.xdata, event.ydata)
            elif event.button == 3:
                self.model.on_right_double_click(event.xdata, event.ydata)
        else:
            if event.button == 1:
                self.model.on_left_click(event.xdata, event.ydata)
            elif event.button == 3:
                self.model.on_right_click(event.xdata, event.ydata)

    def on_clone(self, *args):

        self.model.on_clone()

    def on_copy(self, *args):

        self.model.on_copy()

    def on_create_state_space(self, *args):

        self.model.on_create_state_space()

    def on_create_transfer_function(self, *args):

        self.model.on_create_transfer_function()

    def on_create_twoport(self, arg):

        kind = arg[0]
        self.model.on_create_twoport(kind)

    def on_cut(self, *args):

        self.model.on_cut()

    def on_default_fit(self, *args):

        self.canvas.drawing.set_default_view()
        self.refresh()

    def on_description(self, *args):

        self.show_message_dialog(self.model.circuit.description())

    def report_callback_exception(self, exc, val, tb):

        # This catches exceptions but only for this window.
        # Each class needs to hook into this.
        from tkinter.messagebox import showerror

        if self.debug:
            import pdb
            pdb.set_trace()

        showerror('Error', message=str(val))

    def on_enter(self, event):

        # TODO, determine tab from mouse x, y
        if self.debug:
            print('Enter %s, %s' % (event.x, event.y))

        self.enter(self.canvases[0])

    def on_exception(self, *args):

        from tkinter import messagebox
        import traceback

        err = traceback.format_exception(*args)
        messagebox.showerror('Exception', err)

    def on_expression(self, *args):

        self.model.on_expression()

    def on_edit_values(self, *args):

        self.show_edit_values_dialog()

    def on_expand(self, *args):

        self.model.on_expand()

    def on_export(self, *args):

        self.model.on_export()

    def on_help(self, *args):

        self.model.on_help()

    def on_inspect_current(self, *args):

        self.model.on_inspect_current()

    def on_inspect_noise_current(self, *args):

        self.model.on_inspect_noise_current()

    def on_inspect_noise_voltage(self, *args):

        self.model.on_inspect_noise_voltage()

    def on_inspect_norton_admittance(self, *args):

        self.model.on_inspect_norton_admittance()

    def on_inspect_thevenin_impedance(self, *args):

        self.model.on_inspect_thevenin_impedance()

    def on_inspect_voltage(self, *args):

        self.model.on_inspect_voltage()

    def on_key_press_event(self, event):

        key = event.key
        if self.debug:
            print(key)

        if key in self.model.key_bindings:
            self.model.key_bindings[key]()
        elif key in self.model.key_bindings_with_key:
            self.model.key_bindings_with_key[key](key)

    def on_key(self, event):

        key = event.char

        if self.debug:
            print('Key %s %s, %s, %s' % (key, event.keycode, event.x, event.y))
            print(event)

        if key in self.model.key_bindings_with_key:
            self.model.key_bindings_with_key[key](key)

    def on_key2(self, event, func):

        if self.debug:
            print('Key2', event, func)
        func()

    def on_laplace_model(self, *args):

        self.model.on_laplace_model()

    def on_library(self, *args):
        from lcapygui import __libdir__

        self.model.on_load(str(__libdir__))

    def on_load(self, *args):

        self.model.on_load()

    def on_manipulate_kill(self, *args):

        self.model.on_manipulate_kill()

    def on_manipulate_remove_sources(self, *args):

        self.model.on_manipulate_remove_sources()

    def on_mesh_equations(self, *args):

        self.model.on_mesh_equations()

    def on_mouse_event(self, event):

        if self.debug:

            if event.xdata is None or event.ydata is None:
                print('Mouse event: x=%d, y=%d' %
                      (event.x, event.y))
            else:
                print('Mouse event: x=%d, y=%d, xdata=%f, ydata=%f' %
                      (event.x, event.y, event.xdata, event.ydata))

        if event.xdata is None or event.ydata is None:
            return

        if event.button == 1:
            self.model.on_mouse_drag(event.xdata, event.ydata)

    def on_netlist(self, *args):

        self.model.on_netlist()

    def on_nodal_equations(self, *args):

        self.model.on_nodal_equations()

    def on_noise_model(self, *args):

        self.model.on_noise_model()

    def on_new(self, *args):

        self.model.on_new()

    def on_paste(self, *args):

        self.model.on_paste()

    def on_plots(self, *args):

        self.show_multiplot_dialog()

    def on_preferences(self, *args):

        self.model.on_preferences()

    def on_quit(self, *args):

        self.model.on_quit()

    def on_save(self, *args):

        self.model.on_save()

    def on_save_as(self, *args):

        self.model.on_save_as()

    def on_screenshot(self, *args):

        self.model.on_screenshot()

    def on_simple_netlist(self, *args):

        self.model.on_simple_netlist()

    def on_tab_selected(self, event):

        notebook = event.widget
        tab_id = notebook.select()
        index = notebook.index(tab_id)

        # TODO: rethink if destroy a tab/canvas
        canvas = self.canvases[index]
        self.enter(canvas)

    def on_undo(self, *args):

        self.model.on_undo()

    def on_view(self, *args):

        self.model.on_view()

    def on_view_macros(self, *args):

        self.model.on_view_macros()

    def refresh(self):

        self.canvas.drawing.refresh()

    def quit(self):

        exit()

    def save(self, pathname):

        name = basename(pathname)
        self.set_canvas_title(name)

    def screenshot(self, pathname):

        self.canvas.drawing.savefig(pathname)

    def set_canvas_title(self, name):

        self.notebook.tab('current', text=name)

    def set_view(self, xmin, ymin, xmax, ymax):

        self.canvas.drawing.set_view(xmin, ymin, xmax, ymax)

    def show_approximate_dialog(self, expr, title=''):

        from .approximate_dialog import ApproximateDialog

        self.approximate_dialog = ApproximateDialog(expr, self, title)

    def show_edit_dialog(self, expr):

        from .edit_dialog import EditDialog

        self.edit_dialog = EditDialog(self, expr)

    def show_edit_values_dialog(self):

        from .edit_values_dialog import EditValuesDialog

        self.edit_values_dialog = EditValuesDialog(self)

    def show_equations_dialog(self, expr, title=''):

        from .equations_dialog import EquationsDialog

        self.equations_dialog = EquationsDialog(expr, self, title)

    def show_error_dialog(self, message):

        from tkinter.messagebox import showerror

        showerror('', message)

    def show_expr_dialog(self, expr, title=''):

        from .expr_dialog import ExprDialog

        self.expr_dialog = ExprDialog(expr, self, title)
        return self.expr_dialog

    def show_expr_attributes_dialog(self, expr, title=''):

        from .expr_attributes_dialog import ExprAttributesDialog

        self.expr_attributes_dialog = ExprAttributesDialog(expr, self, title)

    def show_help_dialog(self):

        from .help_dialog import HelpDialog

        self.help_dialog = HelpDialog()

    def show_image_dialog(self, filename, title=''):

        from .image_dialog import ImageDialog

        self.image_dialog = ImageDialog(self, filename, title)

    def show_inspect_dialog(self, cpt, title=''):

        from .inspect_dialog import InspectDialog

        self.inspect_dialog = InspectDialog(self, cpt, title)

    def inspect_properties_dialog(self, cpt, on_changed=None, title=''):

        from .cpt_properties_dialog import CptPropertiesDialog

        name = cpt.name
        if name in self.dialogs:
            self.dialogs[name].focus()
        else:
            dialog = CptPropertiesDialog(self, cpt, on_changed, title)
            self.dialogs[name] = dialog

    def show_info_dialog(self, message):

        from tkinter.messagebox import showinfo

        showinfo('', message)

    def show_limit_dialog(self, expr, title=''):

        from .limit_dialog import LimitDialog

        self.limit_dialog = LimitDialog(expr, self, title)

    def show_message_dialog(self, message, title=''):

        from .message_dialog import MessageDialog

        self.message_dialog = MessageDialog(message, title)

    def show_multiplot_dialog(self):

        from .multiplot_dialog import MultiplotDialog

        self.multiplot_dialog = MultiplotDialog(self)

    def show_node_properties_dialog(self, node, on_changed=None, title=''):

        from .node_properties_dialog import NodePropertiesDialog

        name = node.name
        if name in self.dialogs:
            self.dialogs[name].focus()
        else:
            dialog = NodePropertiesDialog(self, node, on_changed, title)
            self.dialogs[name] = dialog

    def show_plot_properties_dialog(self, expr):

        from .plot_properties_dialog import PlotPropertiesDialog

        self.plot_properties_dialog = PlotPropertiesDialog(expr, self)

    def show_preferences_dialog(self, on_changed=None):

        from .preferences_dialog import PreferencesDialog

        self.preferences_dialog = PreferencesDialog(self, on_changed)

    def show_python_dialog(self, expr):

        from .python_dialog import PythonDialog

        self.python_dialog = PythonDialog(expr, self)

    def show_working_dialog(self, expr):

        from .working_dialog import WorkingDialog

        self.working_dialog = WorkingDialog(expr, self)
        return self.working_dialog

    def show_state_space_dialog(self, cpt):

        from .state_space_dialog import StateSpaceDialog

        self.state_space_dialog = StateSpaceDialog(self, cpt)

    def show_subs_dialog(self, expr, title=''):

        from .subs_dialog import SubsDialog

        self.subs_dialog = SubsDialog(expr, self, title)

    def show_transfer_function_dialog(self, cpt):

        from .transfer_function_dialog import TransferFunctionDialog

        self.transfer_function_dialog = TransferFunctionDialog(self, cpt)

    def show_twoport_dialog(self, cpt, kind):

        from .twoport_dialog import TwoportDialog

        self.twoport_dialog = TwoportDialog(self, cpt, kind)

    def show_twoport_select_dialog(self, TP, kind):

        from .twoport_select_dialog import TwoportSelectDialog

        self.twoport_select_dialog = TwoportSelectDialog(self, TP, kind)

    def show_warning_dialog(self, message):

        from tkinter.messagebox import showwarning

        showwarning('', message)

    def open_file_dialog(self, initialdir='.', doc='Lcapy netlist',
                         ext='*.sch'):

        from tkinter.filedialog import askopenfilename

        pathname = askopenfilename(initialdir=initialdir,
                                   title="Select file",
                                   filetypes=((doc, ext),))
        return pathname

    def save_file_dialog(self, pathname, doc='Lcapy netlist',
                         ext='*.sch'):

        from tkinter.filedialog import asksaveasfilename
        from os.path import dirname, splitext, basename

        dirname = dirname(pathname)
        filename = basename(pathname)
        basename, ext = splitext(filename)

        options = {}
        options['defaultextension'] = ext
        options['filetypes'] = ((doc, ext),)
        options['initialdir'] = dirname
        options['initialfile'] = basename
        options['title'] = "Save file"

        return asksaveasfilename(**options)

    def export_file_dialog(self, pathname, default_ext=None):

        from tkinter.filedialog import asksaveasfilename
        from os.path import dirname, splitext, basename

        dirname = dirname(pathname)
        basename, ext = splitext(basename(pathname))

        if default_ext is not None:
            ext = default_ext

        options = {}
        options['defaultextension'] = ext
        options['filetypes'] = (("Embeddable LaTeX", "*.schtex"),
                                ("Standalone LaTeX", "*.tex"),
                                ("PNG image", "*.png"),
                                ("SVG image", "*.svg"),
                                ("PDF", "*.pdf"))
        options['initialdir'] = dirname
        options['initialfile'] = basename + '.pdf'
        options['title'] = "Export file"

        return asksaveasfilename(**options)

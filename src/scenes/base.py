class BaseScene:
    def __init__(self, cell_size=64, order=0):
        self._cell_size = cell_size
        self._cells = {}
        self._active_widgets = set()
        self._order = order
        self._mouse_pos = 0, 0

    def _hash(self, x, y):
        """Normalize position to cell"""
        return int(x / self._cell_size), int(y / self._cell_size)

    def add_widget(self, widget):
        """Add a Widget to the spatial hash."""
        min_vec, max_vec = self._hash(*widget.aabb[0:2]), self._hash(*widget.aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells.setdefault((i, j), set()).add(widget)
        widget.update_groups(self._order)

    def remove_widget(self, widget):
        """Remove a Widget from the spatial hash."""
        min_vec, max_vec = self._hash(*widget.aabb[0:2]), self._hash(*widget.aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells.get((i, j)).remove(widget)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_press(x, y, buttons, modifiers)
            self._active_widgets.add(widget)

    def on_mouse_release(self, x, y, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        for widget in self._active_widgets:
            widget.on_mouse_release(x, y, buttons, modifiers)
        self._active_widgets.clear()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        for widget in self._active_widgets:
            widget.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self._mouse_pos = x, y

    def on_mouse_scroll(self, x, y, index, direction):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_scroll(x, y, index, direction)

    def on_mouse_motion(self, x, y, dx, dy):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_motion(x, y, dx, dy)
        self._mouse_pos = x, y

    def on_key_press(self, symbol, modifiers):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_key_release(symbol, modifiers)

    def on_text(self, text):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text(text)

    def on_text_motion(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion_select(motion)

class FixedResScene:
    def __init__(self, cell_size=64, order=0):
        self._cell_size = cell_size
        self._cells = {}
        self._active_widgets = set()
        self._order = order
        self._mouse_pos = 0, 0

    def _hash(self, x, y):
        """Normalize position to cell"""
        return int(x / self._cell_size), int(y / self._cell_size)

    def add_widget(self, widget):
        """Add a Widget to the spatial hash."""
        min_vec, max_vec = self._hash(*widget.aabb[0:2]), self._hash(*widget.aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells.setdefault((i, j), set()).add(widget)
        widget.update_groups(self._order)

    def remove_widget(self, widget):
        """Remove a Widget from the spatial hash."""
        min_vec, max_vec = self._hash(*widget.aabb[0:2]), self._hash(*widget.aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells.get((i, j)).remove(widget)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_press(x, y, buttons, modifiers)
            self._active_widgets.add(widget)

    def on_mouse_release(self, x, y, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        for widget in self._active_widgets:
            widget.on_mouse_release(x, y, buttons, modifiers)
        self._active_widgets.clear()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        for widget in self._active_widgets:
            widget.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self._mouse_pos = x, y

    def on_mouse_scroll(self, x, y, index, direction):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_scroll(x, y, index, direction)

    def on_mouse_motion(self, x, y, dx, dy):
        """Pass the event to any widgets within range of the mouse"""
        x = x * (640 / 800)
        y = y * (480 / 600)
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_motion(x, y, dx, dy)
        self._mouse_pos = x, y

    def on_text(self, text):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text(text)

    def on_text_motion(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion_select(motion)
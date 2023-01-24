import pyglet
import pyglet.window.key as PKey


class Camera:
    """
        Bare-bones camera to allow zoom and translation over the view.
    """

    key_keypress = [PKey.UP, PKey.DOWN, PKey.LEFT, PKey.RIGHT]
    key_keyrelease = [PKey.UP, PKey.DOWN, PKey.LEFT, PKey.RIGHT]
    ZOOM_PER_Y_SCROLL = 5

    def __init__(self, window: pyglet.window.Window, scroll_speed=2400, min_zoom=1, max_zoom=4):
        assert min_zoom <= max_zoom, "Minimum zoom must not be greater than maximum zoom"
        self._window = window
        self.scroll_speed = scroll_speed
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self._zoom = max(min(1, self.max_zoom), self.min_zoom)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = max(min(value, self.max_zoom), self.min_zoom)

    def scroll(self, dt):
        # alm = self.alm
        x, y = self.x, self.y

        x += self.vx * dt
        y += self.vy * dt

        # clamp to allowed coords
        # x_max = (alm.width - MAP_PADDING * 2) * TILE_SIZE
        # y_max = (alm.height - MAP_PADDING * 2) * TILE_SIZE
        # x_min = y_min = MAP_PADDING * TILE_SIZE

        # x = min(x, x_max)
        # x = max(x, x_min)
        # y = min(y, y_max)
        # y = max(y, y_min)
        self.x, self.y = x, y

    def handle_scroll(self, scroll_y):
        self.zoom += scroll_y / self.ZOOM_PER_Y_SCROLL

    def handle_keypress(self, symbol):
        scroll_speed = self.scroll_speed
        if symbol == PKey.UP:
            self.vy = scroll_speed
        if symbol == PKey.DOWN:
            self.vy = -scroll_speed
        if symbol == PKey.LEFT:
            self.vx = -scroll_speed
        if symbol == PKey.RIGHT:
            self.vx = scroll_speed

    def handle_keyrelease(self, symbol):
        if symbol in [PKey.DOWN, PKey.UP]:
            self.vy = 0
        elif symbol in [PKey.LEFT, PKey.RIGHT]:
            self.vx = 0

    def begin(self):
        # Copy. I think it's based on tuple so should immutable and ref-by-value?
        self._begin_view_mat = self._window.view

        x = -self.x
        y = -self.y + self._window.size[1]
        z = 0
        view_matrix = self._window.view.translate((x, y, z))
        # Scale by zoom level.
        view_matrix = view_matrix.scale((self._zoom, -self._zoom, 1))

        self._window.view = view_matrix

    def end(self):
        self._window.view = self._begin_view_mat

    def __enter__(self):
        self.begin()

    def __exit__(self, exception_type, exception_value, traceback):
        self.end()

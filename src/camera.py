import pyglet
import pyglet.window.key as PKey


class Camera:
    """
        Bare-bones camera to allow zoom and translation over the view.
    """
    PIXELS_PER_SECOND = 1
    ZOOM_PER_MOUSE_Y_SCROLL = 5
    key_keypress = [PKey.UP, PKey.DOWN, PKey.LEFT, PKey.RIGHT]
    key_keyrelease = [PKey.UP, PKey.DOWN, PKey.LEFT, PKey.RIGHT]
    _stored_view = None

    def __init__(self, window: pyglet.window.Window, scroll_speed=2400 * PIXELS_PER_SECOND, min_zoom=1, max_zoom=4):
        assert min_zoom <= max_zoom, "Minimum zoom must not be greater than maximum zoom"
        self._window = window
        self.scroll_speed = scroll_speed
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.x = 0
        self.y = 0
        # actual translate offset
        self.translate_x = 0
        self.translate_y = 0

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

        w, h = self._window.size
        zoom = self._zoom
        # self.translate_x = (x + w / 2) * zoom - w / 2
        # self.translate_y = (y + h / 2) * zoom - h / 2 + h

        self.x, self.y = x, y

    def handle_scroll(self, scroll_y):
        self.zoom += scroll_y / self.ZOOM_PER_MOUSE_Y_SCROLL

    def handle_keypress(self, symbol):
        scroll_speed = self.scroll_speed
        if symbol == PKey.UP:
            self.vy = -scroll_speed
        if symbol == PKey.DOWN:
            self.vy = scroll_speed
        if symbol == PKey.LEFT:
            self.vx = -scroll_speed
        if symbol == PKey.RIGHT:
            self.vx = scroll_speed

    def handle_keyrelease(self, symbol):
        if symbol in [PKey.DOWN, PKey.UP]:
            self.vy = 0
        elif symbol in [PKey.LEFT, PKey.RIGHT]:
            self.vx = 0

    def screen_xy_to_world_xy(self, x, y):
        zoom = self._zoom
        w, h = self._window.size

        tx = (self.x + w / 2) * zoom - w / 2
        ty = (self.y + h / 2) * zoom - h / 2 + h

        x = (x + tx) / self._zoom
        y = (y - ty) / -self._zoom

        # x = (x + self.translate_x) / self._zoom
        # y = (y - self.translate_y) / -self._zoom

        # matrix impl
        # inverted_transform_matrix = ~self.get_transform_matrix()
        # pos = inverted_transform_matrix @ pyglet.math.Vec4(x, y, 0, 1)
        # x, y = pos.x, pos.y
        return x, y

    def get_transform_matrix(self):
        # opengl renders things at (0, 0, 0)
        # translate the world in inverse direction relative to camera to simulate camera movement
        # y translates directly to flip coordinates

        x, y = self.x, self.y
        zoom = self._zoom
        w, h = self._window.size

        tx = (x + w / 2) * zoom - w / 2
        ty = (y + h / 2) * zoom - h / 2 + h

        transform_matrix = self._window.view
        transform_matrix = transform_matrix.translate((-tx, ty, 0))
        transform_matrix = transform_matrix.scale((zoom, -zoom, 1))
        return transform_matrix

    def begin(self):
        # Copy. I think it's based on tuple so should immutable and ref-by-value?
        self._stored_view = self._window.view
        self._window.view = self.get_transform_matrix()

    def end(self):
        self._window.view = self._stored_view

    def __enter__(self):
        self.begin()

    def __exit__(self, exception_type, exception_value, traceback):
        self.end()

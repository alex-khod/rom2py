
def get_object_animation():
    def prepare_object(self, key):
        a256 = Resources["graphics", "objects", obj_record["filename"] + ".256"].content
        frames = []
        animationframes, animationtimes = [obj_record['index']], [None]
        try:
            animationframes = obj_record["animationframe"]
            animationtimes = obj_record["animationtime"]
        except KeyError:
            pass
        for frame_no, duration in zip(animationframes, animationtimes):
            w, h = obj_record["width"], obj_record["height"]
            image = a256[frame_no]
            cx, cy = obj_record["centerx"], obj_record["centery"]
            image.anchor_x = cx
            image.anchor_y = cy
            duration = duration / 60 if duration else None
            image = image.to_rgba_image_data()
            frame = pyglet.image.AnimationFrame(image, duration)
            frames.append(frame)
        assert len(animationtimes) == len(animationframes)
        self.animations[key] = pyglet.image.Animation(frames)
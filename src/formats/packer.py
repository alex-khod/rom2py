def a256_write(wb, images):
    MAX_COLORS = 256
    palette = {}
    paletted = []
    for image in images:
        image = image.quantize(method=PILImage.Quantize.FASTOCTREE)
        paletted.append(image)
        # print(set([c for c in image.palette.colors]))
        palette.update(image.palette.colors)

    colors = list(palette.keys())[:MAX_COLORS]
    leftover = MAX_COLORS - len(colors)
    colors += leftover * [0, 0, 0]

    assert len(colors) == MAX_COLORS

    for p in colors:
        r, g, b = p
        wb.write(struct.pack("<BBBB", 0, r, g, b))

    for pil in paletted:
        arr = np.array(pil)
        h, w = arr.shape
        arr = arr.reshape(arr.shape[0] * arr.shape[1])

        def alpha_row(idx, wb):
            rows = 0
            while idx < w * h and all(flat[idx:idx + w] == 0):
                rows += 1
                idx += w
            if rows:
                while rows > 0:
                    val = min(MAX_COUNT, rows)
                    rows -= val
                    wb.write(struct.pack("<B", 0x40 | val))
            alpha_count = 0
            while idx < w * h and flat[idx] == 0 and idx < w * h:
                alpha_count += 1
                idx += 1
            if alpha_count:
                while alpha_count > 0:
                    val = min(MAX_COUNT, alpha_count)
                    alpha_count -= val
                    wb.write(struct.pack("<B", 0x80 | val))
            return idx

        def pixels(idx, wb):
            pixel_count = 0
            while idx < w * h and flat[idx] != 0:
                pixel_count += 1
                idx += 1
            if pixel_count:
                while pixel_count > 0:
                    val = min(MAX_COUNT, pixel_count)
                    pixel_count -= val
                    wb.write(struct.pack("<B", val))
            return idx

        from io import BytesIO
        buffer = io.BytesIO()
        buffer.seek(0)

        MAX_COUNT = 64 - 1
        idx = 0
        # flat = arr.reshape((w * h))
        flat = [0] * 128 * 128
        data_size = len(flat)
        while idx < data_size:
            import random
            color_idx = random.randint(0, 255)
            count = random.randint(1, 31)
            count = min(data_size - idx, count)
            values = [count] + [color_idx] * count
            data = struct.pack("<B" + "B" * count, *values)
            print(count + 1)
            buffer.write(data)
            idx += count + 1
            # if flat[idx] == 0:
            #     idx = alpha_row(idx, buffer)
            # else:
            #     idx = pixels(idx, buffer)
        print('puck')
        wb.write(struct.pack("<LLL", h, w, idx))
        buffer.seek(0)
        wb.write(buffer.read())
    HAS_PALETTE = 0x80000000
    wb.write(struct.pack("<L", len(images) | HAS_PALETTE))
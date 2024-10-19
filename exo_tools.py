from exo import EXOTemplate

def calc_frame_from_time(t, settings):
    seconds = t / 100
    frames = int(seconds * settings.GENERAL.PROJECT_FRAMERATE // 1)
    return frames

def calc_margin_x(w, w1, w2, settings):
    if w1 + w2 >= w * settings.GENERAL.PROJECT_LYRIC_X_OVERLAP_FACTOR:
        return 0
    else:
        return (w * settings.GENERAL.PROJECT_LYRIC_X_OVERLAP_FACTOR - (w1 + w2)) // 2

def convert_x(x, settings):
    return int(x - settings.GENERAL.PROJECT_WIDTH // 2)

def generate_exo(data, settings):
    # Output EXO
    output_exo = ""
    init_exo = EXOTemplate.INIT
    init_exo = init_exo.replace("{project_width}", f"{settings.GENERAL.PROJECT_WIDTH}")
    init_exo = init_exo.replace("{project_height}", f"{settings.GENERAL.PROJECT_HEIGHT}")
    init_exo = init_exo.replace("{project_framerate}", f"{settings.GENERAL.PROJECT_FRAMERATE}")
    init_exo = init_exo.replace("{project_length}", f"{calc_frame_from_time(data[-1]['display_end_time'], settings)}")
    output_exo += init_exo
    obj_id = 0

    for i, dc in enumerate(data):

        # back lyric
        back_exo = EXOTemplate.BACK
        display_row = dc["display_row"]
        block_length = dc['block_length']
        x = settings.GENERAL.PROJECT_MARGIN_X

        if display_row == 0:
            y = settings.GENERAL.PROJECT_Y_0_LYRIC
            overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i + 1]["x_length"], dc["x_length"], settings)
            x = convert_x(settings.GENERAL.PROJECT_MARGIN_X + settings.GENERAL.WIDTH / 2, settings) + overlap_margin_x

        elif display_row == 1:
            y = settings.GENERAL.PROJECT_Y_1_LYRIC
            if block_length == 3:
                overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i + 1]["x_length"], dc["x_length"], settings)
                x = convert_x(settings.GENERAL.PROJECT_MARGIN_X + settings.GENERAL.WIDTH / 2, settings) + overlap_margin_x
            elif block_length == 4:
                overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i - 1]["x_length"], dc["x_length"], settings)
                x = convert_x(settings.GENERAL.PROJECT_WIDTH - settings.GENERAL.PROJECT_MARGIN_X - dc["x_length"] + settings.GENERAL.WIDTH / 2, settings) - overlap_margin_x

        elif display_row == 2:
            y = settings.GENERAL.PROJECT_Y_2_LYRIC
            if block_length == 2 or block_length == 4:
                overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i + 1]["x_length"], dc["x_length"], settings)
                x = convert_x(settings.GENERAL.PROJECT_MARGIN_X + settings.GENERAL.WIDTH / 2, settings) + overlap_margin_x
            elif block_length == 3:
                overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i - 1]["x_length"], dc["x_length"], settings)
                x = convert_x(settings.GENERAL.PROJECT_WIDTH - settings.GENERAL.PROJECT_MARGIN_X - dc["x_length"] + settings.GENERAL.WIDTH / 2, settings) - overlap_margin_x

        elif display_row == 3:
            y = settings.GENERAL.PROJECT_Y_3_LYRIC
            if block_length == 1 or block_length == 3:
                x = convert_x(settings.GENERAL.PROJECT_WIDTH / 2 - dc["x_length"] / 2 + settings.GENERAL.WIDTH / 2, settings)
            elif block_length == 2 or block_length == 4:
                overlap_margin_x = calc_margin_x(settings.GENERAL.PROJECT_WIDTH, data[i - 1]["x_length"], dc["x_length"], settings)
                x = convert_x(settings.GENERAL.PROJECT_WIDTH - settings.GENERAL.PROJECT_MARGIN_X - dc["x_length"] + settings.GENERAL.WIDTH / 2, settings) - overlap_margin_x
        
        layer = 4 + display_row
        file = dc["image_2"]
        start = calc_frame_from_time(dc["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc["display_end_time"], settings)
        clip_up = settings.GENERAL.Y_LYRIC - settings.LYRIC.STROKE_WIDTH
        clip_bottom = 0

        back_exo = back_exo.replace("{obj_id}", f"{obj_id}")
        back_exo = back_exo.replace("{start}", f"{start}")
        back_exo = back_exo.replace("{end}", f"{end}")
        back_exo = back_exo.replace("{layer}", f"{layer}")
        back_exo = back_exo.replace("{x}", f"{x}")
        back_exo = back_exo.replace("{y}", f"{y}")
        back_exo = back_exo.replace("{file}", f"{file}")
        back_exo = back_exo.replace("{clip_up}", f"{clip_up}")
        back_exo = back_exo.replace("{clip_bottom}", f"{clip_bottom}")
        
        output_exo += back_exo
        obj_id += 1

        # Front lyric
        front_exo = EXOTemplate.FRONT
        start = calc_frame_from_time(dc["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc["times"][0], settings)
        layer = 12 + display_row
        file = dc["image_1"]
        clip_up = settings.GENERAL.Y_LYRIC - settings.LYRIC.STROKE_WIDTH
        clip_bottom = 0

        front_exo = front_exo.replace("{obj_id}", f"{obj_id}")
        front_exo = front_exo.replace("{start}", f"{start}")
        front_exo = front_exo.replace("{end}", f"{end}")
        front_exo = front_exo.replace("{layer}", f"{layer}")
        front_exo = front_exo.replace("{x}", f"{x}")
        front_exo = front_exo.replace("{y}", f"{y}")
        front_exo = front_exo.replace("{file}", f"{file}")
        front_exo = front_exo.replace("{clip_up}", f"{clip_up}")
        front_exo = front_exo.replace("{clip_bottom}", f"{clip_bottom}")

        output_exo += front_exo
        obj_id += 1

        # Front lyric chain
        for j in range(len(dc["times"]) - 1):
            front_exo = EXOTemplate.FRONT_CHAIN
            start = calc_frame_from_time(dc["times"][j], settings) + 1
            end = calc_frame_from_time(dc["times"][j + 1], settings)
            layer = 12 + display_row
            left = dc["x_start_lyric"][j]
            right = dc["x_end_lyric"][j]

            front_exo = front_exo.replace("{obj_id}", f"{obj_id}")
            front_exo = front_exo.replace("{start}", f"{start}")
            front_exo = front_exo.replace("{end}", f"{end}")
            front_exo = front_exo.replace("{layer}", f"{layer}")
            front_exo = front_exo.replace("{x}", f"{x}")
            front_exo = front_exo.replace("{y}", f"{y}")
            front_exo = front_exo.replace("{left}", f"{left}")
            front_exo = front_exo.replace("{right}", f"{right}")
            front_exo = front_exo.replace("{clip_up}", f"{clip_up}")
            front_exo = front_exo.replace("{clip_bottom}", f"{clip_bottom}")

            output_exo += front_exo
            obj_id += 1

        # back ruby
        back_exo = EXOTemplate.BACK
        display_row = dc["display_row"]
        if display_row == 0:
            y = settings.GENERAL.PROJECT_Y_0_RUBY
        elif display_row == 1:
            y = settings.GENERAL.PROJECT_Y_1_RUBY
        elif display_row == 2:
            y = settings.GENERAL.PROJECT_Y_2_RUBY
        elif display_row == 3:
            y = settings.GENERAL.PROJECT_Y_3_RUBY
        
        layer = 8 + display_row
        file = dc["image_2"]
        start = calc_frame_from_time(dc["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc["display_end_time"], settings)
        clip_up = 0
        clip_bottom = settings.GENERAL.HEIGHT - (settings.GENERAL.Y_RUBY + settings.RUBY.FONT_SIZE + settings.RUBY.STROKE_WIDTH)

        back_exo = back_exo.replace("{obj_id}", f"{obj_id}")
        back_exo = back_exo.replace("{start}", f"{start}")
        back_exo = back_exo.replace("{end}", f"{end}")
        back_exo = back_exo.replace("{layer}", f"{layer}")
        back_exo = back_exo.replace("{x}", f"{x}")
        back_exo = back_exo.replace("{y}", f"{y}")
        back_exo = back_exo.replace("{file}", f"{file}")
        back_exo = back_exo.replace("{clip_up}", f"{clip_up}")
        back_exo = back_exo.replace("{clip_bottom}", f"{clip_bottom}")
        
        output_exo += back_exo
        obj_id += 1

        # Front ruby
        front_exo = EXOTemplate.FRONT
        start = calc_frame_from_time(dc["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc["times"][0], settings)
        layer = 16 + display_row
        file = dc["image_1"]
        clip_up = 0
        clip_bottom = settings.GENERAL.HEIGHT - (settings.GENERAL.Y_RUBY + settings.RUBY.FONT_SIZE + settings.RUBY.STROKE_WIDTH)

        front_exo = front_exo.replace("{obj_id}", f"{obj_id}")
        front_exo = front_exo.replace("{start}", f"{start}")
        front_exo = front_exo.replace("{end}", f"{end}")
        front_exo = front_exo.replace("{layer}", f"{layer}")
        front_exo = front_exo.replace("{x}", f"{x}")
        front_exo = front_exo.replace("{y}", f"{y}")
        front_exo = front_exo.replace("{file}", f"{file}")
        front_exo = front_exo.replace("{clip_up}", f"{clip_up}")
        front_exo = front_exo.replace("{clip_bottom}", f"{clip_bottom}")

        output_exo += front_exo
        obj_id += 1

        # Front ruby chain
        for j in range(len(dc["times"]) - 1):
            front_exo = EXOTemplate.FRONT_CHAIN
            start = calc_frame_from_time(dc["times"][j], settings) + 1
            end = calc_frame_from_time(dc["times"][j + 1], settings)
            layer = 16 + display_row
            left = dc["x_start_ruby"][j]
            right = dc["x_end_ruby"][j]

            front_exo = front_exo.replace("{obj_id}", f"{obj_id}")
            front_exo = front_exo.replace("{start}", f"{start}")
            front_exo = front_exo.replace("{end}", f"{end}")
            front_exo = front_exo.replace("{layer}", f"{layer}")
            front_exo = front_exo.replace("{x}", f"{x}")
            front_exo = front_exo.replace("{y}", f"{y}")
            front_exo = front_exo.replace("{left}", f"{left}")
            front_exo = front_exo.replace("{right}", f"{right}")
            front_exo = front_exo.replace("{clip_up}", f"{clip_up}")
            front_exo = front_exo.replace("{clip_bottom}", f"{clip_bottom}")

            output_exo += front_exo
            obj_id += 1

    return output_exo
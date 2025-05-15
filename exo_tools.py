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

def divide_segments(x_start, x_end, division_points):
    total_ratio = sum(division_points)
    segment_length = (x_end - x_start) / total_ratio
    
    x_coords = [x_start]
    current_x = x_start
    
    for ratio in division_points:
        current_x += ratio * segment_length
        x_coords.append(current_x)
    
    return x_coords

def generate_exo(data, data_r, settings):
    assert len(data) == len(data_r)

    # Output EXO
    output_exo = ""
    init_exo = EXOTemplate.INIT
    init_exo = init_exo.replace("{project_width}", f"{settings.GENERAL.PROJECT_WIDTH}")
    init_exo = init_exo.replace("{project_height}", f"{settings.GENERAL.PROJECT_HEIGHT}")
    init_exo = init_exo.replace("{project_framerate}", f"{settings.GENERAL.PROJECT_FRAMERATE}")
    init_exo = init_exo.replace("{project_length}", f"{calc_frame_from_time(data[-1]['display_end_time'], settings)}")
    output_exo += init_exo
    obj_id = 0

    for i, (dc, dc_r) in enumerate(zip(data, data_r)):

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
        end = calc_frame_from_time(dc["times"][0][0], settings)
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

            delta_time_s = (dc["times"][j + 1][0] - dc["times"][j][0]) / 100
            
            if len(dc["times"][j]) == 1 and delta_time_s >= settings.LYRIC.ADJUST_WIPE_SPEED_THRESHOLD_S:
                # ルビの文字単位でのワイプ定義がない and ワイプ速度有効の場合：設定に沿ってワイプ速度を変更
                division_times = divide_segments(dc["times"][j][0], dc["times"][j + 1][0], settings.LYRIC.ADJUST_WIPE_SPEED_DIVISION_TIMES)
                division_xs = divide_segments(dc["x_start_lyric"][j][0], dc["x_end_lyric"][j][0], settings.LYRIC.ADJUST_WIPE_SPEED_DIVISION_POINTS)

                for k in range(len(division_times) - 1):
                    front_exo = EXOTemplate.FRONT_CHAIN
                    start = calc_frame_from_time(division_times[k], settings) + 1
                    end = calc_frame_from_time(division_times[k + 1], settings)
                    layer = 12 + display_row
                    left = division_xs[k] // 1
                    right = division_xs[k + 1] // 1

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

            elif len(dc["times"][j]) > 1 and settings.LYRIC.SYNC_WIPE_WITH_RUBY:
                # ルビの文字単位でのワイプ定義がある and ルビ・歌詞のワイプ同期ONの場合：ルビのワイプに合わせて歌詞もワイプ

                _time_deltas = [
                    (dc["times"][j][k+1] if k+1 < len(dc["times"][j]) else dc["times"][j + 1][0]) - dc["times"][j][k]
                    for k in range(len(dc["times"][j]))
                ]
                _x_deltas = [
                    (dc["x_start_ruby"][j][k+1] if k+1 < len(dc["x_start_ruby"][j]) else dc["x_end_ruby"][j][-1]) - dc["x_start_ruby"][j][k]
                    for k in range(len(dc["x_start_ruby"][j]))
                ]

                division_times = divide_segments(dc["times"][j][0], dc["times"][j + 1][0], _time_deltas)
                division_xs = divide_segments(dc["x_start_lyric"][j][0], dc["x_end_lyric"][j][0], _x_deltas)

                for k in range(len(division_times) - 1):

                    _delta_time_s = (division_times[k + 1] - division_times[k]) / 100

                    # ルビの文字でワイプ速度有効の場合は、歌詞のワイプもルビに合わせる
                    if _delta_time_s >= settings.RUBY.ADJUST_WIPE_SPEED_THRESHOLD_S:
                        _division_times = divide_segments(division_times[k], division_times[k + 1], settings.RUBY.ADJUST_WIPE_SPEED_DIVISION_TIMES)
                        _division_xs = divide_segments(division_xs[k], division_xs[k + 1], settings.RUBY.ADJUST_WIPE_SPEED_DIVISION_POINTS)
                        
                        for l in range(len(_division_times) - 1):
                            front_exo = EXOTemplate.FRONT_CHAIN
                            start = calc_frame_from_time(_division_times[l], settings) + 1
                            end = calc_frame_from_time(_division_times[l + 1], settings)
                            layer = 12 + display_row
                            left = _division_xs[l] // 1
                            right = _division_xs[l + 1] // 1

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
                        
                        continue

                    front_exo = EXOTemplate.FRONT_CHAIN
                    start = calc_frame_from_time(division_times[k], settings) + 1
                    end = calc_frame_from_time(division_times[k + 1], settings)
                    layer = 12 + display_row
                    left = division_xs[k] // 1
                    right = division_xs[k + 1] // 1

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

            else:
                # ルビの文字単位でのワイプ定義がない or ワイプ速度調整無効の場合：等速でワイプ
                front_exo = EXOTemplate.FRONT_CHAIN
                start = calc_frame_from_time(dc["times"][j][0], settings) + 1
                end = calc_frame_from_time(dc["times"][j + 1][0], settings)
                layer = 12 + display_row
                left = dc["x_start_lyric"][j][0]
                right = dc["x_end_lyric"][j][0]

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
        display_row = dc_r["display_row"]
        if display_row == 0:
            y = settings.GENERAL.PROJECT_Y_0_RUBY
        elif display_row == 1:
            y = settings.GENERAL.PROJECT_Y_1_RUBY
        elif display_row == 2:
            y = settings.GENERAL.PROJECT_Y_2_RUBY
        elif display_row == 3:
            y = settings.GENERAL.PROJECT_Y_3_RUBY
        
        layer = 8 + display_row
        file = dc_r["image_2"]
        start = calc_frame_from_time(dc_r["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc_r["display_end_time"], settings)
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
        start = calc_frame_from_time(dc_r["display_start_time"], settings) + 1
        end = calc_frame_from_time(dc_r["times"][0][0], settings)
        layer = 16 + display_row
        file = dc_r["image_1"]
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

        _dc_ruby = {
            "times": [x for sub in dc_r["times"] for x in sub],
            "x_start_ruby": [x for sub in dc_r["x_start_ruby"] for x in sub],
            "x_end_ruby": [x for sub in dc_r["x_end_ruby"] for x in sub],
        }

        # Front ruby chain
        for j in range(len(_dc_ruby["times"]) - 1):
            delta_time_s = (_dc_ruby["times"][j + 1] - _dc_ruby["times"][j]) / 100
            if delta_time_s >= settings.RUBY.ADJUST_WIPE_SPEED_THRESHOLD_S:
                division_times = divide_segments(_dc_ruby["times"][j], _dc_ruby["times"][j + 1], settings.RUBY.ADJUST_WIPE_SPEED_DIVISION_TIMES)
                division_xs = divide_segments(_dc_ruby["x_start_ruby"][j], _dc_ruby["x_end_ruby"][j], settings.RUBY.ADJUST_WIPE_SPEED_DIVISION_POINTS)

                for k in range(len(division_times) - 1):
                    front_exo = EXOTemplate.FRONT_CHAIN
                    start = calc_frame_from_time(division_times[k], settings) + 1
                    end = calc_frame_from_time(division_times[k + 1], settings)
                    layer = 16 + display_row
                    left = division_xs[k] // 1
                    right = division_xs[k + 1] // 1

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
            
            else:
                front_exo = EXOTemplate.FRONT_CHAIN
                start = calc_frame_from_time(_dc_ruby["times"][j], settings) + 1
                end = calc_frame_from_time(_dc_ruby["times"][j + 1], settings)
                layer = 16 + display_row
                left = _dc_ruby["x_start_ruby"][j]
                right = _dc_ruby["x_end_ruby"][j]

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
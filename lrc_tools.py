import re

def time_tag_to_ms(time_tag):
    """
    時間タグ（[分:秒:ミリ秒]形式）をミリ秒に変換します。

    引数:
    time_tag (str): "[mm:ss:ms]"の形式で与えられる時間タグ文字列。

    戻り値:
    int: 与えられた時間タグをミリ秒に変換した値。
    """
    time_tag = time_tag.strip('[]')
    minutes, seconds, milliseconds = map(int, time_tag.split(':'))
    total_ms = minutes * 60 * 100 + seconds * 100 + milliseconds
    return total_ms

def parse_lrc(text):
    """
    歌詞ファイルから時間と歌詞、およびルビ（振り仮名）を抽出して構造化データに変換します。

    引数:
    text (str): 歌詞と時間タグを含むテキスト。

    戻り値:
    dict: 以下のキーを含む辞書:
        - "times": 各歌詞行に対応する時間（ミリ秒）のリスト。
        - "lyrics": 歌詞のリスト。
        - "rubys": ルビ（振り仮名）のリスト（存在しない場合は空文字列が入る）。
    """
    time_pattern = r'\[\d{2}:\d{2}:\d{2}\]'
    lyrics = re.split(time_pattern, text)[1:]
    times = [time_tag_to_ms(t) for t in re.findall(time_pattern, text)]
    if len(lyrics) <= 1:
        return {}
    
    i = 0
    _lyrics = []
    _times = []
    _rubys = []
    while i < len(times):
        if i + 1 < len(times):
            if times[i] == times[i + 1] and lyrics[i + 1] == "(": # Ruby
                _lyrics.append(lyrics[i])
                _times.append(times[i])
                try:
                    _rubys.append(lyrics[i + 2])
                except:
                    _rubys.append("")
                i += 4

            else:
                _lyrics.append(lyrics[i])
                _times.append(times[i])
                _rubys.append("")
                i += 1

        else:
            _times.append(times[-1])
            i += 1
    
    if len(_lyrics) == len(_times):
        _times.append(_times[-1])
    
    return {"times": _times, "lyrics": _lyrics, "rubys": _rubys}

def split_list(lst, delimiter):
    """
    リストを指定された区切り文字で分割します。

    引数:
    lst (list): 分割対象のリスト。
    delimiter (any): 分割基準となる区切り文字。

    戻り値:
    list: 区切り文字で分割されたリストのリスト。
    """
    result = []
    current = []
    for item in lst:
        if item == delimiter:
            result.append(current)
            current = []
        else:
            current.append(item)
    result.append(current)
    return result

def parse_lrc_texts(lines):
    """
    複数行の歌詞データを解析し、各ブロックごとに時間・歌詞・ルビ情報を取得します。

    引数:
    lines (list of str): 歌詞データの各行を要素とするリスト。

    戻り値:
    list: 各ブロック内で解析された歌詞データの辞書を含むリスト。各辞書には以下のキーが含まれます:
        - "times": 各行に対応する時間（ミリ秒）。
        - "lyrics": 各行の歌詞。
        - "rubys": 各行のルビ（振り仮名）。
        - "block_current": ブロック内の現在の行番号。
        - "block_length": ブロック内の行数。
    """
    lines = [l.strip() for l in lines if not "@" in l]
    blocks = split_list(lines, "")
    result = []
    for block in blocks:
        for i, line in enumerate(block):
            lyric_dc = parse_lrc(line)
            lyric_dc["block_current"] = i + 1
            lyric_dc["block_length"] = len(block)
            result.append(lyric_dc)

    return result
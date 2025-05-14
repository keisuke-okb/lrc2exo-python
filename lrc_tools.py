import re
import numpy as np
from collections import OrderedDict

# 正規表現コンパイル
ruby_def_re = re.compile(
    r'^@Ruby(?P<id>\d+)='                  # @RubyID=
    r'(?P<text>[^,]+),'                    # text (カンマ以外)
    r'(?P<ruby>[^,]+?)'                    # ruby (カンマ以外を最短マッチ)
    r'(?:,(?P<start>(?:\[[0-9:.]+\])?))?'  # ,start フィールド（[hh:mm:ss] または空）
    r'(?:,(?P<end>(?:\[[0-9:.]+\])?))?'    # ,end   フィールド（[hh:mm:ss] または空）
    r'$'                                   # 行末
)

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
    
    return {
        "times": [[t] for t in _times],
        "lyrics": [[l] for l in _lyrics],
        "rubys": [[r] for r in _rubys]
    }


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


def parse_ruby_definitions(lines):
    """
    @Ruby1～N の順序を保持して、各定義を辞書に保存した OrderedDict を返す。
    key: int(Ruby番号), value: dict(text, units, start, end)
    """
    rubies = []
    for line in lines:
        m = ruby_def_re.match(line.strip())
        if not m:
            continue
        idx   = int(m.group('id'))
        text  = m.group('text')
        ruby  = m.group('ruby')
        start = time_tag_to_ms(m.group('start')) if m.group('start') else time_tag_to_ms("[00:00:00]")
        end   = time_tag_to_ms(m.group('end'))   if m.group('end')   else time_tag_to_ms("[99:59:99]")
        
        # ルビ部をタイムタグと文字で分割
        parts = re.split(r'(\[[0-9:.]+\])', ruby)

        texts = []
        times = []
        buf = ''

        for p in parts:
            if p.startswith('['):
                if buf:
                    texts.append(buf); buf = ''
                times.append(time_tag_to_ms(p))

            else:
                buf += p
        if buf:
            texts.append(buf)
        
        rubies.append({'id': idx, 'text': text, 'div_texts': texts, 'div_times': times, 'start': start, 'end': end })
    
    return rubies


def split_with_target(s: str, target: str) -> list[str]:
    """
    文字列 s の中で target にマッチする部分を境に分割し、
    target 自身も要素として含むリストを返す。
    """
    # target を正規表現でエスケープし、キャプチャグループとして使う
    pattern = f'({re.escape(target)})'
    # split すると、キャプチャ部分もリストに残る
    parts = re.split(pattern, s)
    # 空文字を取り除いて返す
    return [p for p in parts if p]

def apply_rubies_to_result(result, ruby_defs):
    """
    result: list of parse_lrc_texts 出力
    ruby_defs: OrderedDict from parse_ruby_definitions
    各 @RubyN を順に適用し、start/end 範囲をチェックする
    """
    for entry in result:
        assert all(k in entry for k in ('times', 'lyrics', 'rubys'))
        times  = entry['times']   # List[List[int]]
        lyrics = entry['lyrics']  # List[List[str]]
        rubys  = entry['rubys']   # List[List[str]]

        _times = []
        _lyrics = []
        _rubys = []

        for idx_l, lyric_li in enumerate(lyrics):
            lyric = lyric_li[0]
            time_start = times[idx_l][0]
            time_end = times[idx_l + 1][0]
            _is_append = False

            # ルビ定義番号順に適用
            for idx, ruby in enumerate(ruby_defs):
                text  = ruby['text']
                div_texts = ruby['div_texts']
                div_times = ruby['div_times']
                start = ruby['start']
                end   = ruby['end']

                if text in lyric:
                    if time_start < start:
                        continue
                    if time_end > end:
                        continue

                    if text == lyric:
                        if len(div_times) > 0:
                            _times.append([times[idx_l][0]] + [d + times[idx_l][0] for d in div_times])
                        else:
                            _times.append([times[idx_l][0]])
                        _lyrics.append(lyric_li)
                        _rubys.append(div_texts)
                        _is_append = True
                        # times[idx_l].extend([d + times[idx_l][0] for d in div_times])
                        # rubys[idx_l] = div_texts

                    else:
                        _lyrics_spl = split_with_target(lyric, text)
                        _is_t = False
                        for _lyric in _lyrics_spl:
                            if text == _lyric:
                                if len(div_times) > 0:
                                    _times.append([times[idx_l][0]] + [d + times[idx_l][0] for d in div_times])
                                else:
                                    _times.append([times[idx_l][0]])
                                _lyrics.append([_lyric])
                                _rubys.append(div_texts)
                                _is_t = True

                            else:
                                if not _is_t:
                                    _times.append([times[idx_l][0]])
                                    _lyrics.append([_lyric])
                                    _rubys.append([""])
                                else:
                                    _times.append([times[idx_l + 1][0]])
                                    _lyrics.append([_lyric])
                                    _rubys.append([""])
                        
                        _is_append = True
                        
                    break

            if not _is_append: # Without ruby
                _times.append([times[idx_l][0]])
                _lyrics.append(lyric_li)
                _rubys.append([""])
        
        _times.append(times[-1])
        entry['times'] = _times
        entry['lyrics'] = _lyrics
        entry['rubys'] = _rubys
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
    if not any(['@Ruby' in l.strip() for l in lines]):
        # LRC without @RubyX annotations or ruby-inlined KRA
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
    
    else:
        # LRC with @RubyX annotations
        ruby_defs = parse_ruby_definitions(lines)
        
        lyric_lines = [l.strip() for l in lines if not "@" in l]
        blocks = split_list(lyric_lines, "")
        result = []
        for block in blocks:
            for i, line in enumerate(block):
                lyric_dc = parse_lrc(line)
                lyric_dc["block_current"] = i + 1
                lyric_dc["block_length"] = len(block)
                result.append(lyric_dc)

        return apply_rubies_to_result(result, ruby_defs)


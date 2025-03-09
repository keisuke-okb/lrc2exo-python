# LRC2EXO-Python

![Image](./images/LRC2EXO-Python.jpg)

Software that creates karaoke subtitles for AviUtl from LRC/KRA lyric files with ruby annotations.

- Usage instructions for the software will be updated continuously.

# Important Notes

- The software’s source code is free to use under the terms of its license.
- Videos produced using this software (including any modified versions) may be uploaded to video-sharing platforms; however, please credit "LRC2EXO-Python" in the video description (or similar) as the software used.

# Introduction

## Software Overview

### Features
- Generates karaoke subtitles that can be edited in AviUtl from karaoke subtitle files (supports LRC and KRA files with ruby annotations for txt2ass).
- Instead of using text objects, subtitles are pre-rendered as images. Because these images can be edited after generation, you can achieve subtitle effects that are not possible with video editing software alone.
- Enables versatile subtitle expressions by using both a lyric file and a settings file.
- **By including numbers such as “①” or “①②” in time-tagged lyrics, the software can automatically create subtitles with part separation.**

![Part Separation Example Image](./images/sample_part.jpg)

## Main Features

- Supports lyric blocks of up to 4 lines per screen.
- Compatible with both monospace and proportional fonts (automatically adjusts based on character width).
- Supports part separation display (with an icon at the beginning of lines).
- Automatically recognizes call-and-response lyrics marked by parentheses.
- Provides various output settings for subtitle images, including adjustments for character spacing in lyrics and ruby, outline width, etc.
- Offers EXO object settings such as display time for the start of singing and subtitle duration.

# Tutorial Using Sample Files

1. Check the contents of `sample/1_シャイニングスター（出典：魔王魂）.kra` (exported using the time-tagged lyric creation software "RhythmicaLyrics") from the sample plain lyric file `sample/1_シャイニングスター（出典：魔王魂）.txt`.

This software recognizes blank lines as delimiters between lyric blocks. For example, the first two lines form a single block:
```
[00:09:65]た[00:09:83]だ[00:10:39]風[00:10:39]([00:10:39]かぜ[00:11:17])[00:11:17]に[00:11:37]揺[00:11:37]([00:11:37]ゆ[00:11:54])[00:11:54]ら[00:11:71]れ[00:11:90]て[00:12:48]
[00:12:66]何[00:12:66]([00:12:66]なに[00:13:02])[00:13:02]も[00:13:19]考[00:13:19]([00:13:19]かんが[00:14:19])[00:14:19]え[00:14:57]ず[00:14:75]に[00:15:48]
```

Conversely, three consecutive lines without a blank line in between are recognized as a single block.
```
[00:35:29]シャ[00:35:45]イ[00:35:61]ニ[00:35:76]ン[00:35:94]グ[00:36:09]ス[00:36:24]ター[00:36:58]綴[00:36:58]([00:36:58]つづ[00:37:30])[00:37:30]れ[00:37:49]ば[00:37:94]
[00:38:10]夢[00:38:10]([00:38:10]ゆめ[00:38:46])[00:38:46]に[00:38:66]眠[00:38:66]([00:38:66]ねむ[00:39:22])[00:39:22]る[00:39:64]幻[00:39:64]([00:39:64]まぼろし[00:40:77])[00:40:77]が[00:41:00][00:41:38]掌[00:41:38]([00:41:38]てのひら[00:42:29])[00:42:29]に[00:42:67]降[00:42:67]([00:42:67]ふ[00:43:04])[00:43:04]り[00:43:41]注[00:43:41]([00:43:41]そそ[00:43:96])[00:43:96]ぐ[00:44:44]
[00:44:56]新[00:44:56]([00:44:56]あら[00:44:91])[00:44:91]た[00:45:29]な[00:45:66]世[00:45:66]([00:45:66]せ[00:46:07])[00:46:07]界[00:46:07]([00:46:07]かい[00:46:63])[00:46:63]へ[00:47:19]
```

2. Prepare your preferred TTF font file for generation. (For OTF or other formats, you will need to edit the Python source code.)
3. Open `settings.json`, set the font file path for "LYRIC" > "FONT_PATH" and "RUBY" > "FONT_PATH", then save the file.
4. In a terminal, navigate to the directory of this repository and run the following command to start generating the subtitles:

```shell
python main.py --input_lrc_path "./sample/2_シャイニングスター（出典：魔王魂）.kra" --exo_output_path "./sample/2_シャイニングスター（出典：魔王魂）.exo"
```

- Alternatively, run `python main_gui.py` to launch the GUI application, specify the file path, and execute the generation process.

![GUI](./images/gui.jpg)

5. Once subtitle generation is complete, open AviUtl and load the EXO file from the extended editing timeline.
6. Refer to the customization guide below to adjust the subtitle output settings.


# Karaoke Subtitle Creation Procedure and Customization Guide

## Overview of the Procedure

1. **Prepare a Plain Lyric File**  
   - Using `sample/1_シャイニングスター（出典：魔王魂）.txt` as a reference, create a lyric file where each block contains up to 4 lines and blank lines act as delimiters between blocks.

2. **Export a KRA File Using a Time-Tagging Software**  
   - Use software such as "[RhythmicaLyrics](https://suwa.pupu.jp/RhythmicaLyrics.html)" to save your time-tagged lyric file as an LRC or KRA file.  
     In the case of [RhythmicaLyrics](https://suwa.pupu.jp/RhythmicaLyrics.html), it supports the output format for ruby-annotated lyrics intended for txt2ass.

3. **Prepare the Font File and settings.json**  
   - Copy the font file you wish to use for the karaoke subtitles along with the provided `settings.json`, and then customize the settings.

4. **Generate Karaoke Subtitles with LRC2EXO-Python**  
   - Execute the following command to generate the subtitles.  
   - Alternatively, run `python main_gui.py` to launch the GUI application, specify the file paths, and execute the generation process.

   ```shell
   python main.py --input_lrc_path "＜path to the time-tagged lyric file＞" --exo_output_path "＜desired path for the exported EXO file＞" --settings_path "＜path to the settings file prepared in step 3＞"
   ```

5. **Edit in AviUtl**  
   - Open AviUtl, import the EXO file generated in step 4 via the extended editing timeline, and, if necessary, edit the image objects before exporting your video.


## Main Settings Overview

![Main Settings Overview](./images/settings_guide.jpg)

## List of Settings (settings.json)

### General Subtitle Settings

| Variable Name                             | Type                                               | Description                                                      |
|-------------------------------------------|----------------------------------------------------|------------------------------------------------------------------|
| `GENERAL.WIDTH`                           | int                                                | Image width for one line of subtitle                             |
| `GENERAL.HEIGHT`                          | int                                                | Image height for one line of subtitle                            |
| `GENERAL.X_BASE_INIT`                     | int                                                | Default X-coordinate for the first character (origin is the top-left of the one-line subtitle image) |
| `GENERAL.Y_LYRIC`                         | int                                                | Y-coordinate for the lyrics (origin is the top-left of the one-line subtitle image) |
| `GENERAL.Y_RUBY`                          | int                                                | Y-coordinate for the ruby (origin is the top-left of the one-line subtitle image) |
| `GENERAL.COLOR_FILL_BEFORE`               | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Text color before the wipe effect                                |
| `GENERAL.COLOR_STROKE_FILL_BEFORE`        | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Outline color before the wipe effect                             |
| `GENERAL.COLOR_FILL_AFTER`                | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Text color after the wipe effect                                 |
| `GENERAL.COLOR_STROKE_FILL_AFTER`         | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Outline color after the wipe effect                              |
| `GENERAL.COLOR_FILL_BEFORE_CHORUS`        | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Text color before the wipe effect for call-and-response or chorus lyrics |
| `GENERAL.COLOR_STROKE_FILL_BEFORE_CHORUS` | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Outline color before the wipe effect for call-and-response or chorus lyrics |
| `GENERAL.COLOR_FILL_AFTER_CHORUS`         | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Text color after the wipe effect for call-and-response or chorus lyrics |
| `GENERAL.COLOR_STROKE_FILL_AFTER_CHORUS`  | int [R(0–255), G(0–255), B(0–255), A(0–255)]         | Outline color after the wipe effect for call-and-response or chorus lyrics |

---

### Settings for Call-and-Response and Part Separation Modes

| Variable Name                             | Type        | Description                                                         |
|-------------------------------------------|-------------|---------------------------------------------------------------------|
| `GENERAL.CHANGE_TO_CHORUS_STR`            | str[]       | List of characters that trigger the switch to call-and-response or chorus mode |
| `GENERAL.CHANGE_TO_MAIN_STR`              | str[]       | List of characters that trigger the switch back to main mode from call-and-response or chorus mode |
| `GENERAL.CHANGE_TO_PART_STR`              | str[]       | List of characters that trigger the switch to part separation mode  |
| `GENERAL.PART_ICON`                       | str[]       | List of file paths for the icons used in part separation display      |
| `GENERAL.PART_ICON_HEIGHT`                | int         | Height of the part separation icon images                             |
| `GENERAL.PART_ICON_OFFSET_X`              | int         | X-coordinate offset for the part separation icon images                |
| `GENERAL.PART_ICON_OFFSET_Y`              | int         | Y-coordinate offset for the part separation icon images                |
| `GENERAL.PART_ICON_MARGIN_X`              | int         | Horizontal margin for the part separation icon images                 |
| `GENERAL.COLOR_FILL_BEFORE_PART`          | list[int [R(0–255), G(0–255), B(0–255), A(0–255)]] | List of text colors before the wipe effect for part separation mode   |
| `GENERAL.COLOR_STROKE_FILL_BEFORE_PART`   | list[int [R(0–255), G(0–255), B(0–255), A(0–255)]] | List of outline colors before the wipe effect for part separation mode |
| `GENERAL.COLOR_FILL_AFTER_PART`           | list[int [R(0–255), G(0–255), B(0–255), A(0–255)]] | List of text colors after the wipe effect for part separation mode    |
| `GENERAL.COLOR_STROKE_FILL_AFTER_PART`    | list[int [R(0–255), G(0–255), B(0–255), A(0–255)]] | List of outline colors after the wipe effect for part separation mode  |

---

### Subtitle Display Settings for AviUtl

| Variable Name                                | Type                        | Description                                                        |
|----------------------------------------------|-----------------------------|--------------------------------------------------------------------|
| `GENERAL.DISPLAY_BEFORE_TIME`                | int (unit: 10 milliseconds) | Start time for displaying the subtitle before the wipe effect       |
| `GENERAL.DISPLAY_AFTER_TIME`                 | int (unit: 10 milliseconds) | Duration for which the subtitle remains after the wipe effect        |
| `GENERAL.DISPLAY_CONNECT_THRESHOLD_TIME`     | int (unit: 10 milliseconds) | Threshold time for determining consecutive subtitle transitions      |
| `GENERAL.PROJECT_WIDTH`                      | int (unit: pixels)          | Video width of the AviUtl project                                    |
| `GENERAL.PROJECT_HEIGHT`                     | int (unit: pixels)          | Video height of the AviUtl project                                   |
| `GENERAL.PROJECT_FRAMERATE`                  | int                         | Frame rate of the AviUtl project                                     |
| `GENERAL.PROJECT_MARGIN_X`                   | int (unit: pixels)          | Margin from the left edge of the video for subtitle placement        |
| `GENERAL.PROJECT_LYRIC_X_OVERLAP_FACTOR`     | float                       | Overlap factor when centering multi-line lyrics                      |
| `GENERAL.PROJECT_Y_0_LYRIC`                   | int (unit: pixels)          | Y-coordinate for the first line of lyrics                            |
| `GENERAL.PROJECT_Y_1_LYRIC`                   | int (unit: pixels)          | Y-coordinate for the second line of lyrics                           |
| `GENERAL.PROJECT_Y_2_LYRIC`                   | int (unit: pixels)          | Y-coordinate for the third line of lyrics                            |
| `GENERAL.PROJECT_Y_3_LYRIC`                   | int (unit: pixels)          | Y-coordinate for the fourth line of lyrics                           |
| `GENERAL.PROJECT_Y_0_RUBY`                    | int (unit: pixels)          | Y-coordinate for the first line of ruby                              |
| `GENERAL.PROJECT_Y_1_RUBY`                    | int (unit: pixels)          | Y-coordinate for the second line of ruby                             |
| `GENERAL.PROJECT_Y_2_RUBY`                    | int (unit: pixels)          | Y-coordinate for the third line of ruby                              |
| `GENERAL.PROJECT_Y_3_RUBY`                    | int (unit: pixels)          | Y-coordinate for the fourth line of ruby                             |

---

### Lyric Subtitle Settings

| Variable Name              | Type                        | Description                                                      |
|----------------------------|-----------------------------|------------------------------------------------------------------|
| `LYRIC.FONT_PATH`          | str                         | Font file path                                                   |
| `LYRIC.FONT_SIZE`          | int (unit: pixels)          | Font size                                                        |
| `LYRIC.STROKE_WIDTH`       | int (unit: pixels)          | Stroke width for the subtitles                                   |
| `LYRIC.MARGIN_SPACE`       | int (unit: pixels)          | Margin for half-width space characters                           |
| `LYRIC.MARGIN_HALF`        | int (unit: pixels)          | Margin for half-width characters                                 |
| `LYRIC.MARGIN_FULL`        | int (unit: pixels)          | Margin for full-width characters                                 |
| `LYRIC.TEXT_WIDTH_MIN`     | int (unit: pixels)          | Minimum text width                                               |
| `LYRIC.Y_DRAW_OFFSET`      | int (unit: pixels)          | Y-axis offset when drawing text (compensates for font differences) |

---

### Ruby Subtitle Settings

| Variable Name              | Type                        | Description                                                      |
|----------------------------|-----------------------------|------------------------------------------------------------------|
| `RUBY.FONT_PATH`           | str                         | Font file path                                                   |
| `RUBY.FONT_SIZE`           | int (unit: pixels)          | Font size                                                        |
| `RUBY.STROKE_WIDTH`        | int (unit: pixels)          | Stroke width for the subtitles                                   |
| `RUBY.MARGIN_SPACE`        | int (unit: pixels)          | Margin for half-width space characters                           |
| `RUBY.MARGIN_HALF`         | int (unit: pixels)          | Margin for half-width characters                                 |
| `RUBY.MARGIN_FULL`         | int (unit: pixels)          | Margin for full-width characters                                 |
| `RUBY.TEXT_WIDTH_MIN`      | int (unit: pixels)          | Minimum text width                                               |
| `RUBY.Y_DRAW_OFFSET`       | int (unit: pixels)          | Y-axis offset when drawing text (compensates for font differences) |

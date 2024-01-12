from PyQt6.QtGui import QFontMetrics, QFont


def is_flat(lst):
    return all(not isinstance(i, list) for i in lst)


def flatten(input_list):
    flat_list = []
    for item in input_list:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def num_to_display_str(num):
    num_str = str(num)
    if len(num_str) > 8:
        return f"{num:.4e}"
    return num_str


def adapt_font_to_width(font, text, width):
    font_metrics = QFontMetrics(font)
    text_width = font_metrics.horizontalAdvance(text)
    if text_width > width:
        new_font = QFont(font)
        new_point_size = int(font.pointSizeF() * width / text_width)
        diff_to_old = abs(font.pointSizeF() - new_point_size)
        diff_to_old = diff_to_old % 2
        new_font.setPointSizeF(new_point_size - diff_to_old)
        return new_font
    return font


def adapt_font_to_width2(font, text, width):
    font_metrics = QFontMetrics(font)
    text_width = font_metrics.horizontalAdvance(text)
    if text_width > width:
        new_font = QFont(font)
        new_point_size = font.pointSizeF() * width / text_width
        new_font.setPointSizeF(new_point_size)
        return new_font
    return font


def find_incremental_series(s):
    sorted_with_index = sorted(enumerate(s), key=lambda x: x[1])

    sequences = []
    indices = []
    current_sequence = [sorted_with_index[0][1]]
    current_indices = [sorted_with_index[0][0]]

    for i in range(1, len(sorted_with_index)):
        if sorted_with_index[i][1] - current_sequence[-1] == 1:
            current_sequence.append(sorted_with_index[i][1])
            current_indices.append(sorted_with_index[i][0])
        else:
            if len(current_sequence) >= 3:
                sequences.append(current_sequence)
                indices.append(current_indices)
            current_sequence = [sorted_with_index[i][1]]
            current_indices = [sorted_with_index[i][0]]

    if len(current_sequence) >= 3:
        sequences.append(current_sequence)
        indices.append(current_indices)

    return sequences, indices

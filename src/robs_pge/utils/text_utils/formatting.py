from typing import Optional

from ..font import Font


def split_text(text: str, font: Optional[Font] = None, max_width: Optional[int] = None) -> list[str]:
    if font is None or max_width is None or max_width <= 0:
        return text.split("\n")

    def split_long_word(w: str) -> list[str]:
        chunks = []
        current_chunk = ""
        for char in w:
            test_chunk = current_chunk + char
            if font.get_render_size(test_chunk).x <= max_width:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = char
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    final_lines: list[str] = []

    for paragraph in text.split("\n"):
        if not paragraph:
            final_lines.append("")
            continue

        words = paragraph.split(" ")
        current_line_words: list[str] = []

        for word in words:
            word_width = font.get_render_size(word).x

            if word_width > max_width:
                if current_line_words:
                    final_lines.append(" ".join(current_line_words))
                    current_line_words = []

                word_chunks = split_long_word(word)
                final_lines.extend(word_chunks[:-1])
                if word_chunks:
                    current_line_words.append(word_chunks[-1])
                continue

            test_line = " ".join(current_line_words + [word]) if current_line_words else word
            if font.get_render_size(test_line).x <= max_width:
                current_line_words.append(word)
            else:
                final_lines.append(" ".join(current_line_words))
                current_line_words = [word]

        if current_line_words:
            final_lines.append(" ".join(current_line_words))

    return final_lines
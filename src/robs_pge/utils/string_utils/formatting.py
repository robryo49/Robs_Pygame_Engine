import math
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


def format_number(number: int | float, max_symbols: int | None = None, precision: int = 6, force_scientific: bool = False, ) -> str:
    if number == 0:
        return "0"

    if precision < 0:
        raise ValueError("precision must be >= 0")

    sign = "-" if number < 0 else ""
    value = abs(number)

    if not force_scientific and max_symbols is not None:

        if isinstance(value, int):
            integer_digits = len(str(value))

            required_digits = integer_digits

        else:
            if not math.isfinite(value):
                return str(number)

            exponent = math.floor(math.log10(value))

            if exponent >= 0:
                integer_digits = exponent + 1

                fractional_digits = min(precision, max(0, len(str(value).split(".")[1].rstrip("0"))) if "." in str(value) else 0,)
                required_digits = integer_digits + fractional_digits

            else:
                decimal = f"{value:.{precision}f}".rstrip("0").rstrip(".")
                required_digits = sum(c.isdigit() for c in decimal)

        if required_digits <= max_symbols:
            if isinstance(value, int):
                return f"{sign}{value}"

            return f"{sign}{value:.{precision}f}".rstrip("0").rstrip(".")

    if max_symbols is None and not force_scientific:
        if isinstance(value, int):
            return f"{sign}{value}"

        return f"{sign}{value:.{precision}f}".rstrip("0").rstrip(".")

    if isinstance(value, int):

        exponent = int((value.bit_length() - 1) * math.log10(2))
        power = 10 ** exponent

        if value < power:
            exponent -= 1
            power //= 10
        elif value >= power * 10:
            exponent += 1

        exponent_digits = len(str(exponent))

        if max_symbols is None:
            mantissa_digits = precision + 1
        else:
            mantissa_digits = max_symbols - exponent_digits
            mantissa_digits = max(1, mantissa_digits)

        decimals = min(precision, mantissa_digits - 1)

        divisor = 10 ** (exponent - decimals)
        significant = value // divisor
        digits = str(significant)[:mantissa_digits]
        mantissa = digits[0]

        if len(digits) > 1:
            decimal_part = digits[1:].rstrip("0")
            if decimal_part:
                mantissa += "." + decimal_part

        return f"{sign}{mantissa}e{exponent}"

    if not math.isfinite(value):
        return str(number)

    exponent = math.floor(math.log10(value))
    exponent_digits = len(str(exponent))

    if max_symbols is None:
        mantissa_digits = precision + 1
    else:
        mantissa_digits = max(1, max_symbols - exponent_digits)

    decimals = min(precision, mantissa_digits - 1)

    result = f"{value:.{decimals}e}"
    mantissa, exponent_str = result.split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{sign}{mantissa}e{int(exponent_str)}"
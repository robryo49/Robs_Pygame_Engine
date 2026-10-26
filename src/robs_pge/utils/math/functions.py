"""General math helpers for interpolation, vectors, transforms, and universal operations."""

import operator
from math import cos, pi, sin
from random import random as rand
from typing import Optional, cast

from glm import vec1, vec2, vec3, vec4
from pygame import Color
from pyglm import glm


def lerp[T](a: T, b: T, t: float) -> T:
    """Interpolate between two values.

    :param a: Start value.
    :param b: End value.
    :param t: Interpolation factor, typically between 0 and 1.
    :return: The interpolated value, with pygame colors blended per channel.
    """
    if isinstance(a, Color) and isinstance(b, Color):
        return Color(
            int(a.r + (b.r - a.r) * t),
            int(a.g + (b.g - a.g) * t),
            int(a.b + (b.b - a.b) * t),
            int(a.a + (b.a - a.a) * t)
        )
    return glm.lerp(a, b, t)

def clamp[T](v: T, mini: float=0, maxi: float=1) -> T:
    """Clamp a value between minimum and maximum bounds.

    :param v: Value to clamp.
    :param mini: Lower bound.
    :param maxi: Upper bound.
    :return: The value constrained to the given range.
    """
    return glm.clamp(v, mini, maxi)

def round_sig(x: float, digits: int) -> float:
    """Round a value to a number of significant digits.

    :param x: Value to round.
    :param digits: Number of significant digits to keep.
    :return: The rounded value, or 0.0 when ``x`` is zero.
    """
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(glm.log(abs(x))))


def invert_y(vec: vec2):
    """Return a vector with its y component negated.

    :param vec: Input vector.
    :return: The vertically inverted vector.
    """
    return vec2(vec.x, -vec.y)

def invert_uv_y(uv: vec2):
    """Flip a UV coordinate vertically around 0.5.

    :param uv: Input UV coordinate.
    :return: The vertically flipped UV coordinate.
    """
    return vec2(uv.x, 1-uv.y)

def invert_x(vec: vec2):
    """Return a vector with its x component negated.

    :param vec: Input vector.
    :return: The horizontally inverted vector.
    """
    return vec2(-vec.x, vec.y)

def invert_uv_x(uv: vec2):
    """Flip a UV coordinate horizontally around 0.5.

    :param uv: Input UV coordinate.
    :return: The horizontally flipped UV coordinate.
    """
    return vec2(1-uv.x, uv.y)

def invert_uv(uv: vec2):
    """Flip both UV axes around 0.5.

    :param uv: Input UV coordinate.
    :return: The flipped UV coordinate.
    """
    return vec2(1-uv.x, 1-uv.y)


def get_object_dims(dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None,
                    content_dims: Optional[vec2] = None, margin: Optional[float] = None) -> vec2:
    """Resolve object dimensions from explicit size, content size, and margin.

    :param dims: Base dimensions used when ``width`` or ``height`` is not provided.
    :param width: Explicit width override.
    :param height: Explicit height override.
    :param content_dims: Content size expanded by ``margin`` before comparison.
    :param margin: Margin added to each side of the content dimensions.
    :return: The resolved width and height.
    """
    if content_dims is None:
        margined_dims = vec2()
    else:
        margined_dims = content_dims + vec2(2*margin if margin is not None else 0)
    
    width = width if width is not None else max(margined_dims.x, dims.x if dims is not None else 0)
    height = height if height is not None else max(margined_dims.y, dims.y if dims is not None else 0)
    
    return vec2(width, height)

def rotated_surface_dims(dims: vec2, rotation: float):
    """Compute the axis-aligned bounds of a rotated rectangle.

    :param dims: Unrotated rectangle dimensions.
    :param rotation: Rotation angle in degrees.
    :return: The width and height of the rotated bounding box.
    """
    return vec2(
        abs(dims.x * cos(rotation*pi/180)) + abs(dims.y * sin(rotation*pi/180)),
        abs(dims.y * cos(rotation*pi/180)) + abs(dims.x * sin(rotation*pi/180))
    )


def surface_pos_from_pixel_pos(pixel_pos: vec2, dims: vec2, rotation: float=0):
    """Map a pixel position into the larger surface used for a rotated image.

    :param pixel_pos: Pixel position in the unrotated image.
    :param dims: Unrotated image dimensions.
    :param rotation: Image rotation angle in degrees.
    :return: The corresponding position on the rotated surface.
    """
    if rotation:
        return rotate(pixel_pos - dims/2, -rotation) + rotated_surface_dims(dims, rotation) / 2
    else:
        return pixel_pos

def surface_pos_from_uv_pos(uv_pos: vec2, dims: vec2, rotation: float=0):
    """Map a UV position into the larger surface used for a rotated image.

    :param uv_pos: UV position within the image.
    :param dims: Unrotated image dimensions.
    :param rotation: Image rotation angle in degrees.
    :return: The corresponding position on the rotated surface.
    """
    return surface_pos_from_pixel_pos(uv_pos*dims, dims, rotation)


def random[T](a: T = 0.0, b: T = 1.0) -> T:
    """Return a random value between two bounds.

    :param a: Lower bound.
    :param b: Upper bound.
    :return: A random value between ``a`` and ``b``.
    """
    return a + rand() * (b - a)


def rotate(vec: vec2, angle_degrees: float) -> vec2:
    """Rotate a 2D vector by an angle in degrees.

    :param vec: Vector to rotate.
    :param angle_degrees: Rotation angle in degrees.
    :return: The rotated vector.
    """
    return rotate_rad(vec, glm.radians(angle_degrees))

def rotate_rad(vec: vec2, angle_rad: float) -> vec2:
    """Rotate a 2D vector by an angle in radians.

    :param vec: Vector to rotate.
    :param angle_rad: Rotation angle in radians.
    :return: The rotated vector.
    """
    return glm.rotateZ(vec3(vec.x, vec.y, 0), angle_rad).xy

def length(v) -> float:
    """Return the length of a vector.

    :param v: Input vector.
    :return: The vector's magnitude.
    """
    return glm.length(v)


def get_transformation_matrix(translation: vec2, rotation: float, scale: float) -> glm.mat4:
    """Build a translation, rotation, and uniform scale matrix.

    :param translation: Translation offset.
    :param rotation: Rotation angle in degrees.
    :param scale: Uniform scale factor.
    :return: The composed transformation matrix.
    """
    mat = glm.mat4(1.0)
    mat = glm.translate(mat, glm.vec3(translation.x, translation.y, 0.0))
    mat = glm.rotate(mat, glm.radians(rotation), glm.vec3(0.0, 0.0, 1.0))
    mat = glm.scale(mat, glm.vec3(scale, scale, 1.0))
    return mat

def get_inverse_transformation_matrix(translation: vec2, rotation: float, scale: float) -> glm.mat4:
    """Build the inverse of a translation, rotation, and uniform scale matrix.

    :param translation: Translation offset.
    :param rotation: Rotation angle in degrees.
    :param scale: Uniform scale factor.
    :return: The inverse transformation matrix.
    """
    return cast(glm.mat4, cast(object, glm.inverse(get_transformation_matrix(translation, rotation, scale))))

def apply_transformation_matrix_on_point(mat: glm.mat4, point: vec2):
    """Apply a transformation matrix to a 2D point.

    :param mat: Transformation matrix.
    :param point: Point to transform.
    :return: The transformed point.
    """
    return cast(vec4, cast(object, mat * vec4(point.x, point.y, 0, 1))).xy

def apply_transformation_matrix_on_vec(mat: glm.mat4, vec: vec2):
    """Apply a transformation matrix to a 2D direction vector.

    :param mat: Transformation matrix.
    :param vec: Direction vector to transform.
    :return: The transformed direction vector.
    """
    return cast(vec4, cast(object, mat * vec4(vec.x, vec.y, 0, 0))).xy


def _is_color(value) -> bool:
    return isinstance(value, Color)

def _is_math_iterable(value) -> bool:
    return isinstance(value, (Color, vec1, vec2, vec3, vec4, tuple, list))

def _clamp_channel(value: float) -> int:
    return max(0, min(255, int(round(value))))

def _cast(blueprint, values, clamp_color=True):
    """Convert a sequence of values into the type of a blueprint value.

    :param blueprint: Value whose type determines the output type.
    :param values: Sequence of values to convert.
    :param clamp_color: Whether color channels are clamped to 0 through 255.
    :return: The converted value, preserving vector, tuple, and list types.
    """
    vals = list(values)
    
    if _is_color(blueprint):
        if clamp_color:
            return Color(*[_clamp_channel(v) for v in vals][:4])
        return tuple(vals)
    
    if isinstance(blueprint, (vec1, vec2, vec3, vec4)):
        return type(blueprint)(*vals[:len(blueprint)])
    
    if isinstance(blueprint, (tuple, list)):
        return type(blueprint)(vals)
    
    return vals

def _universal_op(a, b, op, clamp_color=True):
    """Apply a binary operation element-wise to math iterables or scalars.

    :param a: Left operand.
    :param b: Right operand.
    :param op: Binary operation to apply.
    :param clamp_color: Whether color results are clamped to 0 through 255.
    :return: The operation result, preserving iterable types where applicable.
    """
    a_is_iter = _is_math_iterable(a)
    b_is_iter = _is_math_iterable(b)
    
    if a_is_iter and b_is_iter:
        blueprint = a if _is_color(a) else (b if _is_color(b) else a)
        return _cast(blueprint, (op(v1, v2) for v1, v2 in zip(a, b)), clamp_color)
    
    if a_is_iter and isinstance(b, (int, float)):
        return _cast(a, (op(v, b) for v in a), clamp_color)
    
    if isinstance(a, (int, float)) and b_is_iter:
        return _cast(b, (op(a, v) for v in b), clamp_color)
    
    return op(a, b)


def add(a, b):
    """Add two values, operating element-wise for colors and vectors.

    :param a: Left operand.
    :param b: Right operand.
    :return: The sum, with color channels clamped to 0 through 255.
    """
    return _universal_op(a, b, operator.add, clamp_color=True)

def subtract(a, b):
    """Subtract two values, operating element-wise for colors and vectors.

    :param a: Left operand.
    :param b: Right operand.
    :return: The difference, without color clamping when both operands are iterables.
    """
    is_delta = _is_math_iterable(a) and _is_math_iterable(b)
    return _universal_op(a, b, operator.sub, clamp_color=not is_delta)

def multiply(a, b):
    """Multiply two values, operating element-wise for colors and vectors.

    :param a: Left operand.
    :param b: Right operand.
    :return: The product, with color channels clamped to 0 through 255.
    """
    return _universal_op(a, b, operator.mul, clamp_color=True)

def divide(a, b):
    """Divide two values, operating element-wise for colors and vectors.

    :param a: Numerator.
    :param b: Denominator.
    :return: The quotient, with color channels clamped to 0 through 255.
    :raises ZeroDivisionError: If the denominator is a numeric zero.
    """
    if isinstance(b, (int, float)) and b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return _universal_op(a, b, operator.truediv, clamp_color=True)

def power(a, b):
    """Raise values to a power, operating element-wise for colors and vectors.

    :param a: Base value.
    :param b: Exponent value.
    :return: The result, with color channels clamped to 0 through 255.
    """
    return _universal_op(a, b, operator.pow, clamp_color=True)


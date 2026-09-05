# Robs Pygame Engine

A lightweight game engine built with Pygame for creating 2D games in Python.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Author

**RobRyo49** - [GitHub](https://github.com/robryo49)

## UI Widgets

The engine provides built-in UI widgets such as `ValueSelectorObject` and `ValueCyclerObject` created via `ObjectFactory`:

```python
# Value selector (bounded numeric increment/decrement selection)
self.create_object.ui.value_selector(
    vec2(400, 300), vec2(320, 48),
    start_value=10, min_value=0, max_value=100,
    increments=[1, 5, 10]
)

# Value cycler (cycling through a fixed set of values with arrow buttons)
self.create_object.ui.value_cycler(
    vec2(400, 360), vec2(220, 48),
    values=("Easy", "Normal", "Hard")
)
```


# Pull Request: Refactor/sentsplit-cleanup

## Summary

Clean up and refactor sentsplit for better readability, maintainability, and consistency across the codebase.

## Changes

### Test Refactoring (test_segment.py)

Flattened `TestUnsupportedLanguageInitialization` class-based tests to function-based tests for consistency with other test files in the project. The file `test_options.py` already uses function-based tests, so this brings `test_segment.py` in line with the existing style. This also follows pytest best practices for simpler test structure.

### Utils Refactoring (sentsplit/utils.py)

Simplified `split_keep_multiple_separators` function by replacing the `reduce`-based implementation with an explicit for-loop. The original reduce lambda with conditional logic was difficult to read and maintain. The new implementation makes the intent clear:

```python
# Before
return reduce(
    lambda acc, elem: acc[:-1] + [acc[-1] + elem] if (elem in separators) else acc + [elem],
    re.split(rgx_multiple_separators, string),
    [],
)

# After
sentences = []
for elem in re.split(rgx_multiple_separators, string):
    if elem in separators:
        sentences[-1] += elem
        continue
    sentences.append(elem)
return sentences
```

### Segment & Config Cleanup (sentsplit/segment.py, sentsplit/config.py)

Renamed several variables for clarity. The parameter `string` was renamed to `input` because the function accepts both a string and a list of strings, so "string" was misleading. The variable `chars_strings` was renamed to `char_lists` for better, more descriptive naming. The variable `multiple_spaces_positions_strings` was shortened to `multiple_spaces_position_lists` for a clearer plural form.

The `_substitute_multiple_spaces` method was refactored to use a single `re.sub` call with a replacer function that records positions during substitution, instead of making separate `finditer` and `sub` calls.

Removed redundant step comments like "Step 1:", "Step 2:", etc., as they added noise without providing value. Also removed dead code comments about deprecated imports and an extra blank line in config.py.

## Test Results

All 23 tests pass.

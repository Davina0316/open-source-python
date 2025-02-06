# Static Analysis and Code Formatting Configuration

## Ruff Configuration
This project enables all possible checks in `ruff` by setting `"ALL"` in the configuration.
However, the following rules have been disabled for specific reasons:

- **E501**: Line length → The maximum line length has been increased to `100` for better readability.
- **ANN101**: Missing type annotation for `self` → `self` and `cls` are standard in Python and do not need type annotations.
- **D100**: Missing module-level docstring → In small projects, requiring a docstring at the module level can be redundant.
- **D103**: Missing function docstring → Test functions do not always require docstrings since the test function name should be self-explanatory.

## Mypy Configuration
All strict checks in `mypy` have been enabled to ensure strong type safety.
However, the following checks have been disabled:

- **ignore_missing_imports**: Some third-party libraries may not provide type annotations, causing unnecessary warnings.


# Bagels Testing Guide
<br>

## Overview

<br>
<p>This document explains how to run the tests for the Bagels project, what files were created or modified for testing, and summarizes coverage and known issues.</p> 
<p>The tests were written by wagscoll and svanalex as part of a project for CS4499.</p>
<br>

## Running the Tests

<br>

- Step 1:
  - Active viritual environment
`source .venv/bin/activate`

<br>

- Step 2:
  - Run pytest
`uv run pytest`

<br><br>

_*Note: testpaths[] within pyproject.toml has been modified to only run the tests Alex and I have written._
<br>
<br>

# Files Modified
<br>

> /managers/utils/validation.py

<p>has been modified to improve error handling and validation clarity throughout the Bagels project. </p>


<p>Both exceptions are used in validation helper functions:</p>

 - validate_number()
 - validate_date()
 - validate_autocomplete()
 - validateForm()


<p>Each function uses try/except blocks to catch these exceptions and populate an errors dictionary — ensuring the user gets meaningful error messages without crashing the application. </p>

<br>

 **Example:**
```
except (InvalidFormDataException, AutocompleteOptionMismatchException) as e:
    errors[fieldKey] = str(e)
    isValid = False
```

<br>

## *InvalidFormDataException*

<br>

**Purpose:**

<p>Raised when a form field contains invalid or inconsistent data such as:
 - Missing required fields
 - Numeric values outside allowed min/max bounds
 - Incorrect date formats
</p>
 
<br>

**Example:**

```
if not value and field.is_required:
    raise InvalidFormDataException(f"Field '{field.key}' is required")

if field.min is not None and num_val <= field.min:
    raise InvalidFormDataException(f"Value must be greater than {field.min}")
```
<br>

**Usefuleness**: 

<p>
It replaces generic ValueError exceptions with a clear, domain-specific error type that tells the user why a form input failed.
</p>    

<br>
<br>

## *AutocompleteOptionMismatchException*

<br>

**Purpose:**

<p>
Raised when a user’s input doesn’t match any of the allowed autocomplete options — either because the selection wasn’t tab-confirmed, or because it’s missing entirely.
</p>

<br>

**Example:**

```
if not field.options or not field.options.items:
    return True, None

if not matching_items:
    raise AutocompleteOptionMismatchException(f"Invalid selection for field '{field.key}'")
```

<br>

**Usefuleness**: 

<p>
This exception provides a precise mechanism to handle invalid dropdown/autocomplete entries instead of failing silently or producing unclear errors.
</p>

## Files Tested
The following files files have been added and tested:
- tests/test_config.py
- tests/utils/test_validation.py
- tests/components/modules/test_incomemode.py
- tests/managers/test_person.py
- tests/ADD_THIS_ONE_LATER_!_!



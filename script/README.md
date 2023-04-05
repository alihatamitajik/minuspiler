# Grammar Preprocessor

The `prepare.js` script creates a python file `script/grammar.json` which has
the following structure:

```json
{
  "Program": {
    "first": [],
    "follow": [],
    "rules": [
      { "rule": ["Declaration-list"], "prediction": ["Declaration-list"] }
    ]
  },
  "Declaration-list": {
    "first": [],
    "follow": [],
    "rules": [
      { "rule": ["Declaration", "Declaration-list"], "prediction": ["..."] },
      { "rule": [null], "prediction": ["..."] }
    ]
  },
  "...": "..."
}
```

This structure could be used to build the parser using transition diagram
technique. The created JSON file will be copied and pasted as a docstring inside
the parser module and it would be read into a dictionary so it can be used for
the parser.

This script can be executed using the following command:

```bash
node prepare.js
```

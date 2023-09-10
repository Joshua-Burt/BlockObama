Several directories are not included in the GitHub repo, and instead are created at first-run.

Currently, the `json_files` director is generated fully at first-run, but `sounds` is not.
This will be amended in a later date.

Currently, you will need to manually create the sounds directory, and the two subdirectories.

Below is the general file structure of both of those directories:

```
[Project Directory]
    |
    └ — sounds
    |   |
    |   └ intros
    |   |   └ {file_name}.mp3
    |   |   └ etc.
    |   |
    |   └ pay_to_play
    |       └ {file_name}.mp3
    |       └ etc.
    |
    └ — json_files
        └ config.json
        └ item_prices.json
        └ jackpot.json
        └ sayings.json
        └ users.json
```

You can find out more about each of the JSON files in `json_file_structure.md`

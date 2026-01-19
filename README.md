# Sage Drop
Sage Drop is a Python Command Line Interface for Sage. You can start, pause and resume work on Sage. You can
check your work-time balance and download all documents from Sage.

## Installation

1. Install `pipx` (see [here](https://realpython.com/python-pipx/))
2. Open a console
3. Define the environment variables as follows (for Windows
   see [here](https://bodo-schoenfeld.de/umgebungsvariablen-in-windows-11-bearbeiten/)):
    ```
    export SAGE_BASE_URL=http://sage.fabfab.de/
    export SAGE_PASSWORD=<<YOUR SAGE PASSWORD>>
    export SAGE_USER=<<YOUR SAGE USERNAME>>
    ```

4. Run `pipx install install git+https://github.com/nleipi/sage-drop`
5. Run `sage-drop` to see the help
6. Enjoy!

## Usage
Some examples how to use sage-drop.

### Current Work-Time
Show work-time balance summed up to current time.
```bash
$ sage balance
Balance: 6:21
```

### Download all Documents
Without arguments downloads all documents from sage to the current directory.
Configure with `--out-dir <<TARGET_DIR>>`
```bash
$ sage documents --out-dir documents
Downloading: documents/201910_Lohnscheine.pdf ...
Done.
Downloading: documents/201911_Lohnscheine.pdf ...
Done.
Downloading: documents/201912_Lohnscheine.pdf ...
Done.
Downloading: documents/202001_Lohnscheine.pdf ...
Done.
Downloading: documents/202002_Lohnscheine.pdf ...
Done.
```
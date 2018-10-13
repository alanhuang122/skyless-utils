# skyless-utils
Utilities for serialization of Sunless Skies data.

Python 3.7 is required.

This codebase is largely based off [fl-utils](https://github.com/alanhuang122/fl-utils).

`convert.py` will take individual serialized data files and combine them into a single data file, in a usable format.

`init.py` loads the data file produced by `convert.py`.

`skyless.py` contains methods to format the data.

## How to use
1. Extract the TextAsset files from the Unity resources files.
2. Convert from binary format to JSON format.<br>
  The C# file `Reserialize.cs` will perform this function.<br>
  Namespace `Skyless.Assets.Code.Skyless.Utilities.Serialization` is defined in `Assembly-CSharp.dll`, in the Sunless Skies directory.

NB: There's also [an indexed S3 bucket](https://data.skylesssetup.storynexus.com) with JSON files. The provenance and status of said files are unknown to me at this moment.

Running `convert.py` from the directory containing the JSON-serialized data will produce a file suitable for use with `init.py`.

Run `python -i init.py` from the directory containing the data file.

To format Storylets, Qualities, etc., ```print(skyless.Storylet.get(284781))``` or ```print(skyless.Quality.get(804))```, for example.

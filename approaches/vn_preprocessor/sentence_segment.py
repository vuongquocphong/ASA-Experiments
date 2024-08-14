import os
import sys

from .preprocessor import *

CMD_OVERWRITE_OPTION = '-ow'

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) >= 3:
        # At least 2 arguments have been passed
        inp = sys.argv[1]
        out = sys.argv[2]

        # Remove out file if exist
        if os.path.exists(out): os.remove(out)

        # Define overwrite option
        overwrite = len(sys.argv) >= 4 and sys.argv[3] == CMD_OVERWRITE_OPTION
        p = Preprocessor(Language.vietnamese)
        try:
            p.segment_files_to_sentences(inp, out, {'overwrite': overwrite})
        except (FileNotFoundError, FileExistsError) as errors:
            for e in errors.args:
                if e:
                    print(e)
    else:
        print('Missing arguments. Arguments: input output [-ow]')

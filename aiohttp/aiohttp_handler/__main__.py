import sys

from aiohttp_handler.main import main

if len(sys.argv) > 1 and 'config' in sys.argv[1]:
    main(config_filename=sys.argv[1])
else:
    main()

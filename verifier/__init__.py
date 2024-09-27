def main():
    import logging
    from .runners import runners
    from .config import config

    import argparse
    import argcomplete
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Generate evidence for standard issues")
    subparsers = parser.add_subparsers(dest="runner", metavar="runner", required=True)
    for runner in runners:
        runner(subparsers)

    argcomplete.autocomplete(parser)
    args, extra_args = parser.parse_known_args()
    args.func(args, extra_args)


if __name__ == "__main__":
    main()

import sys
import argparse
import logging

LOG = logging.getLogger(__name__)


class Arg(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ArgGroup(object):

    def __init__(self, title, options):
        self.title  = title
        self.options = options


class SubCli(object):
    """Add class property NAME to set subcommaon name
    """
    ARGUMENTS = []

    def __call__(self, args):
        raise NotImplementedError()

    @classmethod
    def arguments(cls):
        return cls.ARGUMENTS


class SubCliParser(object):

    def __init__(self, title):
        self.parser = argparse.ArgumentParser()
        self.sub_parser = self.parser.add_subparsers(title=title)
        self._args = None

    def parse_args(self):
        from easy2use.globals import log                  # noqa

        self._args = self.parser.parse_args()
        if not hasattr(self._args, 'cli'):
            self.print_usage()
            sys.exit(1)

        log_level = logging.DEBUG if getattr(self._args, 'debug', False) \
            else logging.INFO
        log.basic_config(
            filename=getattr(self._args, 'log_file', None),
            max_mb=getattr(self._args, 'max_mb', None),
            backup_count=getattr(self._args, 'backup_count', None),
            level=log_level)
        LOG.debug('args: %s', self._args)

        return self._args

    def call(self):
        if not self._args:
            self.parse_args()
        return self._args.cli()(self._args)

    def register_clis(self, *args):
        for arg in args:
            self.register_cli(arg)

    def register_cli(self, cls):
        """params cls: CliBase type"""
        if not issubclass(cls, SubCli):
            raise ValueError(f'{cls} is not the subclass of {SubCli}')
        name = cls.NAME if hasattr(cls, 'NAME') else cls.__name__
        sub_parser = self.sub_parser.add_parser(name)

        for argument in cls.arguments():
            if isinstance(argument, Arg):
                sub_parser.add_argument(*argument.args, **argument.kwargs)
            elif isinstance(argument, ArgGroup):
                arg_group = sub_parser.add_argument_group(
                    title=argument.title)
                self._register_args(arg_group, argument.options)
            else:
                raise ValueError('Invalid arg class %s', argument.__class__)

        sub_parser.set_defaults(cli=cls)

    def _register_args(self, parser, args):
        for arg in args:
            parser.add_argument(*arg.args, **arg.kwargs)

    def print_usage(self):
        self.parser.print_usage()

    def print_help(self):
        self.parser.print_help()


def get_sub_cli_parser(title):
    return SubCliParser(title)


def register_cli(sub_cli_parser):

    def wrapper(cls):
        cli_parser = sub_cli_parser.sub_parser.add_parser(cls.NAME)
        for argument in cls.ARGUMENTS:
            cli_parser.add_argument(*argument.args, **argument.kwargs)
        cli_parser.set_defaults(cli=cls)
        return cls

    return wrapper

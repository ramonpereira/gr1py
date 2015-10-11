"""
Command-line interface to gr1py
"""
from __future__ import print_function
from __future__ import absolute_import
import sys
import argparse
import pprint

from . import __version__
from .form import gr1c, util
from .tstruct import ts_from_expr
from .solve import check_realizable, synthesize
from . import output


def main(args=None):
    parser = argparse.ArgumentParser(prog='gr1py')
    parser.add_argument('FILE', nargs='?',
                        help='input specification file; default format of gr1c')
    parser.add_argument('-V', action='store_true', dest='show_version',
                        help='print version number and exit')
    parser.add_argument('-r', action='store_true', dest='check_realizable',
                        help='check realizability')
    parser.add_argument('-t', metavar='TYPE', action='store',
                        dest='output_format', default='json',
                        help=('strategy output format; default is "json"; '
                              'supported formats: json, gr1caut'))

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    if args.show_version:
        print('gr1py '+__version__)
        return 0

    args.output_format = args.output_format.lower()
    if args.output_format not in ['json', 'gr1caut']:
        print('Unrecognized output format, "'+str(args.output_format)+'". Try "-h".')
        return 1

    if args.FILE is None:
        f = sys.stdin
    else:
        f = open(args.FILE, 'r')

    asd = gr1c.parse(f.read())
    if f is not sys.stdin:
        f.close()

    symtab, exprtab = util.gen_expr(asd)
    exprtab = util.fill_empty(exprtab)
    tsys = ts_from_expr(symtab, exprtab)

    if args.check_realizable:
        if check_realizable(tsys, exprtab):
            print('Realizable.')
            return 0
        else:
            print('Not realizable.')
            return 3
    else: # Default behavior is to synthesize
        strategy = synthesize(tsys, exprtab)
        if strategy is None:
            print('Not realizable.')
            return 3
        else:
            if args.output_format == 'json':
                print(output.dump_json(symtab, strategy))
            elif args.output_format == 'gr1caut':
                print(output.dump_gr1caut(symtab, strategy))
            else:
                raise ValueError('Unrecognized output format, "'+str(args.output_format)+'"')
                return 1

    return 0

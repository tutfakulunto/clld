"""
Functionality to be called from command line scripts is provided in this module.

.. note:

    The various scripts are installed when running `python setup.py develop|install`,
    following the specification in `setup.py`.

.. seealso: http://www.scotttorborg.com/python-packaging/command-line-scripts.html\
#the-console-scripts-entry-point
"""
from __future__ import unicode_literals, division, absolute_import, print_function
import os
import argparse

import transaction

from clld.interfaces import IDownload
from clld.scripts.util import parsed_args, gbs_func
from clld.scripts.freeze import freeze_func, unfreeze_func
from clld.scripts.internetarchive import ia_func
from clld.scripts.llod import llod_func, register


def llod():  # pragma: no cover
    """
    Create an RDF dataset for an app and register it with datahub.io
    """
    args = parsed_args(bootstrap=True, description=llod.__doc__)
    llod_func(args)
    register(args)


def internetarchive(**kw):  # pragma: no cover
    """
    Add information about availability on Internet Archive to Source objects.
    """
    add_args = [(("command",), dict(help="download|verify|update"))]
    kw.setdefault('description', internetarchive.__doc__)
    args = parsed_args(*add_args, **kw)
    with transaction.manager:
        ia_func(args.command, args, kw.get('sources'))


def create_downloads(**kw):  # pragma: no cover
    """
    Create all registered downloads (locally).
    """
    args = parsed_args(bootstrap=True, description=create_downloads.__doc__)
    for name, download in args.env['registry'].getUtilitiesFor(IDownload):
        args.log.info('creating download %s' % name)
        download.create(args.env['request'])


def google_books(**kw):  # pragma: no cover
    add_args = [
        (("command",), dict(help="download|verify|update|cleanup")),
        (("--api-key",), dict(default=kw.get('key', os.environ.get('GBS_API_KEY')))),
    ]

    args = parsed_args(*add_args, **kw)
    if args.command == 'download' and not args.api_key:
        raise argparse.ArgumentError(None, 'no API key found for download')

    with transaction.manager:
        gbs_func(args.command, args, kw.get('sources'))


def freeze():  # pragma: no cover
    """
    Create a dump a an app's database as set of csv files in an archive data.zip
    """
    freeze_func(parsed_args(bootstrap=True, description=freeze.__doc__))


def unfreeze():  # pragma: no cover
    """
    Import an app's data from a frozen dump into an sqlite db.
    """
    unfreeze_func(parsed_args(description=unfreeze.__doc__))

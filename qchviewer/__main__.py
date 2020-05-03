#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import tempfile
import os.path
import jinja2
from subprocess import run
from whichcraft import which


def system(cmd):
    click.echo(cmd)
    os.system(cmd)


def find_qhc_generator():
    generators = ["qcollectiongenerator", "qhelpgenerator"]
    for generator in generators:
        if which(generator) is None:
            continue

        p = run([generator, "-v"], shell=True, capture_output=True)
        if b"o such file" in p.stderr:
            continue

        return generator

    raise FileNotFoundError()


@click.command()
@click.argument("qchfile")
def main(**kwargs):
    """
    Console script for qchviewer

    QCHFILE: The qch file path
    """

    if not os.path.isfile(kwargs["qchfile"]):
        raise click.BadParameter(
            "%s not a valid qch file!" % kwargs["qchfile"]
        )

    template = jinja2.Template(
        """\
<?xml version="1.0" encoding="utf-8" ?>
<QHelpCollectionProject version="1.0">
	<assistant>
		<title>{{ title }}</title>
		<currentFilter>Default</currentFilter>
		<enableAddressBar visible="true">true</enableAddressBar>
	</assistant>
	<docFiles>
		<register>
			<file>{{ path }}</file>
		</register>
	</docFiles>
</QHelpCollectionProject>

"""
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        qhcp_path = os.path.realpath(os.path.join(temp_dir, "main.qhcp"))
        qhcp_content = template.render(
            title=os.path.basename(kwargs["qchfile"]),
            path=os.path.realpath(kwargs["qchfile"]),
        )

        with open(qhcp_path, "wb") as qhcp_file:
            qhcp_file.write(qhcp_content.encode("utf-8"))

        qhc_path = os.path.realpath(os.path.join(temp_dir, "main.qhc"))

        try:
            qhc_generator = find_qhc_generator()
        except FileNotFoundError:
            raise click.FileError(
                "Can't find a QHC generator! You should have  qcollectiongenerator or qhelpgenerator in path."
            )

        system('%s "%s" -o "%s"' % (qhc_generator, qhcp_path, qhc_path))

        system('assistant -collectionFile "%s"' % qhc_path)


if __name__ == "__main__":
    main()

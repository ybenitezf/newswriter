"""Utilitarios para renderizar data de editorjs a diferentes formatos"""
from flask import render_template

BLOCK_TYPES = [
        'paragraph', 'delimiter', 'header', 'list', 'quote', 'warning',
        'image', 'linkTool']


def renderBlock(block, format='html'):
    if block.get('type') in BLOCK_TYPES:
        return render_template(
            "editorjs/{}.{}".format(
                block.get('type'), format),
            **block)
    else:
        render_template(
            "editorjs/default.{}".format(format), **block)

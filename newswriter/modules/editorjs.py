"""Utilitarios para renderizar data de editorjs a diferentes formatos"""
from flask import render_template, current_app

BLOCK_TYPES = [
        'paragraph', 'delimiter', 'header', 'list', 'quote', 'warning',
        'image', 'linkTool', 'photo', 'rawCode']


def renderBlock(block, format='html'):
    if block.get('type') in BLOCK_TYPES:
        current_app.logger.debug(f"Found template for {block.get('type')}")
        return render_template(
            "editorjs/{}.{}".format(
                block.get('type'), format),
            **block)
    else:
        current_app.logger.debug(f"Using default for {block.get('type')}")
        return render_template(
            "editorjs/default.{}".format(format), **block)

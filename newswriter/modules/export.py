from newswriter.models.content import Article, ImageModel
from newswriter.schemas import ArticleExportSchema, ImageModelExportSchema
from adelacommon.ziparchive import ZipArchive
from flask import current_app
from slugify import slugify
import tempfile
import json
import shutil
import os

def article_safe_name(article: Article) -> str:
    return f"{slugify(article.headline, max_length=10)}_{article.id[-4:]}"


def export_image(image: ImageModel) -> str:
    archive_name = os.path.join(
        tempfile.gettempdir(), f"{image.id}.zip")
    work_dir = tempfile.TemporaryDirectory()
    
    meta_file_name = os.path.join(
        work_dir.name, "META-INFO.json")
    with open(meta_file_name, 'w') as mf:
        json.dump(ImageModelExportSchema().dump(image), mf)
    src_name = os.path.join(
        current_app.config.get('UPLOAD_FOLDER'),  "images", image.filename)
    dst_name = os.path.join(work_dir.name, image.filename)
    shutil.copy(src_name, dst_name)

    # ponerlo todo en un el archivo zip
    zip = ZipArchive(archive_name, 'w')
    zip.addFile(dst_name, baseToRemove=work_dir.name)
    zip.addFile(meta_file_name, baseToRemove=work_dir.name)
    zip.close()

    work_dir.cleanup()
    return archive_name


def export_article(article: Article) -> str:
    ld = current_app.logger.debug
    archive_name = os.path.join(
        tempfile.gettempdir(), f"{article_safe_name(article)}.zip")
    work_dir = tempfile.TemporaryDirectory()
    assets = list()
    ld(f"Exporting {article.id} to {work_dir.name}")

    # buscar cada una de las imagenes y exportarlas
    to_export = ['image', 'photo', 'attaches']
    for block in article.getDecodedContent().get('blocks'):
        if block.get('type') == 'image':
            # zip image data
            block_data = block.get('data')
            img = ImageModel.query.get(block_data['file']['md5sum'])
            assets.append(shutil.move(export_image(img), work_dir.name))
        elif block.get('type') == 'linkTool':
            # linkTool tiene las imagenes adjuntas en otra parte
            block_data = block.get('data')
            if 'image' in block_data.get('meta'):
                img = ImageModel.query.get(
                    block_data['meta']['image']['md5sum'])
                assets.append(shutil.move(export_image(img), work_dir.name))
        elif block.get('type') == 'attaches':
            # agregar el adjunto al paquete
            src = os.path.join(
                current_app.config['UPLOAD_FOLDER'], 
                block.get('data').get('file').get('name'))
            assets.append(shutil.copy(src, work_dir.name))

    meta_file_name = os.path.join(
        work_dir.name, "META-INFO.json")
    with open(meta_file_name, 'w') as mf:
        json.dump(ArticleExportSchema().dump(article), mf)
    ld(f"Exporting metadata to {meta_file_name}")


    # crear el .zip
    ld(f"Adding files to {archive_name}")
    zip = ZipArchive(archive_name, "w")
    zip.addFile(meta_file_name, baseToRemove=work_dir.name)
    ld(f"Added {meta_file_name}")
    # agregar las imagenes
    for asset in assets:
        zip.addFile(asset, baseToRemove=work_dir.name)
        ld(f"Added {asset}")
    zip.close()

    work_dir.cleanup()
    ld(f"Cleanup completed")
    return archive_name

#!/usr/bin/env python

import argparse
import os

# flake8: noqa

"""
This scans a directory containing directories numbered according to the legacy id
of the articles. Each numbered directory contains files from the old site.

"""

def get_all_legacy_articles():
    articles = models.Article.objects.filter(
        legacy_id__isnull=False
    )
    return articles


def get_legacy_articles(legacy_ids=[]):
    articles = models.Article.objects.filter(
        legacy_id__in=legacy_ids
    )
    return articles


def get_filehandles(path, legacy_id):
    fullpath = os.path.join(path, legacy_id)
    if not os.path.exists(fullpath) or not os.path.isdir(fullpath):
        return []
    fnames =  os.listdir(fullpath)

    return fnames


def save_material(articles, path):
    print('handling articles')
    too_big = 1024**2
    for article in articles:
        legacy_id = str(article.legacy_id)
        print('handling legacy article %s, %s' % (legacy_id, article))

        fullpath = os.path.join(path, legacy_id)
        if not os.path.exists(fullpath) or not os.path.isdir(fullpath):
            print('    %s is not a valid directory' % fullpath)
            continue
        filenames = os.listdir(fullpath)
        print('    handling filenames', fullpath, filenames)

        for filename in filenames:
            filepath = os.path.join(fullpath, filename)
            filestat = os.stat(filepath)
            if filestat.st_size > too_big:
                print('    file %s is too big' % filepath)
                continue
            with open(filepath) as fh:
                print('    adding %s' % filename)
                supporting_material = article.supportingmaterial_set.create(
                    name=filename,
                    explanatory_text='supporting materials file',
                )
                supporting_material.archive_file.save(
                    filename,
                    ContentFile(fh.read()),
                )

    print('done handling articles')


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "companionpages.settings")
    from django.conf import settings
    from supportingmaterials import models
    from django.core.files.base import ContentFile

    parser = argparse.ArgumentParser(description="""
        For each article with a legacy id, this scans a directory that contains files from the old site,
        creates supplemental materials for each files, and adds these to the article record.
    """)

    parser.add_argument('legacy_ids', metavar='N', nargs='*',
        help='legacy ids. use to run against specific articles')
    parser.add_argument('--path', default='/home/sheila/Dropbox/RMC-DataCode/',
        help='path to directory of legacy file directories')
    args = parser.parse_args()
    if len(args.legacy_ids) > 0:
        print 'legacy_ids: ', args.legacy_ids
        articles = get_legacy_articles(args.legacy_ids)
    else:
        print 'all'
        articles = get_all_legacy_articles()
    save_material(articles, args.path)
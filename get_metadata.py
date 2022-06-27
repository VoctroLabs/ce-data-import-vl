import os.path
from pathlib import Path
import json

import click
from ceimport import logger
from ceimport.sites import cpdl

root = Path("~/voctro").expanduser()
path_files = root / "get-metadata/"


def import_cpdl_work_wikitext(work_wikitext):
    composition = cpdl.composition_wikitext_to_music_composition(work_wikitext)
    return composition


def import_cpdl_work(work_names):
    """Import a single work"""
    wikitext = cpdl.get_wikitext_for_titles(work_names)
    for work in wikitext:
        logger.info("Importing CPDL work %s", work['title'])
        composition = import_cpdl_work_wikitext(work)
    return composition


def cpdl_import_work(file, url):
    """Import the given work (--url x) or file of works (--file f).
    Works need to be wiki titles (no http://.... and no _ to split words."""
    if url:
        composition = import_cpdl_work([url])
    elif file:
        works = []
        with open(file, 'r') as fp:
            for work in fp:
                works.append(work.strip())
        composition = import_cpdl_work(works)
    else:
        click.echo("Need to provide --url or --file")
    return composition


url = "Requiem (Pierre de Manchicourt)"
f = None
compo = cpdl_import_work(f, url)
info = compo['work']
lan = info['inlanguage']
composer = compo['composer']
title_xml = os.path.basename(info['source'])
print(title_xml, lan,  composer)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def import_cpdl_works_for_category(cpdl_category):
    """Given a category in CPDL, find all of its works. Then, filter to only include works
    with a musicxml file. Import each of these works and the xml files.
    This assumes that import_cpdl_composers_for_category has been run first and that Person
    objects exist in the CE for each Composer"""

    titles = cpdl.get_titles_in_category(cpdl_category)
    wikitext = cpdl.get_wikitext_for_titles(titles)
    new_wikitext_dic = []
    for each_dic in wikitext:
        ret = cpdl.composition_wikitext_to_mediaobjects(each_dic)
        print(each_dic['title'])
        if ret:
            xml_info = ret[0]['xml']
            f_url = xml_info['contenturl']
            #  file_url = remove_suffix(os.path.basename(xml_info['contenturl']), '.mxl')
            each_dic['file_url'] = f_url
            new_wikitext_dic.append(each_dic)
        else:
            new_wikitext_dic.append(each_dic)

    xmlwikitext = cpdl.get_works_with_xml(new_wikitext_dic)
    new_xmlwikitext = []
    for dics in xmlwikitext:
        if len(dics) == 3:
            new_xmlwikitext.append(dics)

    total = len(new_xmlwikitext)
    all_compositions = []
    for i, work in enumerate(new_xmlwikitext, 1):
        logger.info("Importing CPDL work %s/%s %s", i, total, work['title'])
        file_url = work['file_url']
        composition = import_cpdl_work_wikitext(work)
        composition['file_url'] = file_url
        all_compositions.append(composition)
    return all_compositions


def write_in_json(compos):
    with open("output" + ".json", "w+") as json_file:
        info_json = json.dumps(compos, indent=2)
        json_file.write(info_json)
    return json_file


def create_whole_dic(compositions):
    for comp in compositions:
        compositions_catalan.append(comp)


compositions_catalan = import_cpdl_works_for_category("Works in Catalan")
compositions_spanish = import_cpdl_works_for_category("Works in Spanish")
compositions_german = import_cpdl_works_for_category("Works in German")
compositions_latin = import_cpdl_works_for_category("Works in Latin")
compositions_english = import_cpdl_works_for_category("Works in English")


create_whole_dic(compositions_spanish)
create_whole_dic(compositions_english)
create_whole_dic(compositions_german)
create_whole_dic(compositions_latin)

jf_all = write_in_json(compositions_catalan)



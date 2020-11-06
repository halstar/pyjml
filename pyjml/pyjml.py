#!/usr/bin/env python
# coding: utf-8

"""
Python-based tool to import Joomla articles from version 1.5 to 3.9.
"""

import os
import os.path
import shutil
import sys
import re
from optparse import OptionParser
from xml.etree import ElementTree

__all__ = []
__version__ = 1.0
__date__ = '2020-11-03'
__updated__ = '2020-11-03'
program_long_desc = 'This program helps and import Joomla articles from version 1.5 to 3.9'

# Default log level
LOG_LEVEL = 1

# Default limit in number of articles
LIMIT_COUNT = 1

# Required Python version
REQUIRED_PYTHON_VERSION = 3

# High level constants
SQL_TARGET_TABLE = 'fressin_content'

# Hard coded value to insert in SQL
SQL_EMPTY_STRING     = '\'\''
SQL_EMPTY_DATE       = '\'0000-00-00 00:00:00\''
SQL_ASSET_ID         = '0'
SQL_STATE            = '1'
SQL_CREATED_BY       = '372'
SQL_CREATED_BY_ALIAS = SQL_EMPTY_STRING
SQL_MODIFIED_BY      = '0'
SQL_CHECKED_OUT      = '0'
SQL_CHECKED_OUT_TIME = SQL_EMPTY_DATE
SQL_PUBLISH_DOWN     = SQL_EMPTY_DATE
SQL_IMAGES           = '\'{{\\"image_intro\\":\\"\\",\\"float_intro\\":\\"\\",\\"image_intro_alt\\":\\"\\",\\"image_intro_caption\\":\\"\\",\\"image_fulltext\\":\\"\\",\\"float_fulltext\\":\\"\\",\\"image_fulltext_alt\\":\\"\\",\\"image_fulltext_caption\\":\\"\\"}}\''
SQL_URLS             = '\'{{\\"urla\\":false,\\"urlatext\\":\\"\\",\\"targeta\\":\\"\\",\\"urlb\\":false,\\"urlbtext\\":\\"\\",\\"targetb\\":\\"\\",\\"urlc\\":false,\\"urlctext\\":\\"\\",\\"targetc\\":\\"\\"}}\''
SQL_ATTRIBS          = '\'{{\\"article_layout\\":\\"\\",\\"show_title\\":\\"\\",\\"link_titles\\":\\"\\",\\"show_tags\\":\\"\\",\\"show_intro\\":\\"\\",\\"info_block_position\\":\\"\\",\\"info_block_show_title\\":\\"\\",\\"show_category\\":\\"\\",\\"link_category\\":\\"\\",\\"show_parent_category\\":\\"\\",\\"link_parent_category\\":\\"\\",\\"show_associations\\":\\"\\",\\"show_author\\":\\"\\",\\"link_author\\":\\"\\",\\"show_create_date\\":\\"\\",\\"show_modify_date\\":\\"\\",\\"show_publish_date\\":\\"\\",\\"show_item_navigation\\":\\"\\",\\"show_icons\\":\\"\\",\\"show_print_icon\\":\\"\\",\\"show_email_icon\\":\\"\\",\\"show_vote\\":\\"\\",\\"show_hits\\":\\"\\",\\"show_noauth\\":\\"\\",\\"urls_position\\":\\"\\",\\"alternative_readmore\\":\\"\\",\\"article_page_title\\":\\"\\",\\"show_publishing_options\\":\\"\\",\\"show_article_options\\":\\"\\",\\"show_urls_images_backend\\":\\"\\",\\"show_urls_images_frontend\\":\\"\\"}}\''
SQL_VERSION          = '1'
SQL_ORDERING         = '0'
SQL_METAKEY          = SQL_EMPTY_STRING
SQL_METADESC         = SQL_EMPTY_STRING
SQL_ACCESS           = '1'
SQL_METADATA         = '\'{{\\"robots\\":\\"\\",\\"author\\":\\"\\",\\"rights\\":\\"\\",\\"xreference\\":\\"\\"}}\''
SQL_FEATURED         = '0'
SQL_LANGUAGE         = '\'*\''
SQL_XREFERENCE       = SQL_EMPTY_STRING
SQL_NOTE             = SQL_EMPTY_STRING

#  Problematic characters substitution table
CHARACTERS_TABLE = [
    ('\u200b', ''   ),
    ('\u2032', '\'' ),
    ('\u2033', '"'  ),
    ('\u2192', '=>' ),
    ('"'     , '\\"'),
    ('\''    , '\\\'')
]

#  Problematic strings substitution table
STRINGS_TABLE = [
    ('/images/articles'                       , 'images/archives'                                                            ),
    ('images/articles'                        , 'images/archives'                                                            ),
    ('images/partenaires/privilegies'         , 'images/archives/partenaires'                                                ),
    ('images/partenaires/2010'                , 'images/archives/partenaires'                                                ),
    ('images/manifestations/foulees/2010'     , 'images/archives/foulees'                                                    ),
    ('images/manifestations/foulees'          , 'images/archives/foulees'                                                    ),
    ('images/manifestations/sponsors'         , 'images/archives/sponsors'                                                   ),
    ('style=\"float: left;\"'                 , ''                                                                           ),
    ('style=\"float: right;\"'                , ''                                                                           ),
    ('style=\"border: 1px solid black;\"'     , ''                                                                           ),
    ('<img '                                  , '<img class=\"pull-center\" style=\"margin-bottom: 6px; margin-top: 3px\" '  ),
    ('<p> </p>'                               , ''                                                                           ),
    ('<p> </p>'                               , ''                                                                           ),
    ('<p style=\"margin: 0cm 0cm 0pt;\"> </p>', ''                                                                           ),
    ('<table border=\"0\">'                   , '<table>'                                                                    ),
    ('<table><tr><td><p><center><img '        , '<table><tr><td width=\"50%\" style=\"padding-right:10px;\"><p><center><img '),
    ('</td><td><p><img '                      , '</td><td width=\"50%\" style=\"padding-left:10px;\"><p><img '               ),
]

# Old to new categories conversion table
CATEGORIES_CONVERSION_TABLE = {
    37: 50,  # Art, culture, histoire
    38: 51,  # Cartes postales
    39: 52,  # Environnement
    40: 53,  # Evénements
    41: 54,  # Histoire de Fressin
    42: 57,  # Personnalités locales
    43: 60,  # Rions un peu!
    44: 49,  # Journal de la semaine
    45: 55,  # La vie du canton
    46: 56,  # La vie économique
    47: 58,  # Points de vue
    48: 61,  # Sports
    49: 62,  # Tourisme
    50: 63,  # Vie associative
    51: 59,  # Reconnaissez-vous?
    84: 64,  # Nécrologies
    89: 66,  # Foulées Fressinoises
}

# Categories to ignore
CATEGORIES_IGNORE_LIST = { 34, 52, 53, 55, 60, 61, 62, 63, 64, 78, 90, 91, 92, 93, 94, 95, 96, 97, 98 }


# SQL insertion command and values strings
SQL_INSERT_COMMAND = 'INSERT INTO `' + SQL_TARGET_TABLE + '` (`asset_id`, `title`, `alias`, `introtext`, `fulltext`, `state`, `catid`, `created`, `created_by`, `created_by_alias`, `modified`, `modified_by`, `checked_out`, `checked_out_time`, `publish_up`, `publish_down`, `images`, `urls`, `attribs`, `version`, `ordering`, `metakey`, `metadesc`, `access`, `hits`, `metadata`, `featured`, `language`, `xreference`, `note`) VALUES'
SQL_INSERT_VALUES = '(' + SQL_ASSET_ID + ', \'{}\', \'{}\', \'{}\', \'{}\', ' + SQL_STATE + ', {}, \'{}\', ' + SQL_CREATED_BY + ', ' + SQL_CREATED_BY_ALIAS + ', \'{}\', ' + SQL_MODIFIED_BY + ', ' + SQL_CHECKED_OUT + ', ' + SQL_CHECKED_OUT_TIME + ', \'{}\', ' + SQL_PUBLISH_DOWN + ', ' + SQL_IMAGES + ', ' + SQL_URLS + ', ' + SQL_ATTRIBS + ', ' + SQL_VERSION + ', ' + SQL_ORDERING + ', ' + SQL_METAKEY + ', ' + SQL_METADESC + ', ' + SQL_ACCESS + ', {}, ' + SQL_METADATA + ', ' + SQL_FEATURED + ', ' + SQL_LANGUAGE + ', ' + SQL_XREFERENCE + ', ' + SQL_NOTE + ')'

# Just show log message on STDERR, if log level is enough
def log(level, message):

    if LOG_LEVEL >= level:
        sys.stdout.flush()
        sys.stdout.write(message + '\n')
        sys.stdout.flush()


def convert_xml_to_sql(xml_input, img_dir, sql_output):

    global LIMIT_COUNT

    counter_read    = 0
    counter_write   = 0
    not_found_count = 0

    log(0, '\nStarting conversion...\n')

    with open(xml_input, 'r',  encoding='utf8') as file_in:
        tree = ElementTree.parse(file_in)

    with open(sql_output, 'w',  encoding='utf8') as file_out:

        articles = tree.findall('.//table')
        log(0, 'Found {} articles'.format(len(articles)))

        for article in articles:

            title      = article.find('column[@name="title"]'    ).text
            alias      = article.find('column[@name="alias"]'    ).text
            intro_text = article.find('column[@name="introtext"]').text
            full_text  = article.find('column[@name="fulltext"]' ).text
            category   = article.find('column[@name="catid"]'    ).text
            date       = article.find('column[@name="created"]'  ).text
            hits       = article.find('column[@name="hits"]'     ).text
            log(1, '#{:04}: {} - {}'.format(counter_read, alias, title))
            log(2, 'Cat. : {} - Date: {} - Hits: {}'.format(category, date, hits))
            log(3, 'intro_text: {}'.format(intro_text))
            log(3, 'full_text : {}'.format(full_text ))

            category_int = int(category)

            if category_int in CATEGORIES_IGNORE_LIST:
                insert_article = False
            elif category_int not in CATEGORIES_CONVERSION_TABLE:
                log(0, 'WARNING: category #{} not found; Cf. article "{}"'.format(category, title))
                insert_article = False
            else:
                new_category   = CATEGORIES_CONVERSION_TABLE[category_int]
                insert_article = True

            if insert_article:

                if intro_text is None:
                    intro_text = ''

                if full_text is None:
                    full_text = ''

                # Update like images paths in texts
                for string in STRINGS_TABLE:
                    intro_text = intro_text.replace(string[0], string[1])
                    full_text  = full_text.replace(string[0], string[1])

                matches = re.findall(r'src="(.*?)"', intro_text)

                if matches:
                    for match in matches:
                        img_path = img_dir + '/' + match
                        if not os.path.isfile(img_path):
                            log(0, 'WARNING: ' + img_path + ' not found in article "{}"'.format(title))
                            not_found_count += 1

                matches = re.findall(r'src="(.*?)"', full_text)

                if matches:
                    for match in matches:
                        img_path = img_dir + '/' + match
                        if not os.path.isfile(img_path):
                            log(0, 'WARNING: ' + img_path + ' not found in article "{}"'.format(title))
                            not_found_count += 1

                # Cleanup title & texts from problematic characters
                for character in CHARACTERS_TABLE:
                    title      = title.replace     (character[0], character[1])
                    intro_text = intro_text.replace(character[0], character[1])
                    full_text  = full_text.replace(character[0], character[1])

                if counter_write % 10 == 0:
                    file_out.write(SQL_INSERT_COMMAND + '\n')

                file_out.write(SQL_INSERT_VALUES.format(title, alias, intro_text, full_text, new_category, date, date, date, hits))

                counter_write += 1

                if counter_write % 10 == 0:
                    file_out.write(';\n')
                else:
                    file_out.write(',\n')

            counter_read += 1

            if counter_read == LIMIT_COUNT:
                break

        if counter_write != 0:
            file_out.seek(0, os.SEEK_END)
            file_out.seek(file_out.tell() - 3, os.SEEK_SET)
            file_out.truncate()
            file_out.write(';\n')

    log(0, '\nRead/wrote {}/{} articles'.format(counter_read, counter_write))
    log(0, '\nMissing {} images'.format(not_found_count))
    log(0, '\nConversion done OK!...')

    return 0


def main(argv=None):

    global LOG_LEVEL, LIMIT_COUNT
    program_name = os.path.basename(sys.argv[0])
    program_version = 'v%1.1f' % __version__
    program_build_date = '%s' % __updated__
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_usage = 'usage: %prog [-h] [--verbose=INT] [--limit=INT] --input-xml-file=STRING --input-img-dir=STRING --output-sql-file=STRING\n'

    # Check python version is the minimum expected one
    if sys.version_info[0] < REQUIRED_PYTHON_VERSION:
        log(0, 'ERROR: this tool requires at least Python version ' + str(REQUIRED_PYTHON_VERSION))
        sys.exit(2)

    # Setup options
    if argv is None:
        argv = sys.argv[1:]

    try:
        # Setup options parser
        parser = OptionParser(usage=program_usage,
                              version=program_version_string,
                              epilog=program_long_desc)
        parser.add_option('-v',
                          '--verbose',
                          action='store',
                          dest='verbose',
                          help='Set verbose level [default: %default]',
                          metavar='INT')
        parser.add_option('-l',
                          '--limit',
                          action='store',
                          dest='limit',
                          help='Set limit number of articles to deal with [default: %default]',
                          metavar='INT')
        parser.add_option('-x',
                          '--input-xml-file',
                          action='store',
                          dest='xml_input',
                          help='Input file including Joomla articles content in XML format',
                          metavar='STRING')
        parser.add_option('-i',
                          '--input-img-dir',
                          action='store',
                          dest='img_dir',
                          help='Input directory including articles\' images',
                          metavar='STRING')
        parser.add_option('-s',
                          '--output-sql-file',
                          action='store',
                          dest='sql_output',
                          help='Output file including Joomla articles content in SQL format',
                          metavar='STRING')

        # Set defaults
        parser.set_defaults(verbose=str(LOG_LEVEL), limit=LIMIT_COUNT)

        # Process options
        (opts, args) = parser.parse_args(argv)

        LOG_LEVEL = int(opts.verbose)
        log(2, 'Log verbosity level  = %s' % opts.verbose)

        LIMIT_COUNT = int(opts.limit)
        log(2, 'Articles limit count = %s' % opts.limit)

        # Check the options
        if not opts.xml_input:
            log(0, 'ERROR: missing input XML file. Try --help')
            return 2

        if not opts.img_dir:
            log(0, 'ERROR: missing input images directory. Try --help')
            return 2

        if not opts.sql_output:
            log(0, 'ERROR: missing output SQL file. Try --help')
            return 2

        if not os.path.isfile(opts.xml_input):
            log(0, 'ERROR: ' + opts.xml_input + ' file not found')
            return 2

        if not os.path.isdir(opts.img_dir):
            log(0, 'ERROR: ' + opts.img_dir + ' directory not found')
            return 2

        if not os.path.isfile(opts.sql_output):
            log(0, 'ERROR: ' + opts.sql_output + ' file not found')
            return 2

    except Exception as error:
        indent = len(program_name) * ' '
        sys.stderr.write(program_name + ': ' + repr(error) + '\n')
        sys.stderr.write(indent + ' for help use --help\n')
        return 2

    return convert_xml_to_sql(opts.xml_input, opts.img_dir, opts.sql_output)


# Module run in main mode
if __name__ == '__main__':
    sys.exit(main())

# Prepare the notebook for publication
from IPython.nbconvert import HTMLExporter
import json
import os
import warnings


DEFAULT_THUMBNAIL_URL = '/images/static-image'


def publish(notebook_name, url_path, page_title, page_description,
            ignore_last_n_cells=2, uses_plotly_offline=False,
            thumbnail_url=DEFAULT_THUMBNAIL_URL,
            language='python', **kwargs):
    '''
    Convert an IPython notebook into an HTML file that can be consumed
    by GitHub pages in plotly's documentation repo.

    Arguments:
    - notebook_name: The name of the notebook to convert.
                     Used as input arg to nbconvert, nowhere else.
    - url_path: e.g. /python/offline
    - page_title: The <title> of the page.
    - page_description: So, what's this page about?
                        Sell it in 160 characters or less.
                        This is the <meta name="description"> tag.
    - ignore_last_n_cells: When converting to HTML, don't convert the
                           ignore_last_n_cells number of cells.
                           This is usually the cell that runs this `publish`
                           command and the blank output cell that is always
                           included.
    - uses_plotly_offline: If this was created with plotly.offline, then set
                           this to True. This will include an extra lib
                           (jquery) that is included in ipython notebook,
                           but not included in gh-pages
    - thumbnail_url: Used as a thumbnail image on the notebook splash
                     (if applicable) and as the image when sharing the
                     notebook as a tweet, a facebook post, etc.
                     Can be relative to the repo, eg '/images/static-image'
                     or absolute, e.g. http://i.imgur.com/j0Uiy0n.jpg
    - language: Not sure what this is used for.

    Example:
    publish('Plotly Offline',
            '/python/offline',
            'Plotly Offline for IPython Notebooks',
            'How to use Plotly offline inside IPython notebooks with Plotly Offline',
             uses_plotly_offline=True)
    '''
    warnings.warn('Did you "Save" this notebook before running this command? '
                  'Remember to save, always save.')

    parts = url_path.split('/')
    if len(parts) > 3:
        warnings.warn('Your URL has more than 2 parts... are you sure?')
    if url_path[-1] == '/':
        url_path = url_path[:-1]
    if len(page_description) > 160:
        raise Exception("Shorten up that page_description! "
                        "Your description was {} characters, "
                        "and it's gotta be <= than 160."
                        .format(len(page_description)))

    if thumbnail_url == DEFAULT_THUMBNAIL_URL:
        has_thumbnail = 'false'
    else:
        has_thumbnail = 'true'

    if '.ipynb' not in notebook_name:
        notebook_name += '.ipynb'
    fn = notebook_name
    tmpfn = 'temp-{}'.format(fn)
    nbjson = json.load(open(fn))
    if 'cells' in nbjson:
        nbjson['cells'] = nbjson['cells'][:-ignore_last_n_cells]
    elif 'worksheets' in nbjson:
        if len(nbjson['worksheets']) != 1:
            raise Exception('multiple worksheets?')
        elif 'cells' in nbjson['worksheets'][0]:
            nbjson['worksheets'][0]['cells'] = nbjson['worksheets'][0]['cells'][:-ignore_last_n_cells]
        else:
            raise Exception('cells not in worksheets[0]?')
    else:
        raise Exception('unknown ipython notebook format')
    with open(tmpfn, 'w') as f:
        f.write(json.dumps(nbjson))

    exporter = HTMLExporter(template_file='basic')
    html = exporter.from_filename(tmpfn)[0]

    kwargs.setdefault('layout', 'user-guide')
    kwargs.setdefault('page_type', 'u-guide')
    kwargs.setdefault('language', 'python')

    with open('2015-06-30-' + fn.replace('.ipynb', '.html'), 'w') as f:
        f.write('\n'.join([''
                           '---',
                           'permalink: ' + url_path,
                           'description: ' + page_description.replace(':', '&#58;'),
                           'name: ' + page_title.replace(':', '&#58;'),
                           'has_thumbnail: ' + has_thumbnail,
                           'thumbnail: ' + thumbnail_url,
                           '\n'.join(['{}: {}'.format(k, v) for k, v in kwargs.iteritems()]),
                           '---',
                           '{% raw %}'
                           ]))
        if uses_plotly_offline:
            f.write(
                '<script type="text/javascript" '
                '        src="https://code.jquery.com/jquery-2.1.4.min.js">'
                '</script>'
            )
        f.write(html.encode('utf8'))
        f.write('{% endraw %}')
    os.remove(tmpfn)

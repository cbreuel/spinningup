"""Render LaTeX ``algorithm``/``algorithmic`` pseudocode blocks as HTML.

The algorithm pages write their pseudocode as LaTeX, using the ``algorithm``
and ``algorithmic`` packages, inside ``.. math:: :nowrap:`` blocks. That
worked when the docs rendered math with ``sphinx.ext.imgmath``, which ran a
real LaTeX installation, but MathJax knows nothing about those environments
and renders the whole block as ``Unknown environment 'algorithm'``.

This extension translates those blocks into HTML for HTML builders. Other
builders (notably LaTeX/PDF) see the blocks unchanged, so the preamble in
conf.py still typesets them the way it always did.

Only the subset of ``algorithmic`` the docs actually use is supported --
\\STATE, \\FOR, \\IF, \\REPEAT and friends, plus displayed equations nested
inside a line. Anything unrecognized is passed through as literal text
rather than silently dropped.
"""

import re
from html import escape

from docutils import nodes

__version__ = '1.0'

# A line of pseudocode starts at one of these commands and runs until the
# next one, so they're what the body gets split on.
CONTROL_RE = re.compile(
    r'\\(STATE|FOR|ENDFOR|IF|ELSIF|ELSE|ENDIF|WHILE|ENDWHILE'
    r'|REPEAT|UNTIL|LOOP|ENDLOOP|RETURN|REQUIRE|ENSURE)(?![A-Za-z])'
)

# Commands that take a condition/loop argument in braces.
TAKES_ARG = {'FOR', 'IF', 'ELSIF', 'WHILE', 'UNTIL'}

# How each command opens a line, and what it does to the indent level. The
# first number is applied before the line is emitted, the second after.
KEYWORDS = {
    'STATE': ('', '', 0, 0),
    'FOR': ('for', 'do', 0, 1),
    'ENDFOR': ('end for', '', -1, 0),
    'WHILE': ('while', 'do', 0, 1),
    'ENDWHILE': ('end while', '', -1, 0),
    'IF': ('if', 'then', 0, 1),
    'ELSIF': ('else if', 'then', -1, 1),
    'ELSE': ('else', '', -1, 1),
    'ENDIF': ('end if', '', -1, 0),
    'REPEAT': ('repeat', '', 0, 1),
    'UNTIL': ('until', '', -1, 0),
    'LOOP': ('loop', '', 0, 1),
    'ENDLOOP': ('end loop', '', -1, 0),
    'RETURN': ('return', '', 0, 0),
    'REQUIRE': ('require:', '', 0, 0),
    'ENSURE': ('ensure:', '', 0, 0),
}

ALGORITHM_RE = re.compile(r'\\begin\s*\{algorithm\}')
CAPTION_RE = re.compile(r'\\caption\s*\{')
ALGORITHMIC_RE = re.compile(
    r'\\begin\s*\{algorithmic\}(?:\[[^\]]*\])?(.*)\\end\s*\{algorithmic\}',
    re.DOTALL,
)
# Displayed equations nested inside a pseudocode line.
DISPLAY_RE = re.compile(
    r'\\begin\{(equation\*?|align\*?|gather\*?|aligned)\}(.*?)\\end\{\1\}',
    re.DOTALL,
)
TEXTTT_RE = re.compile(r'\\texttt\s*\{([^{}]*)\}')
INLINE_MATH_RE = re.compile(r'\$(.+?)\$', re.DOTALL)
MAX_INDENT = 6


def _match_brace(text, start):
    """Return (contents, index just past the closing brace) for text[start] == '{'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{' and (i == start or text[i - 1] != '\\'):
            depth += 1
        elif text[i] == '}' and text[i - 1] != '\\':
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    # Unbalanced: treat the rest of the block as the argument.
    return text[start + 1:], len(text)


def _render_text(text):
    """Turn one line's LaTeX text into HTML, with math handed to MathJax."""
    out = []
    pos = 0
    for match in DISPLAY_RE.finditer(text):
        out.append(_render_prose(text[pos:match.start()]))
        env, body = match.group(1), match.group(2).strip()
        if env.startswith('align') or env == 'aligned':
            # align* is only legal at the top level; aligned is the same
            # layout in a form MathJax accepts inside \[ ... \].
            body = '\\begin{aligned}%s\\end{aligned}' % body
        out.append(
            '<div class="pseudocode-math">\\[%s\\]</div>' % escape(body)
        )
        pos = match.end()
    out.append(_render_prose(text[pos:]))
    return ''.join(part for part in out if part)


def _render_prose(text):
    """Escape a run of text mode LaTeX and convert its inline math."""
    text = ' '.join(text.split())
    if not text:
        return ''
    text = escape(text, quote=False)
    text = INLINE_MATH_RE.sub(lambda m: '\\(%s\\)' % m.group(1), text)
    text = TEXTTT_RE.sub(
        lambda m: '<code>%s</code>' % m.group(1).replace('\\_', '_'), text
    )
    return text


def _parse(source):
    """Parse one algorithm block into (caption, [(indent, html), ...])."""
    caption = ''
    caption_match = CAPTION_RE.search(source)
    if caption_match:
        caption = _render_text(
            _match_brace(source, caption_match.end() - 1)[0]
        )

    body_match = ALGORITHMIC_RE.search(source)
    if not body_match:
        return caption, []
    body = body_match.group(1)

    controls = list(CONTROL_RE.finditer(body))
    lines = []
    indent = 0
    for i, control in enumerate(controls):
        command = control.group(1)
        keyword, trailer, before, after = KEYWORDS[command]
        end = controls[i + 1].start() if i + 1 < len(controls) else len(body)

        rest = body[control.end():end]
        argument = ''
        if command in TAKES_ARG:
            stripped = rest.lstrip()
            if stripped.startswith('{'):
                offset = len(rest) - len(stripped)
                argument, consumed = _match_brace(rest, offset)
                rest = rest[consumed:]

        parts = []
        if keyword:
            parts.append('<b>%s</b>' % keyword)
        if argument:
            parts.append(_render_text(argument))
        if trailer:
            parts.append('<b>%s</b>' % trailer)
        rendered = _render_text(rest)
        if rendered:
            parts.append(rendered)

        indent = max(0, min(MAX_INDENT, indent + before))
        lines.append((indent, ' '.join(parts)))
        indent = max(0, min(MAX_INDENT, indent + after))

    return caption, lines


def _to_html(source, number):
    caption, lines = _parse(source)
    if not lines:
        return None

    title = 'Algorithm %d' % number
    if caption:
        title += ' %s' % caption
    html = [
        '<div class="pseudocode">',
        '<div class="pseudocode-title">%s</div>' % title,
        '<ol class="pseudocode-lines">',
    ]
    for indent, line in lines:
        html.append(
            '<li><div class="pseudocode-line pseudocode-indent-%d">%s</div></li>'
            % (indent, line)
        )
    html.append('</ol>')
    html.append('</div>')
    return '\n'.join(html)


def convert_algorithm_blocks(app, doctree, docname):
    if app.builder.format != 'html':
        return

    number = 0
    for node in list(doctree.findall(nodes.math_block)):
        source = node.astext()
        if not ALGORITHM_RE.search(source):
            continue
        number += 1
        html = _to_html(source, number)
        if html is None:
            continue
        node.replace_self(nodes.raw('', html, format='html'))


def setup(app):
    app.connect('doctree-resolved', convert_algorithm_blocks)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

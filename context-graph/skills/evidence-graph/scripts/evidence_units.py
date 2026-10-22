"""Bounded read-only evidence units from a verified project snapshot.

Preserve table rows and paragraphs, not independent matching cells. This is
retrieval, never canonical acceptance or proof that an omitted fact is absent.
"""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path


class _Units(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.units, self.heading = [], ''
        self.active, self.parts, self.line = None, [], 0
        self.depth, self.dropped = 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'noscript'}:
            self.dropped += 1
        if self.dropped:
            return
        if self.active:
            if tag == self.active:
                self.depth += 1
            if tag in {'td', 'th', 'br', 'p', 'li'}:
                self.parts.append(' | ' if tag in {'td', 'th'} else ' ')
            return
        if tag in {'p', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.active, self.parts, self.line, self.depth = tag, [], self.getpos()[0], 1

    def handle_data(self, data):
        if self.active and not self.dropped:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript'}:
            self.dropped = max(0, self.dropped - 1)
            return
        if self.dropped or tag != self.active:
            return
        self.depth -= 1
        if self.depth:
            return
        text = ' '.join(''.join(self.parts).split()).strip(' |')
        if tag.startswith('h'):
            self.heading = text
        elif text:
            self.units.append({'label': text, 'source_location': self.line,
                               'source_end': self.getpos()[0], 'heading': self.heading})
        self.active, self.parts = None, []


def retrieve_units(graph, question, budget, asked_words, match_count, authorize_source=None):
    """No cache or writes. Every source is authorized and digest-replayed before parsing."""
    words = asked_words(question)
    sources = {n.get('source_file') for n in graph['nodes'] if n.get('source_file')}
    hashes = {r['path']: r['sha256'] for r in graph['source_snapshot']['files']}
    titles = {}
    for n in graph['nodes']:
        if n.get('kind') == 'document':
            titles[n.get('source_file')] = n.get('label', '')
    candidates = []
    for source in sorted(sources):
        if authorize_source is not None and not authorize_source(source):
            continue
        raw = Path(source).read_bytes()
        if hashlib.sha256(raw).hexdigest() != hashes[source]:
            raise ValueError('source_changed_during_query')
        if Path(source).suffix.lower() in {'.html', '.htm'}:
            parser = _Units(); parser.feed(raw.decode('utf-8')); parser.close()
            units = parser.units
        else:
            # Keep existing Markdown statements and their replayable locations.
            units = [{'label': n['label'], 'source_location': n['source_location'],
                      'source_end': n['source_location'], 'heading': ''}
                     for n in graph['nodes'] if n.get('source_file') == source
                     and n.get('kind') == 'statement' and n.get('source_location')]
        title = titles.get(source, '') + ' ' + Path(source).stem.replace('-', ' ').replace('_', ' ')
        scope = match_count(title, words)
        for ordinal, unit in enumerate(units):
            direct = match_count(unit['label'], words)
            heading = match_count(unit['heading'], words)
            if not direct and not scope and not heading:
                continue
            # A source/title match makes otherwise unlabelled values eligible;
            # all statements compete globally, so contradictory sources survive.
            score = 3 * direct + 2 * scope + heading
            hit = {**unit, 'source_file': source, 'source_sha256': hashes[source]}
            candidates.append((-score, -direct, len(unit['label']), source,
                               unit['source_location'], ordinal, hit))
    candidates.sort(key=lambda row: row[:-1])
    hits, omitted = [], 0
    for *_, hit in candidates:
        if len(json.dumps(hits + [hit], ensure_ascii=False).encode('utf-8')) > budget:
            omitted += 1
        else:
            hits.append(hit)
    return {'retrieval': 'evidence_units_read_only', 'hits': hits,
            'candidate_units': len(candidates), 'omitted_units': omitted,
            'partial': bool(omitted), 'evidence_status': 'source_verified_not_canonical_acceptance',
            'absence_proven': False}

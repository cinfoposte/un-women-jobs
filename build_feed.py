#!/usr/bin/env python3
"""Convert UN Women's official RSS 1.0 feed into an ARCA-friendly filtered RSS 2.0 feed.
Only current international Professional/Director P- and D-grade staff vacancies are included.
No third-party packages required.
"""
import argparse
import datetime as dt
import email.utils
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE_URL = 'https://jobs.undp.org/rss_feeds/UNWomen.xml'
OUTFILE = 'unwomen_jobs.xml'
RSS1 = '{http://purl.org/rss/1.0/}'
DC = '{http://purl.org/dc/elements/1.1/}'
JOBS = '{https://jobs.undp.org/rss_feed/spec/}'
GRADE = re.compile(r'^(?:P[- ]?[1-6]|D[- ]?[1-2])$', re.IGNORECASE)


def get_text(node, field):
    element = node.find(field)
    return ''.join(element.itertext()).strip() if element is not None else ''


def load_xml(source_file=None):
    if source_file:
        return Path(source_file).read_bytes()
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0 (compatible; cinfoPoste-RSS/1.0)', 'Accept': 'application/xml, application/rss+xml, */*'})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def create_feed(source_xml):
    root = ET.fromstring(source_xml)
    source_items = root.findall(f'{RSS1}item')
    if not source_items:
        raise RuntimeError('The official feed contains no RSS 1.0 item elements; refusing to overwrite existing output.')

    now = dt.datetime.now(dt.timezone.utc)
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'UN Women – International Professional and Director Vacancies'
    ET.SubElement(channel, 'link').text = SOURCE_URL
    ET.SubElement(channel, 'description').text = 'Current international P- and D-grade staff vacancies from the official UN Women RSS feed. Automatically updated by cinfo.'
    ET.SubElement(channel, 'language').text = 'en'
    ET.SubElement(channel, 'lastBuildDate').text = email.utils.format_datetime(now)

    seen = set()
    accepted = 0
    for item in source_items:
        grade = get_text(item, f'{JOBS}post_level').upper().replace(' ', '').replace('-', '')
        if not GRADE.fullmatch(grade):
            continue

        recruiting_type = get_text(item, f'{JOBS}recruiting_type')
        if recruiting_type and re.search(r'\b(?:local|national|consultant|consultancy|consulting)\b', recruiting_type, re.IGNORECASE):
            continue

        deadline = get_text(item, f'{JOBS}job_deadline_d')
        if deadline:
            try:
                due = dt.datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                if due.tzinfo is None:
                    due = due.replace(tzinfo=dt.timezone.utc)
                if due < now:
                    continue
            except ValueError:
                # Keep the job if its deadline cannot be parsed, but show the raw date.
                pass

        link = get_text(item, f'{RSS1}link') or item.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
        title = get_text(item, f'{RSS1}title')
        if not title or not link or link in seen:
            continue
        seen.add(link)

        job = ET.SubElement(channel, 'item')
        ET.SubElement(job, 'title').text = title
        ET.SubElement(job, 'link').text = link
        metadata = [f'Grade: {grade}']
        station = get_text(item, f'{JOBS}duty_station')
        if station:
            metadata.append(f'Duty station: {station}')
        if deadline:
            metadata.append(f'Application deadline: {deadline[:10]}')
        if recruiting_type:
            metadata.append(f'Contract type: {recruiting_type}')
        function = get_text(item, f'{JOBS}job_function')
        if function:
            metadata.append(f'Job function: {function}')
        ET.SubElement(job, 'description').text = ' | '.join(metadata) + ' | Full vacancy: ' + link
        ET.SubElement(job, 'guid', {'isPermaLink': 'true'}).text = link
        posted = get_text(item, f'{DC}date')
        if posted:
            try:
                posted_dt = dt.datetime.fromisoformat(posted.replace('Z', '+00:00'))
                if posted_dt.tzinfo is None:
                    posted_dt = posted_dt.replace(tzinfo=dt.timezone.utc)
                ET.SubElement(job, 'pubDate').text = email.utils.format_datetime(posted_dt)
            except ValueError:
                pass
        accepted += 1

    ET.indent(rss, space='  ')
    return ET.tostring(rss, encoding='utf-8', xml_declaration=True), len(source_items), accepted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', help='Optional local source XML for testing, instead of downloading live feed')
    parser.add_argument('--output', default=OUTFILE)
    args = parser.parse_args()
    result, total, kept = create_feed(load_xml(args.source_file))
    Path(args.output).write_bytes(result)
    print(f'Processed {total} official UN Women jobs; included {kept} current international P/D staff vacancies → {args.output}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
import json


def kwic(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q['format'] == "json":
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
        kwic_results = fetch_kwic(hits, path, q, f.link.byte_query, db, start-1, end, length=250)
        formatted_results = [{"citation": i[0],
                              "text": i[1]} for i in kwic_results]
        return json.dumps(formatted_results)
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_kwic(hits, db, dbname, q, path, config)
        
def render_kwic(hits, db, dbname, q, path, config):
    biblio_criteria = f.biblio_criteria(q, config)
    return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                path=path, results_per_page=q['results_per_page'], biblio_criteria=biblio_criteria,
                                config=config, template_name='kwic.mako', report="kwic")

def fetch_kwic(results, path, q, byte_query, db, start, end, length=5000):
    kwic_results = []
    shortest_biblio = 0

    for hit in results[start:end]:
        author = hit.doc.author
        if author:
            short_author = author
            if len(author) > 15:
                short_author = short_author[:15] + '&#8230;'
        title = hit.doc.title
        if title:
            short_title = title
            if len(title) > 12:
                short_title = short_title[:12] + '&#8230;'
        biblio = short_author + ' ' +  short_title
        
        get_query = byte_query(hit.bytes)
        href = "./" + '/'.join([str(i) for i in hit.philo_id[:2]]) + get_query
        
        ## Find shortest bibliography entry
        if shortest_biblio == 0:
            shortest_biblio = len(biblio)
        if len(biblio) < shortest_biblio:
            shortest_biblio = len(biblio)
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = length/2 + byte_distance + length/2
            
        ## Get concordance and align it
        bytes, byte_start = adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))
        kwic_results.append(((author, short_author), (title, short_title), href, conc_text, hit))
        
    if shortest_biblio < 20:
        shortest_biblio = 20
    elif shortest_biblio > 30:
        shortest_biblio = 30
    
    ## Reset variables to avoid collisions
    author = ""
    title = ""
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        author, title, href, text, hit = result
        short_biblio = author[1] + ' ' + title[1]
        biblio = author[0] + ', ' +  title[0]
        if len(biblio) < 20:
            diff = 20 - len(biblio)
            biblio += ' ' * diff
        short_biblio = '<span class="short_biblio" style="white-space:pre-wrap;">%s</span>' % short_biblio[:shortest_biblio]
        full_biblio = '<span class="full_biblio" style="display:none;">%s</span>' % biblio
        kwic_biblio = full_biblio + short_biblio
        if q['format'] == "json":
            kwic_results[pos] = (kwic_biblio, text)
        else:
            kwic_biblio_link = '<a href="%s" class="kwic_biblio" style="white-space:pre-wrap;">' % href + kwic_biblio + '</a>: '
            kwic_results[pos] = kwic_biblio_link + '<span>%s</span>' % text
    return kwic_results


def KWIC_formatter(output, hit_num, chars=40):
    output = output.replace('\n', ' ')
    output = output.replace('\r', '')
    output = output.replace('\t', ' ')
    output = re.sub(' {2,}', ' ', output)
    output = convert_entities(output)
    start_hit = output.index('<span class="highlight">')
    end_hit = output.rindex('</span>') + 7
    tag_length = 7 * hit_num
    start_output = output[start_hit - chars:start_hit]
    start_output = re.sub('^[^ ]+? ', ' ', start_output, 1) # Do we want to keep this?
    if len(start_output) < chars:
        white_space = ' ' * (chars - len(start_output))
        start_output = white_space + start_output
    start_output = '<span style="white-space:pre-wrap;">' + start_output + '</span>'
    end_output = re.sub('[^ ]+\Z', ' ', output[end_hit:], 1)
    match = output[start_hit:end_hit]
    return start_output + match + end_output[:chars+tag_length]

#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import json
import sqlite3
sys.path.append('..')
import functions as f
from functions.ObjectFormatter import adjust_bytes
#from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler

def lookup_word_service(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    cursor = db.dbh.cursor()

    if request.report == "concordance":
        hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
        context_size = config['concordance_length'] * 3
        hit = hits[int(request.position)]
        bytes = hit.bytes
        hit_span = hit.bytes[-1] - hit.bytes[0]
        length = context_size + hit_span + context_size
        bytes, byte_start = adjust_bytes(bytes, length)
        byte_end = byte_start + length    
        filename = hit.filename
        token = request.selected
    elif request.report == "navigation":
        print >> sys.stderr, "WORD LOOKUP FROM NAVIGATION", request
    else:
        pass
    print >> sys.stderr, "TOKEN", token, "BYTES: ", byte_start, byte_end, "FILENAME: ", filename, "POSITION", request.position
    token_n = 0
    yield lookup_word(db,cursor, token, token_n, byte_start, byte_end, filename)

def lookup_word(db,cursor,token,n,start,end,filename):
    i = 0
    query = "select * from words where (byte_start >= ?) and (byte_end <= ?) and (filename = ?);"
    print >> sys.stderr, query, (start,end,filename)
    cursor.execute(query,(start, end, filename))
    token_lower = token.decode("utf-8").lower().encode("utf-8")
    for row in cursor.fetchall():
#        print >> sys.stderr, row['philo_name'], type(row['philo_name'])
        if row['philo_name'] == token_lower:
            
            tokenid = row["tokenid"]
            best_parse = (row["lemma"],row["pos"])
            all_parses = {}
            authority = ""
            try:
                lex_connect = sqlite3.connect(db.locals.db_path + "/data/lexicon.db")
                lex_cursor = lex_connect.cursor()
                lex_query = "select Lexicon.lemma,Lexicon.code,authority from parses,Lexicon where parses.tokenid = ? and parses.lex=Lexicon.lexid;"
                lex_cursor.execute(lex_query,(tokenid,))
                raw_parses = []
                for parse_row in lex_cursor.fetchall():
                    if not authority:
                        authority = "Hand parsed by " + parse_row[2]
                    p_lemma, p_pos = parse_row[0].encode("utf-8"),parse_row[1]
                    parse = (p_lemma,p_pos)
                    if parse != best_parse:
                        print>> sys.stderr, parse, "!=", best_parse
                        raw_parses.append( parse )
                        if p_lemma not in all_parses:
                            all_parses[p_lemma] = [p_pos]
                        else:
                            all_parses[p_lemma].append(p_pos)
                    
            except:
                pass            
                
            if i == int(n):
                result_object = {'properties':
                                    [{"property": "Form", "value": row['philo_name']},
                                    {"property": "Lemma", "value": row['lemma']},
                                    {"property": "Parse", "value": row['pos']},
                                    {"property": "Definition", "value": ''},
                                    {"property": "Provenance", "value": authority}],
                                 'problem_report': '/',
                                 'token': row['philo_name'],
                                 'lemma': row['lemma'],
                                 'philo_id': row['philo_id'],
                                 'alt_lemma': [],
                                 "dictionary_name": 'Logeion',
                                 "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + row['lemma'],

                                 "alt_parses" : [{"lemma": l, "parse": all_parses[l], "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + l} for l,p in all_parses.items()]
#                                 "alt_parses": [{'lemma': 'x', 'parse': ["a","b","c","d"], "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + 'x'},
#                                                {'lemma': 'y', 'parse': ["e","f","g"], "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + 'y'}]
                                }
                return json.dumps(result_object)
            else:
                i += 1
    return json.dumps( {} )

if __name__ == "__main__":
    if len(sys.argv) > 6:
        db = DB(sys.argv[1])
        print >> sys.stderr, db.dbh
        cursor = db.dbh.cursor()
        lookup_word(cursor,sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        CGIHandler().run(lookup_word_service)


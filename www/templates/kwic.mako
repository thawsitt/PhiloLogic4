<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<div class="container-fluid">    
    <div id='philologic_response' class="panel panel-default">
        <div id='initial_report'>
           <div id='description'>
                <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                    Export results
                </button>
                <%
                 start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
                 r_status = "."
                 if not results.done:
                    r_status += " Still working..."
                 current_pos = start
                %>
                <div id="search_arguments">
                    Searching database for <b>${q['q'].decode('utf-8', 'ignore')}</b></br>
                    Bibliographic criteria: ${biblio_criteria or "None"}
                </div>
                <div id="search-hits" data-script="${config.db_url + '/scripts/get_total_results.py?' + q['q_string']}">
                    % if end != 0:
                        % if end < results_per_page or end < len(results):
                            Hits <span id="start">${start}</span> - <span id="end">${end}</span> of <span id="total_results">${len(results) or results_per_page}</span><span id="incomplete">${r_status}</span>
                        % else:
                            Hits <span id="start">${start}</span> - <span id="end">${len(results) or end}</span> of <span id="total_results">${len(results) or results_per_page}</span><span id="incomplete">${r_status}</span>         
                        % endif
                    % else:
                        No results for your query.
                    % endif
                </div>
            </div>
        </div>
        <div class="row hidden-xs" id="act-on-report">
            <div class="col-sm-9 col-md-8 col-lg-6">
                <%include file="concordance_kwic_switcher.mako"/>
            </div>
            <div class="col-sm-3 col-md-4 col-lg-4 col-lg-offset-2" id="right-act-on-report">
                <%include file="sidebar_menu.mako"/>
            </div>
        </div>
        <div class="row">
            <div id="results_container" class="col-xs-12" style="overflow: hidden;">
                <div id="kwic_concordance">
                    % for i in fetch_kwic(results, path, q, f.link.byte_query, db, start-1, end):
                        <div class="kwic_line">
                            % if len(str(end)) > len(str(current_pos)):
                                <% spaces = '&nbsp' * (len(str(end)) - len(str(current_pos))) %>
                                <span>${current_pos}.${spaces}</span>
                            % else:
                                <span>${current_pos}.</span>    
                            % endif
                            ${i}
                            <% current_pos += 1 %>
                        </div>
                    % endfor
                </div>
            </div>
            <%include file="show_frequency.mako"/>
        </div>
    <!--    <div id="results-bibliography">
            <span id="show-results-bibliography">Results Bibliography in current page:</span>
        </div>-->
    </div>
    <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>
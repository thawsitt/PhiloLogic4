<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response'>
    <div id='initial_report'>
        <div id='description'>
        <%
        start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
        r_status = "."
        if not results.done:
           r_status += " Still working.  Refresh for a more accurate count of the results."
        %>
        <div id="search_arguments">
                Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}<br>
        </div>
        Hits <span class="start">${start}</span> - <span class="end">${end}</span> of <span id="total_results">${len(results)}</span>${r_status}
        </div>
        <%include file="show_frequency.mako"/>
    </div>
    <div class="results_container" id="results_container">
        <div id='bibliographic_results'>
            <ol id='philologic_cite_list'>
                % for i in results[start-1:end]:
                    <li class='philologic_occurrence' style="padding-top: 10px; padding-bottom: 10px;">
                        <%
                        n += 1
                        %>
                        <span style="padding-left: 5px;">${n}.</span>
                        ##<input type="checkbox" name="philo_id" value="${i.philo_id}">
                        % if i.type == 'doc':
                            <span class='philologic_cite'>${f.biblio_citation(db, config, i)}</span>
                        % else:
                            <span class='philologic_cite'>${f.concordance_citation(db, config, i)}</span>
                        % endif
                    </li>
                % endfor
            </ol>
       </div>
   </div>
   <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>

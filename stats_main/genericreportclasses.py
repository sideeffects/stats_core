import urllib

from django.db import connections
from django.template import Context, Template
from django.utils.html import escape

from cachedqueries import cacheable
from utils import sigdig
import time_series

#===============================================================================

def _get_cursor(db_name):
        """Given a db name returns a cursor."""
        return connections[db_name].cursor()

def expand_templated_query(string_query, context_vars):
    context_vars = context_vars.copy()
    
    context_vars["start_date"] = context_vars['series_range'][0] 
    context_vars["end_date"] = context_vars['series_range'][1]

    tpl_header =  "{% load reports_tags %} "
    tpl = Template(tpl_header + string_query)
    return tpl.render(Context(context_vars))

# TODO: Rename this to get_sql_time_series_for_report
@cacheable(max_num_caches=15)
def get_sql_data_for_report(
        string_query, db_name, context_vars, 
        fill_zeros=True, fill_empty_string=False):
        """
        Generic function to get data for reports, doing sql queries using a
        cursor.
        
        This func will receive the string with the query, the database name to
        create a cursor and the context vars using in the query.
        
        Explanation of the last 3 params:
        
        1. fill_zeros:  For time series the dates that have no value will be
        filled with zeros. 
        
        Sometimes we want to execute a query but the query wont retrieve
        datetimes, it wont be a time series, but different kind of data. For
        example data used for pie charts, for this cases we set fill_zeros=
        False so that we don't treat the data as time series.
        
        2. fill_empty_string: sometimes we want to fill with an empty string 
        instead of with zeros
        """
        
        string_query = expand_templated_query(string_query, context_vars)

        cursor = _get_cursor(db_name)
        cursor.execute(string_query, [])

        series = [(row[0], row[1]) for row in cursor.fetchall()]

        if not fill_zeros and fill_empty_string:
            return time_series.fill_missing_dates_with_zeros(
                series,
                context_vars['aggregation'][:-2], 
                context_vars['series_range'],
                True) 
        if not fill_zeros:
            return series

        return time_series.fill_missing_dates_with_zeros(
            series,
            context_vars['aggregation'][:-2], 
            context_vars['series_range'])  
        
#-------------------------------------------------------------------------------

@cacheable(max_num_caches=15)
def get_orm_data_for_report(query_set, time_field, series_range, 
                            aggregation = None, func = None, 
                            annotate_field = None):
        """
        Function to get data for reports, using django orm for the queries.
        
        This function will receive the queryset, the name of the time field to
        be passed to the time series function, the series range, the aggregation 
        and the function to be passed for aggregation in the time series.    
        """
        
        return time_series.time_series(query_set, time_field, series_range, 
                                       func, aggregation, annotate_field)

#-------------------------------------------------------------------------------
#TODO: Move this to houdini reports, or create an events table for
# the stats main app.

@cacheable(max_num_caches=15)
def get_events_in_range(series_range, aggregation, fill_empty_string = True):
    """
    Get all the events in the give time period. Return the results as a time
    serie [date, event_name]
    """
    
    string_query = """
        select {% aggregated_date "date" aggregation %} AS mydate, 
               group_concat(title separator ', ') AS my_title
        from stats_main_event
        where {% where_between "date" start_date end_date %}
        group by mydate
        order by mydate"""
    
    return get_sql_data_for_report(string_query,'stats', locals(),
                                   fill_zeros = False, 
                                   fill_empty_string = fill_empty_string)
    
#===============================================================================

class Filter(object):
    def __init__(self, report, name, label):
        self.report = report
        self.name = name
        self.label = label

    def url_parm_name(self):
        """Return the name of the GET parameter that is passed into the URL
        for this filter.
        """
        return self.report.name() + "|" + self.name

    def default_value(self):
        """Return the default value for the GET parameter, in case it isn't
        passed in.
        """
        raise NotImplemented()

    def html_form_element(self, current_value):
        """Generate an input inside an html form for this filter, given
        the current value that it should display.
        """
        raise NotImplemented()

    def process_GET_value(self, value):
        """Give the filter a chance to convert the GET parameter value into
        something else.
        """
        return value

class DropdownFilter(Filter):
    def __init__(self, report, name, label, values):
        Filter.__init__(self, report, name, label)
        self.values = values[:]

    def default_value(self):
        return self.values[0]

    def html_form_element(self, current_value):
        html = "<br> <span>%s</span>&nbsp;" % escape(self.label)
        html += '<select style="width: 180px" name="%s">\n' % escape(self.url_parm_name())
        for value in self.values:
            selected_str = (" selected" if value == current_value else "")
            html += '<option%s>%s</option>\n' % (selected_str, escape(value))
        html += "</select>\n"
        return html 

class CheckboxFilter(Filter):
    def __init__(self, report, name, label, checked):
        Filter.__init__(self, report, name, label)
        self.checked_by_default = checked

    def default_value(self):
        return ("1" if self.checked_by_default else "0")

    def html_form_element(self, current_value):
        # Note that if the form containing this checkbox has never been
        # submitted, the corresponding GET parameter will not exist.  If
        # it has been submitted and the checkbox as unchecked, we'll
        # receive a GET value of "0".  If it has been submitted and the
        # checkbox was checked, it will be ["0", "1"], and Django will flatten
        # that to the last value of just "1".
        checked_str = (" checked" if current_value else "")
        return (
            '<input type="hidden" name="%s" value="0">' % (
                escape(self.url_parm_name())) +
            '<input type="checkbox" name="%s" value="1"%s>%s <br>' % (
                escape(self.url_parm_name()), checked_str, escape(self.label)))

    def process_GET_value(self, value):
        # Return True if the checkbox was checked, so that the reports
        # get a sensible value.
        assert value in ("0", "1")
        return value == "1"

#===============================================================================

registered_report_classes = []
            
class ReportMetaclass(type):
    def __new__(cls, name, bases, dct):
        result_class = type.__new__(cls, name, bases, dct)
        registered_report_classes.append(result_class)
        return result_class

#-------------------------------------------------------------------------------

def find_report_class(name):
    report_classes = [
        cls for cls in registered_report_classes if cls.__name__ == name]
    if len(report_classes) == 0:
        return None

    return report_classes[0]

#-------------------------------------------------------------------------------
        
class Report(object):
    __metaclass__ = ReportMetaclass
    
    def get_base_class(self):
        return (self.__class__.__base__).__name__
    
    def get_class_name(self):
        return self.__class__.__name__
    
    def name(self):
        """
        Each report in the same page must have a unique name.
        """
        pass
    
    def title(self):
        pass
    
    def is_heatmap(self):
        return False
    
    def loading_time(self):
        return 0
    
    def get_filters(self):
        return ()

    def get_data(self, series_range, aggregation, filter_values):
        pass

    def supports_aggregation(self):
        return True

    def show_date_picker(self):
        return True

    def minimum_start_date(self):
        import settings
        return settings.REPORTS_START_DATE

    def generate_template_placeholder_code(self, request, filter_values):
        pass
    
    def generate_template_graph_drawing(self, filter_values):
        pass

    def html_for_filters(self, request, filter_values):
        filters = self.get_filters()
        if len(filters) == 0:
            return ""

        filter_names = set(filt.url_parm_name() for filt in filters)

        parts = ['<form>\n']
        parts.extend(
            '<input type="hidden" name="%s" value="%s">\n' % (
                    url_parm_name, escape(value))
            for url_parm_name, value in request.GET.items()
            if url_parm_name not in filter_names)

        for filt in filters:
            parts.append(filt.html_form_element(filter_values.get(filt.name)))

        parts.append('<br> <input type="submit" value="Apply Filters" /> \n')
        parts.append('</form>\n')
        return "".join(parts)

#-------------------------------------------------------------------------------

class ChartReport(Report):
    
    def chart_columns(self, filter_values):
        pass

    def chart_options(self):
        # TODO: Add report types, and determine default options from that type.
        # TODO: Allow each class to contribute to the options template.
        pass
    
    def chart_count(self):
        """
        How many charts to be drawn under the same placeholder.
        For pie charts we can have more than one chart.
        """
        return 1  
    
    def chart_aditional_message(self):
        """
        For messages that need to go before the chart title.
        """
        return "" 
    
    def chart_aditional_information_above(self):
        """
        For extra information that we need to add above the chart, but below 
        the chart title.
        """
        return "" 
    
    def chart_aditional_information_below(self):
        """
        For extra information that we need to add below the chart, at the
        bottom of it.
        """
        return ""  
    
    def chart_loading_time_information(self):
        """
        To add the loading time below charts.
        """
        if self.loading_time == 0:
            return ""
        
        return '''<div style="float:left;">  
                  <font size="1"> loading time: {0}s </font>
                  </div><br>
               '''.format(str(sigdig(self.loading_time)))
        
    def allows_csv_file_generation(self):
        """
        To mark if the report allows csv files generation.
        """
        return True
    
    def generate_filters(self, request, filter_values):
        """
        To get the html code for the filters.
        """
        if len(self.get_filters()) == 0:
            return ""

        return self.html_for_filters(request, filter_values)

    def generate_csv_file(self, request):
        """
        To add button to generate a csv file for the report.
        """
        if not self.allows_csv_file_generation():
            return ""
        
        url =  ("{% url 'generic_report_csv' '"+ self.get_class_name() +
            "' %}?" + request.META["QUERY_STRING"])
        
        return '''
        <a href="''' + url + '''"><button>
        Generate CSV file</button></a>
        ''' 
             
    
    def generate_template_placeholder_code(self, request, filter_values):
        """
        Generate the template placeholder to draw the chart.
        Usually we have just one report under placeholder, but there are cases
        in the pie charts that we draw more than one pie chart under the same
        placeholder.
        """        
        
        filters_placeholder = ''
        report_title = '''
        <div class="graph-title">''' + self.title() + '''</div>
        <br>'''
        
        # How many charts to paint under the same placeholder
        chart_count = self.chart_count() 
        
        if chart_count==1:
            report_placeholder = '''
            <div id="''' + self.name() + '''" class="wide graph" 
            style="float:left; width:940px; height:260px;">'''+ \
            '</div> <br>'
        
        else:
            report_placeholder = ''' 
            <div style="float:left; width:940px; height:260px;">
            '''
            # Draw more than one report inline, under the same report tittle
            for i in range(1, chart_count+1):
                report_placeholder += '''
                <div id="''' + self.name() + str(i) + '''" style="display: inline-block;">
                </div> 
                '''
            report_placeholder +='''
            </div>
            '''   
        
        filters_placeholder = '''<div id="filters_wrapper" 
            style="float:right; width:180px; display: inline-block;">''' +\
            self.generate_filters(request, filter_values) + \
            self.generate_csv_file(request) + "</div>"
        
        return '''<div id="reports_elements_wrapper" 
            style="width:1150px; height:400px;">''' + \
            self.chart_aditional_message() + report_title + \
            self.chart_aditional_information_above() + \
            '<div id="chart_filt_wrapper" style="width:1150px; height:260px;">'+\
            report_placeholder + filters_placeholder + '</div>' + \
            self.chart_loading_time_information() + \
            self.chart_aditional_information_below() + \
            "</div> <br>" # End tag for div reports_wrapper 

    def generate_template_graph_drawing(self, filter_values):
        """
        Generate the graph drawing template placeholder to draw the chart.
        Usually we have just one report to draw, but there are cases
        in the pie charts that we want to paint more than one pie chart under 
        the same placeholder.
        """  
        
        # How many charts to be painted
        chart_count = self.chart_count() 
        
        format_dict = dict(
            name=self.name(),
            options=self.chart_options())
        
        template_string = ""
        if chart_count==1:
            template_string =  (
                ("""{%% data report_data.%(name)s "%(name)s" %%}\n"""
                    % format_dict) +
                self.chart_columns(filter_values) + "\n" +
                "{% enddata %}\n" +
                ("""{%% graph "%(name)s" "%(name)s" %(options)s %%}"""
                    % format_dict)
            )
        else:
            for i in range(1, chart_count+1):
                format_dict['index'] = i-1
                format_dict['count'] = i
                template_string += (
                ("""{%% data report_data.%(name)s.%(index)d "%(name)s%(count)d" %%}\n"""
                    % format_dict) +
                self.chart_columns(filter_values) + "\n" +
                "{% enddata %}\n" +
                ("""{%% graph "%(name)s%(count)d" "%(name)s%(count)d" %(options)s %%}"""
                    % format_dict)
                 ) + "\n" 
        return template_string 
        
#-------------------------------------------------------------------------------

class HeatMapReport(Report):
    
    def is_heatmap(self):
        return True
    
    def supports_aggregation(self):
        return False
    
    def generate_template_placeholder_code(self, request, filter_values):
        
        return ''' <div class="graph-title"> ''' + self.title() + ''' </div>
               <br>
               '''
    def generate_template_graph_drawing(self, filter_values):
        """
        Generate the generic template code to be used for all heatmaps that
        inherit from this class.
        """    
        return '''
             <iframe height="600px" width="100%" frameborder="0"
               scrolling="no" 
               src="{% url "heatmap" "''' +str(self.get_class_name())+ '''" %}
                 {{get_request_string}}">
             </iframe>
             <br>
             '''
    



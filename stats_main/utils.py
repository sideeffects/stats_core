from django.http import HttpResponse
from django.contrib.gis.geoip import GeoIP
from settings import REPORTS_START_DATE, _this_dir
from dateutil.relativedelta import relativedelta

import json
import re
import datetime
import time
import hashlib

#===============================================================================

def text_http_response(content, status=200):
    """
    Translate a response into HTML text.
    """
    # FIXME: Why doesn't Django set the Content-Length header?
    response = HttpResponse(content, status=status)
    response["Content-Length"] = str(len(response.content))
    return response

#-------------------------------------------------------------------------------

class StatsError(Exception):
    """
    Parent class for all stats exceptions.  Requires an HTTP status
    code, an error message template, and optionally some formatting
    arguments for that template.
    """
    def __init__(self, status_code, msg_template, **kwargs):
        Exception.__init__(self, msg_template % kwargs)
        self.status_code = status_code
        
#-------------------------------------------------------------------------------
class ServerError(StatsError):
    """
    Internal error.
    """
    def __init__(self, msg_template, **kwargs):
        StatsError.__init__(self, 500, msg_template, **kwargs)       

#-------------------------------------------------------------------------------
class UnauthorizedError(StatsError):
    """
    Access control (as opposed to permission).
    """
    def __init__(self, msg_template, **kwargs):
        StatsError.__init__(self, 401, msg_template, **kwargs)

#-------------------------------------------------------------------------------

def parse_byte_size_string(string):
    """
    Attempts to guess the string format based on default symbols
    set and return the corresponding bytes as an integer.
    When unable to recognize the format ValueError is raised.

      >>> parse_byte_size_string('1 KB')
      1024
      >>> parse_byte_size_string('2.2 GB')
      2362232012
    """
    
    if not string:
        return
    # Find out the numerical part.
    initial_string = string
    num_string = ""
    while string and string[0:1].isdigit() or string[0:1] == '.':
        num_string += string[0]
        string = string[1:]

    num = float(num_string)

    # Look for the suffix.
    suffix = string.strip() or "B"
    suffix_set = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    prefix = {suffix_set[0]: 1}
    for i, string in enumerate(suffix_set[1:]):
        prefix[string] = 1 << (i+1)*10

    return int(num * prefix[suffix])

#-------------------------------------------------------------------------------
    
def date_range_to_seconds(datetime1, datetime2):
    """
    Computes the number of seconds between two datetime
    """
    return (datetime2 - datetime1).total_seconds() 

#-------------------------------------------------------------------------------

def seconds_to_multiple_time_units(secs):
    """
    This function receives a number of seconds and return how many min, hours,
    days those seconds represent.
    """
    return {
        "seconds": int(secs),
        "minutes": round(int(secs) / 60.0),
        "hours": round(int(secs) / (60.0 * 60.0)),
        "days": round(int(secs) / (60.0 * 60.0 * 24.0)),
    }

#-------------------------------------------------------------------------------

def get_percent(part, whole):
    """
    Get which percentage is a from b, and round it to 2 decimal numbers.
    """
    return round(100 * float(part)/float(whole)  if whole !=0 else 0.0, 2)

#-------------------------------------------------------------------------------

def get_difference(num1, num2):
    """
    Get difference between number one and number two.
    """    
    return num1-num2

#-------------------------------------------------------------------------------

def get_lat_and_long(ip):
    """
    Get the values of the latitude and long by ip address
    """
    g = GeoIP(cache=GeoIP.GEOIP_MEMORY_CACHE)
    
    return  g.lat_lon(str(ip))#lat, long 

#-------------------------------------------------------------------------------   

def get_ip_address(request):
    """
    Get the ip address from the machine doing the request.
    """
    return request.META.get("REMOTE_ADDR", "0.0.0.0")
 
#-------------------------------------------------------------------------------
def _get_valid_date_or_error(str_date):
    """
    Convert a string date to a valid datetime object or return error message.
    """
    
    try:
        return time.strptime(str_date, '%d/%m/%Y')
    except:
        raise ServerError("""INVALID DATE: %(date)s. 
                          The date format must be 'dd/mm/yyyy'. 
                          You can fix the dates in the url and try again. 
                          """,
                          date=str_date)
        
#-------------------------------------------------------------------------------
def _reset_time_for_date(date):
    """
    Set time on a datetime to 00:00:00
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0 )      
    
#-------------------------------------------------------------------------------
def _get_yesterdays_date():
    """
    Get yesterday's date    
    """  
    return datetime.datetime.now() - datetime.timedelta(hours=24)  

#-------------------------------------------------------------------------------
def _get_months_ago_date(months = 3):
    """
    Get n-months ago date. Starting from yesterday's date. 
    """
    return _reset_time_for_date(_get_yesterdays_date() + relativedelta(
                                                             months = -months))  

#-------------------------------------------------------------------------------
def _get_start_request(request, aggregation, minimum_start_date=None):
    """
    Get start date from the request.
    """
    start_request = request.GET.get("start", None)
    
    if start_request is not None:
        t = _get_valid_date_or_error(start_request)
        start = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday)
        
    elif minimum_start_date is not None:
        # Date when we started collecting good data for this report
        start = max(minimum_start_date, _get_months_ago_date())
    else:
        # The start date will be three months from yesterday's date
        start = _get_months_ago_date()
    
    return _adjust_start_date(start, aggregation)
    
#------------------------------------------------------------------------------- 
def _adjust_start_date(start_date, aggregation):
    """
    Adjust the start date depending on the aggregation
    """            
    
    if aggregation == "weekly":
        # Return the Monday of the starting date week    
        return start_date - datetime.timedelta(days = start_date.weekday())
    if aggregation == "monthly":
       # Return the fist day of the starting date's month   
       return datetime.datetime(start_date.year, start_date.month, 1) 
    
    if aggregation == "yearly":
       # Return the first day of the first month of the current year    
       return datetime.datetime(start_date.year, 1, 1)      
    
    # Daily aggregation        
    return start_date
        
#------------------------------------------------------------------------------- 
def _get_end_request(request):
    """
    Get end date from the request.
    """
    end_request = request.GET.get("end", None)
    
    if end_request is not None:
        t = _get_valid_date_or_error(end_request)
        end = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday)
    else:
        # We get yesterday's date    
        end = _reset_time_for_date(_get_yesterdays_date())

    return end

#------------------------------------------------------------------------------- 
def _get_aggregation(get_vars):
    """
    Get aggregation from the request.GET.
    If there is not aggregation we set it to daily by default.
    """
    # For aggregation 
    valid_agg = ["monthly", "weekly", "yearly", "daily"]
    if "ag" not in get_vars:
        return "daily"
    
    aggregation = get_vars["ag"].lower()
    
    if aggregation not in valid_agg and aggregation !="inherit":
        raise ServerError("""INVALID AGGREGATION: %(agg)s. 
                           The valid aggregations are:   
                           'daily', 'weekly', 'monthly' or 'yearly'. 
                           You can fix the aggregation in the url and try again. 
                           """,
                           agg=aggregation)
    elif aggregation=="inherit":
        return "daily"  
    
    return aggregation 

#-------------------------------------------------------------------------------
def get_common_vars_for_charts(request, minimum_start_date=None):
    """
    Get all variables that will be used for the reports.
    """
    
    aggregation = _get_aggregation(request.GET)
    
    return [_get_start_request(request, aggregation, minimum_start_date),
            _get_end_request(request)], aggregation

#-------------------------------------------------------------------------------
def get_list_of_tuples_from_list(list):
    """
    Get a list of tuples from a list.
    
    For example given:    
    
    [1,2,3,4,5,6]
    
    Return [(1,2),(3,4)(5,6)]
    
    """
    output = []
    item = []
    
    for i in list:
        item.append(i)
        if len(item) == 2:
            output.append(item)
            item = []
    if item:
        output.append(item) 
    
    return output
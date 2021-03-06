from django.http import HttpResponse
from houdini_stats.models import *
from stats_main.models import *
from django.contrib.gis.geoip import GeoIP
from settings import REPORTS_START_DATE, _this_dir
from dateutil.relativedelta import relativedelta

import json
import re
import datetime
import time
import hashlib
import math

import settings

#===============================================================================

def text_http_response(content, status=200):
    """
    Translate a response into HTML text.
    """
    # FIXME: Why doesn't Django set the Content-Length header?
    response = HttpResponse(content, status=status)
    response["Content-Length"] = str(len(response.content))
    return response

def json_http_response(content, status=200):
    """
    Translate a response JSON and return.
    """
    return text_http_response(json.dumps(content), status=status)

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

class ServerError(StatsError):
    """
    Internal error.
    """
    def __init__(self, msg_template, **kwargs):
        StatsError.__init__(self, 500, msg_template, **kwargs)

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

    if len(string) == 0:
        return

    # Find out the numerical part.
    initial_string = string
    num_string = ""
    while len(string) and (string[:1].isdigit() or string[:1] == '.'):
        num_string += string[0]
        string = string[1:]

    num = float(num_string)

    # Look for the suffix.
    suffix = string.strip() or "B"
    suffix_set = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    prefix = {suffix_set[0]: 1}
    for i, string in enumerate(suffix_set[1:]):
        prefix[string] = 1 << (i+1)*10

    # If the data is garbage for some reason, just discard it.
    if suffix not in prefix:
        return 0

    return int(num * prefix[suffix])

#-------------------------------------------------------------------------------
def is_valid_machine_config_hash(user_info):
    """
    Compute the hash of the data, ignoring the hash value stored in the data,
    and validate that the computed hash matches the one in the data.
    We want to make sure that the same user configs always create the
    same hash, so the data needs to be ordered.
    """

    string_to_hash = ''.join([
        key + ": " + unicode(user_info[key])
        for key in sorted(user_info.keys())
        if key != "config_hash"])

    print  "The hash passed to server: ", user_info["config_hash"]
    print  "The hash created by server: ", \
        hashlib.md5(string_to_hash).hexdigest()

    return (user_info["config_hash"] ==
        hashlib.md5(string_to_hash).hexdigest())

#-------------------------------------------------------------------------------
def get_or_save_machine_config(user_info, ip_address, data_log_date):
    """
    Get or save if not already in db the machine config

    User Info:{ 'config_hash': '7ef9c42fe4d3748dc9aad755e02852d8',
                'houdini_build_version': '146',
                'houdini_major_version': '13',
                'houdini_minor_version': '0',
                'application_name': 'houdini',
                'operating_system': 'linux-x86_64-gcc4.7',
                'system_memory': '23.55 GB',
                'license_category': 'Commercial',
                'number_of_processors': '12',
                'graphics_card': 'Quadro 600/PCIe/SSE2',
                'graphics_card_version': '4.2.0 NVIDIA 304.88'
                'mac_address_hash'      : '05e8458a3e60776298ece4af002dcef7',
                'cpu_info':
                'system_resolution:
                ""
              }
    """

    # 1. Validate machine config
    config_hash = user_info['config_hash']

#     if not is_valid_machine_config_hash(user_info):
#         print "Different"
#         raise ServerError("Invalid config hash %(name)s.",
#                            name=config_hash)
#
    # 2. Get or save Machine by hardware_id
    hardware_id = user_info.get('mac_address_hash','')
    machine, created = Machine.objects.get_or_create(hardware_id=hardware_id)

    # 3. Get or save Machine Config
    sys_memory = user_info.get('system_memory', "0")
    product = user_info.get('application_name',"") + " " + user_info.get(
                                                         'license_category',"")

    machine_config, created = MachineConfig.objects.get_or_create(
        machine=machine,
        config_hash=config_hash,
        defaults= dict(
            ip_address=ip_address,
            creation_date=data_log_date,
            graphics_card=user_info.get('graphics_card',''),
            graphics_card_version=user_info.get('graphics_card_version',''),
            operating_system=user_info.get('operating_system', ""),
            system_memory=parse_byte_size_string(sys_memory),
            number_of_processors=user_info.get('number_of_processors',0),
            cpu_info=user_info.get('cpu_info', ""),
            system_resolution=user_info.get('system_resolution', ""),
            raw_user_info=str(user_info),
        ))

    if created:
        # Let applications extend the machine config model.
        for app_name in settings.STATS_APPLICATIONS:
            try:
                app_module = __import__(app_name + ".models")
            except ImportError:
                continue

            app_models_module = getattr(app_module, "models")
            creation_function = getattr(
                app_models_module, "create_machine_config_extension", None)
            if creation_function is not None:
                machine_config_extension = creation_function(
                    machine_config, user_info)
                machine_config_extension.save()

    return machine_config

#-------------------------------------------------------------------------------

def is_new_log_or_existing(machine_config, log_id, data_log_date):
    """
    Verify if a log already exists and if not save it.
    Returns true if the log is new, and false otherwise.
    """
    log, created = LogId.objects.get_or_create(
        machine_config=machine_config,
        log_id=log_id,
        defaults=dict(logging_date=data_log_date))
    return created

#-------------------------------------------------------------------------------

def save_crash(machine_config, crash_log, data_log_date):
    """
    Create a HoudiniCrash object and save it in DB..

    crash_log: {
                 u'traceback': u'Caught signal 11\\n\\nAP_Interface::
                              createCrashLog(UTsignalHandlerArg....'
    }
    """
    crash = HoudiniCrash(
        stats_machine_config=machine_config,
        date=data_log_date,
        stack_trace=crash_log['traceback'],
        type="crash",
    )
    crash.save()

#-------------------------------------------------------------------------------

def save_uptime(machine_config, num_seconds, idle_time, data_log_date):
    """
    Create Uptime record and save it in DB.
    """
    uptime = Uptime(
        stats_machine_config=machine_config,
        date=data_log_date,
        number_of_seconds=num_seconds,
        idle_time=idle_time)
    uptime.save()
    
#-------------------------------------------------------------------------------
def save_counts(machine_config, counts_dict, data_log_date):
    """
    Save the data that comes in "counts"
    """
    # Prefix for the houdini tools
    tools_prefix = "tools/"

    for key, count in counts_dict.iteritems():
        if key.startswith(tools_prefix):
            save_tool_usage(
                machine_config, tools_prefix, key, count, data_log_date)
        else:
            save_key_usage(
                machine_config, key, count, data_log_date)

#-------------------------------------------------------------------------------
def save_tool_usage(machine_config, tools_prefix, key, count, data_log_date):
    """
    Create HoudiniToolUsage object and save it in DB.

    Schema: tools|location|tool_name
    - location can be "shelf", "viewer/Object", "viewer/Sop",
      "network/Object", "network/Sop", etc.
    - tool_name can be "sop_box", or "SideFX::spaceship" or
      blank if it's a custom tool
    - the tool name can be followed by "(orbolt)" (if it's an orbolt tool) or
      "(custom_tool)" if it's a nameless custom tool.
    """
    is_asset = False
    is_custom = False

    for mode, name in HoudiniToolUsage.TOOL_CREATION_MODES:
        prefix = tools_prefix + name
        if key.startswith(prefix):
            # Find "|" to get tool creation mode
            pipe_pos = key.index("|")
            tool_creation_location = key[len(prefix)+1: pipe_pos]
            tool_name = key[pipe_pos +1:]

            # Verify if tool type is a custom_tool
            if "(custom_tool)" in tool_name:
                tool_name = re.sub('[\(\)]', "", tool_name)
                is_custom = True
            # Verify if tool type is an Orbolt asset
            elif "(orbolt)" in tool_name:
                tool_name = tool_name.replace("(orbolt)","")
                is_asset = True

            tools_usage = HoudiniToolUsage(
                stats_machine_config=machine_config,
                date=data_log_date,
                tool_name=tool_name,
                tool_creation_location=tool_creation_location,
                tool_creation_mode=mode,
                count=count,
                is_builtin=(not is_asset and not is_custom),
                is_asset=is_asset)
            tools_usage.save()
            break
        
#-------------------------------------------------------------------------------
def save_key_usage(machine_config, key, count, data_log_date):
    """
    Create HoudiniUsageCount object and save it in DB.
    """
    key_usage = HoudiniUsageCount(
        stats_machine_config=machine_config,
        date=data_log_date,
        key=key,
        count=count)
    key_usage.save()

#-------------------------------------------------------------------------------
def persistent_stats(machine_config, persistent_stats_dict, data_log_date):
    """
    Save the data that comes in persistent stats
    """
    
    for key, value in persistent_stats_dict.iteritems():
        # Try to find the key value pair and if it doesn't exists insert a new
        # one
        try:
            key_value_pair = HoudiniPersistentStatsKeyValuePair.objects.get(
                                                           key=key, value=value)
        except:
            key_value_pair = HoudiniPersistentStatsKeyValuePair(key=key,
                                                                value=value)
            key_value_pair.save()    
        
        assert key_value_pair is not None
        
        # Get houdini_major_version and houdini_minor_version from machine 
        # config extension 
        machine_config_ext = HoudiniMachineConfig.objects.get(
                                                machine_config = machine_config) 
        
        # Try to find if there is a not a persistent stats like this one already
        # and if so update it if needed, if not insert a new one
        try:
            # Get houdini permanent stats
            hou_per_stats = HoudiniPersistentStats.objects.get(
               machine = machine_config.machine,
               houdini_major_version = machine_config_ext.houdini_major_version,
               houdini_minor_version = machine_config_ext.houdini_minor_version,
               )
            # Find if there is an entry that already contains this persistent
            # stats and update it if needed
            hou_per_stats_entry = HoudiniPersistentStatsEntry.objects.filter(
                                              persistent_stats = hou_per_stats)
            need_to_add = True  
            for entry in hou_per_stats_entry:
                # See if we have a matching key and value.  If so, we won't
                # add anything later.
                if entry.persistent_stats_kvp == key_value_pair:
                    need_to_add = False
                    break
                
                # If we have a matching key but different value, delete the
                # old pair and add the new one later.
                if entry.persistent_stats_kvp.key == key:
                    hou_per_stats_entry.delete()
                    break

            if need_to_add:
                hou_per_stats_entry = HoudiniPersistentStatsEntry(
                                          persistent_stats = hou_per_stats,
                                          persistent_stats_kvp = key_value_pair) 
                hou_per_stats_entry.save()
        
        except:
            # Create persistent stats object and save it
            hou_per_stats = HoudiniPersistentStats(date = data_log_date,
               machine = machine_config.machine, hash = "",
               houdini_major_version = machine_config_ext.houdini_major_version,
               houdini_minor_version = machine_config_ext.houdini_minor_version,
                   )                                        
            hou_per_stats.save()
            # Create persistent stats entry object and save it
            hou_per_stats_entry = HoudiniPersistentStatsEntry(
                                          persistent_stats = hou_per_stats,
                                          persistent_stats_kvp = key_value_pair) 
            hou_per_stats_entry.save()

#-------------------------------------------------------------------------------
def save_strings(machine_config, strings_dict, data_log_date):
    """
    Save the data that comes in "strings"
    """
    for key, value in strings_dict.iteritems():
        houdini_string = HoudiniString(
            stats_machine_config=machine_config,
            date=data_log_date,
            key=key,
            value=value)
        houdini_string.save()

#-------------------------------------------------------------------------------
def save_sums_and_counts(machine_config, sums_and_counts, data_log_date):
    """
    Save sums and counts in DB.

    "sums_and_counts":{
            "cook/SOP_xform/time": [0.524806, 4171],
            "cook/SOP_scatter/time": [0.041588, 3],
            "cook/SOP_merge/time": [0.041572, 3],
            "cook/mantra/mantra1/time": [36.195406, 1],
            "cook/SOP_copy/time": [1.512519, 3]
     }
    """
    for key, sum_count in sums_and_counts.iteritems():
        sum_and_count_object = HoudiniSumAndCount(
            stats_machine_config=machine_config,
            date=data_log_date,
            key=key,
            sum=sum_count[0],
            count=sum_count[1])
        sum_and_count_object.save()

#-------------------------------------------------------------------------------
def save_flags(machine_config, flags, data_log_date):
    """
    Save flags in DB.

    "flags":[ "key1", "key2", "key3" ]
    """
    for key in flags:
        flag_object = HoudiniFlag(
            stats_machine_config=machine_config,
            date=data_log_date,
            key=key)
        flag_object.save()

#-------------------------------------------------------------------------------
def save_logs(machine_config, logs, data_log_date):
    """
    Save logs in DB.

    "logs": {
            "web_server": {
                "80.511179": "user requested page /",
                "90.234239": "user requested page /index"
            }

    """
    for key, values in logs.iteritems():
        for timestamp, log_entry in values.iteritems():
            log_object = HoudiniLog(
                stats_machine_config=machine_config,
                date=data_log_date,
                key=key,
                timestamp=timestamp,
                log_entry=log_entry)
            log_object.save()

#-------------------------------------------------------------------------------

def save_error_log(description, stack_trace, ip_address):
    """
    Create ErrorLog object and save it in DB.
    """
    error_log = ErrorLog(
        description=description,
        date=datetime.datetime.now(),
        stack_trace=stack_trace,
        ip_address=ip_address)
    error_log.save()

#-------------------------------------------------------------------------------

def save_data_log_to_file(date, config_hash, json_data, ip_adress):
    """
    Save the received data log to a text file
    """
    with open(_this_dir + "/../houdini_logs.txt", "a") as log_file:
        log_file.write("""\n Date log saved: {0}, IP: {1}, Config Hash: {2}, Date: {3} \n {4}
                       """.format(datetime.datetime.now(), ip_adress,
                                  config_hash, date, str(json_data)))

#-------------------------------------------------------------------------------

def date_range_to_seconds(datetime1, datetime2):
    """
    Computes the number of seconds between two datetime
    """
    return (datetime2 - datetime1).total_seconds()

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
    return round(100 * float(part)/float(whole) if whole != 0 else 0.0, 2)

def get_difference(num1, num2):
    """
    Get difference between number one and number two.
    """
    return num1 - num2

#-------------------------------------------------------------------------------

def get_lat_and_long(ip):
    """
    Get the values of the latitude and long by ip address
    """
    g = GeoIP(cache=GeoIP.GEOIP_MEMORY_CACHE)

    return  g.lat_lon(str(ip))#lat, long

def get_ip_address(request):
    """
    Get the ip address from the machine doing the request.
    """
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _get_valid_date_or_error(str_date):
    """
    Convert a string date to a valid datetime object or return error message.
    """
    try:
        return time.strptime(str_date, '%d/%m/%Y')
    except:
        raise ServerError(
            "INVALID DATE: %(date)s.\n"
            "The date format must be 'dd/mm/yyyy'.\n"
            "You can fix the dates in the url and try again.\n",
            date=str_date)

def _reset_time_for_date(date):
    """
    Set time on a datetime to 00:00:00
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

def _get_yesterdays_date():
    """
    Get yesterday's date
    """
    return datetime.datetime.now() - datetime.timedelta(hours=24)

def _get_months_ago_date(months = 3):
    """
    Get n-months ago date. Starting from yesterday's date.
    """
    return _reset_time_for_date(
        _get_yesterdays_date() + relativedelta(months = -months))

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
        raise ServerError(
            "INVALID AGGREGATION: %(agg)s.\n"
            "The valid aggregations are:\n"
            "'daily', 'weekly', 'monthly' or 'yearly'.\n"
            "You can fix the aggregation in the url and try again.\n",
            agg=aggregation)
    elif aggregation=="inherit":
        return "daily"

    return aggregation

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

#-------------------------------------------------------------------------------

def sigdig(value, digits = 3):
    """
    Return float number with certain amount of significant digits
    """
    order = int(math.floor(math.log10(math.fabs(value))))
    places = digits - order - 1
    if places > 0:
        fmtstr = "%%.%df" % (places)
    else:
        fmtstr = "%.0f"
    return fmtstr % (round(value, places))

#-------------------------------------------------------------------------------

def validate_log_date(start_time, end_time):
    """
    Validate that the log dates are not greater than the current date.
    Return log date to use for the data logging too.
    """
    current_date = datetime.datetime.now()  
    
    if current_date < datetime.datetime.fromtimestamp(start_time) or \
       current_date < datetime.datetime.fromtimestamp(end_time):
        return False, current_date
    
    return True, datetime.datetime.fromtimestamp(start_time)
        

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from utils import *
from stats_main.utils import get_ip_address

import json
import datetime
import traceback
import settings

#-------------------------------------------------------------------------------

class API(object):
    """
    Handle web API requests.
    """

    @classmethod
    def api_function(cls, function):
        """
        This decorator can be used to add any function as a static method
        of this class.

        It is used by extensions to the stats system to extend the API.
        """
        function._api_static_method = True
        setattr(cls, function.__name__, staticmethod(function))

    _extensions_are_loaded = False

    @classmethod
    def _ensure_extensions_are_loaded(cls):
        """
        Give other applications a chance to extend the API.
        
        We import their api modules, if they exist, to perform the extensions.
        """
        if cls._extensions_are_loaded:
            return

        cls._extensions_are_loaded = True
        for app_name in settings.STATS_APPLICATIONS:
            try:
                app_module = __import__(app_name + ".api")
            except ImportError:
                continue

    def __init__(self):
        self._ensure_extensions_are_loaded()

    def dispatch(self, request):
        """
        Dispatch requests for '/api' URLds by:
           1. Unpacking the handler and post data from the JSON in the request.
           2. Looking up the handler method.
           3. Dispatching to it.
           4. Wrapping its response as JSON.
        The handler method must take the user name as its first argument, as
        well as optional extra arguments.  It normally returns a valid
        HttpResponse or raises an StoreError exception when it wants to give the
        user helpful error messages.  However, buggy or malicious callers can
        make a handler raise other exceptions, in which case the production
        server will return a non-descriptive error message.
        """
        try:
            result = self._dispatch_without_catching_api_errors(request)
        except StatsError as e:
#            return text_http_response(
#                traceback.format_exc(), status=e.status_code)
            # Properly raise an exception so it's handled by the logger and
            # we're notified if Houdini attempts to call an API function that
            # doesn't exist.
            raise

        # If the API function didn't return an HttpResponse, wrap the result
        # in JSON and convert to an HttpResponse on its behalf.
        if not isinstance(result, HttpResponse):
            result = json_http_response(result)

        return result

    def _dispatch_without_catching_api_errors(self, request):
        """
        As the name suggests, this help method dispatches without
        looking for or handling errors.
        """
        try:
            # request.POST is a magic variable that loads the data on demand
            # when you access it.
            json_data = request.POST.get("json")
        except IOError as e:
            # For whatever reason, django's engine could not read the post
            # data.  Don't bother to generate an error trigger an email to
            # be sent to the site administrators.
            return text_http_response(
                "Error reading POST data:\n" + traceback.format_exc(), 500)

        if "json" not in request.POST:
            return text_http_response(
                "'json' not given in the POST data", 500)

        # Look up the API method, making sure that it exists and has been
        # flagged as an API method.
        try:
            handler_name, args, kwargs = json.loads(json_data)
        except ValueError:
            save_error_log(
                "Errors in stats file", traceback.format_exc(),
                get_ip_address(request))

            # Return True so this machine will stop trying to send the
            # garbage data.
            return True

        handler = getattr(self, handler_name, None)
        if handler is None or not hasattr(handler, "_api_static_method"):
            raise ServerError("Invalid API handler name %(name)s.",
                              name=handler_name)

        return handler(request, *args, **kwargs)

#------------------------------------------------------------------------

@API.api_function
def send_stats(request, machine_config_info, stats):
    """
    Save user stats.

    This API function is called by older versions of Houdini.
    """
    return _send_stats_main(
        request,
        stats["stat_log_version"],
        machine_config_info,
        json.loads(stats["json_content"]))

@API.api_function
def send_machine_config_and_stats(request, machine_config_and_stats_json):
    """
    Save user stats.

    This API function is called by the current version of Houdini.
    """
    # Catch errors if the log file is empty.
    json_content = ""
    try:
        json_content = json.loads(
            machine_config_and_stats_json['json_content'])
    except ValueError:
        save_error_log(
            "Errors in stats file", traceback.format_exc(),
            get_ip_address(request))
        return True

    # Catch errors where the json_content is not a dictionary or contains
    # different data types like a number.
    try:
        stat_log_version = machine_config_and_stats_json['stat_log_version']
        machine_config = json_content['machine_config']
        stats = json_content['stats']
    except (ValueError, KeyError):
        formated_stack_trace = (
            "json_content: " + str(json_content) + " - " +
            traceback.format_exc())

        save_error_log(
            "Errors in stats file", formated_stack_trace,
            get_ip_address(request))
        return True

    return _send_stats_main(
        request, stat_log_version, machine_config, stats)

def _send_stats_main(request, stat_log_version, machine_config_info, stats):
    # We will only save the logs where version is 2 or higher.  Logs
    # without a log id also won't be saved.
    if stat_log_version < 2 or "log_id" not in stats.keys():
        return True

    # Start by computing the total time they ran the product.
    is_log_date_correct, data_log_date = validate_log_date(stats["start_time"],
                                                           stats["end_time"])
    # If the log dates received don't pass the validations don't do anything 
    # else just skip that entire log
    if not is_log_date_correct:
        return True
    
    # Get total seconds and total idle time
    total_sec = stats["end_time"] - stats["start_time"]
    total_idle_time = (stats["idle_time"]
        if stats.has_key("idle_time") else 0)

    # Avoid adding data where the total time idle is greater than the
    # overall total, since the database doesn't like that.
    if total_idle_time > total_sec:
        total_idle_time = total_sec

    # Get or save machine config
    ip_address = get_ip_address(request)
    machine_config = get_or_save_machine_config(
        machine_config_info, ip_address, data_log_date)

    # Save the log id if it hasnt been saved in the db yet.  Only save the
    # stats data if the log id was new.
    is_new_log = is_new_log_or_existing(
        machine_config, stats["log_id"], data_log_date)
    if not is_new_log:
        return True

    # Finally, save the pieces of the json data into the database.
    save_uptime(
        machine_config, total_sec, total_idle_time, data_log_date)
    save_counts(
        machine_config, stats["counts"], data_log_date)
    save_sums_and_counts(
        machine_config, _get_sums_and_counts(stats),
        data_log_date)
    save_flags(
        machine_config, stats["flags"], data_log_date)
    save_logs(
        machine_config, stats["logs"], data_log_date)
    
    if "persistent_stats" in stats:
        persistent_stats(
            machine_config, stats["persistent_stats"], data_log_date)

    if "strings" in stats:
        save_strings(
            machine_config, stats["strings"], data_log_date)

    # Put everything inside a log file as well.
    save_data_log_to_file(
        data_log_date, machine_config_info['config_hash'], stats,
        ip_address)
    return True

def _get_sums_and_counts(stats):
    """
    To return properly sums and counts. There are machines who might not be 
    sending this key yet.
    """
    if stats.has_key("sums_and_counts"):
        return stats["sums_and_counts"]
    return stats.get("sums", {})

@API.api_function
def send_crash(request, machine_config_info, crashlog):
    """
    Save houdini crashes
    """
    machine_config = get_or_save_machine_config(
        machine_config_info, get_ip_address(request),
        datetime.datetime.now())
    save_crash(machine_config, crashlog, datetime.datetime.now())
    return True

#-------------------------------------------------------------------------------

@require_http_methods(["POST"])
@csrf_exempt
def api_view(request):
    """
    Dispatch requests for API URLs.
    """
    # Note that other applications may have added static methods to the API
    # class at load time, before this function gets called.
    return API().dispatch(request)

#-------------------------------------------------------------------------------


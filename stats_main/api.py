
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

    # API methods can be flagged as either requiring a login or not.  All other
    # methods, including those provided by the object class, will not be
    # visible in the API.
    def login_required(method):
        method._login_required = True
        return method

    def login_not_required(method):
        method._login_required = False
        return method

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
            return self._dispatch_without_catching_api_errors(request)
        except StatsError as e:
            # Properly raise an exception so it's handled by the logger and
            # we're notified if Houdini attempts to call an API function that
            # doesn't exist.
            raise

            #return text_http_response(
            #    traceback.format_exc(), status=e.status_code)

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
            
        
        handler_name, args, kwargs = json.loads(json_data)
        
        handler = getattr(self, handler_name, None)
        
        if handler is None:
            raise ServerError("Invalid API handler name %(name)s.",
                              name=handler_name)
            
        return handler(request, *args, **kwargs)

    @login_not_required
    def send_stats(self, request, machine_config_info, stats):
        """
        Save user stats
        """
        return self.send_stats_main(
            request,
            stats["stat_log_version"],
            machine_config_info,
            json.loads(stats["json_content"]))

    @login_not_required
    def send_machine_config_and_stats( self, request, 
                                       machine_config_and_stats_json):
        json_content = ""
        # try/except to avoid getting errors when the log file is empty
        try:
            # Get json content
            json_content = json.loads(
                                  machine_config_and_stats_json['json_content'])
        except:
            import traceback
            save_error_log("Errors in stats file", traceback.format_exc(), 
                           get_ip_address(request))
            return json_http_response(True)
        
        # try/except to avoid errors when the json_content is not a dictionary
        # and contains different data types like a number
        try:
            return self.send_stats_main(request, 
                          machine_config_and_stats_json['stat_log_version'],
                          json_content['machine_config'], json_content['stats'])
        except:
            import traceback
            formated_stack_trace = "json_content: " + str(json_content) + " - "+\
                    traceback.format_exc()
            
            save_error_log("Errors in stats file", formated_stack_trace,
                           get_ip_address(request))
            return json_http_response(True)
            
        
    def send_stats_main(self, request, stat_log_version, machine_config_info, 
                        stats):
        
        # We will just save the logs which version is 2 or higher
        if stat_log_version >=2:
            # Get json content. Contains start_time and end_time and counts for the 
            # Houdini tools usage
            json_data = stats
                
            # Get total seconds
            data_log_date =  datetime.datetime.fromtimestamp(json_data["start_time"])
            total_sec = json_data["end_time"] - json_data["start_time"]
            total_idle_time = json_data["idle_time"] \
                if json_data.has_key("idle_time") else 0 
                
            # Get ip address
            ip_address = get_ip_address(request)     
                
            # Get or save machine config
            machine_config = get_or_save_machine_config(machine_config_info,
                                 ip_address, data_log_date)
                
            # The logs without log id wont be saved
            is_new_log = False
            if "log_id" in json_data.keys():                        
                # Save log id if it hasnt been saved in the db yet
                is_new_log = is_new_log_or_existing(machine_config, 
                                                    json_data["log_id"], 
                                                    data_log_date)
                
                # Just save the stats data if  the log id was new
                if is_new_log:
                    # Save uptime
                    save_uptime(machine_config, total_sec, total_idle_time, 
                                data_log_date)
                    # Save counts 
                    save_counts(machine_config, json_data["counts"], 
                                data_log_date)
                    
                    # Save sums and counts
                    save_sums_and_counts(machine_config, 
                                         _get_sums_and_counts(json_data), 
                                         data_log_date)
                    
                    # Save flags
                    save_flags(machine_config, json_data["flags"], 
                               data_log_date)
                    # Save logs
                    save_logs(machine_config, json_data["logs"], 
                              data_log_date)
                       
                    # Put everything inside json
                    save_data_log_to_file(data_log_date, 
                                          machine_config_info['config_hash'],
                                          json_data, ip_address)
                      
        return json_http_response(True)

    
    @login_not_required
    def send_crash(self, request, machine_config_info, crashlog):
        """
        Save houdini crashes
        """
        # Get or save machine config
        machine_config = get_or_save_machine_config(machine_config_info,
                                                    get_ip_address(request),
                                                    datetime.datetime.now())
        # Save the crash
        save_crash(machine_config, crashlog, datetime.datetime.now())
        
        return json_http_response(True)

    @login_not_required
    def send_license_failure(self, request, machine_config_info, failure_info):
        print "machine config info (fail):", machine_config_info
        print "failure info:", failure_info
        return json_http_response(True) 

    @login_not_required
    def send_apprentice_activation(self, request, machine_config_info, 
                                   activation_info):
        print "machine config info (Apprentice activation):", machine_config_info
        print "activation info:", activation_info
        return json_http_response(True) 
                
#-------------------------------------------------------------------------------

@require_http_methods(["POST"])
@csrf_exempt
def api_view(request):
    """
    Dispatch requests for API URLs.
    """
    return API().dispatch(request)

#-------------------------------------------------------------------------------

def _get_sums_and_counts(json_data):
    """
    To return properly sums and counts. There are machines who might not be 
    sending this key yet.
    """
    
    if json_data.has_key("sums_and_counts"):
        return json_data["sums_and_counts"]
    elif json_data.has_key("sums"):
        return json_data["sums"]
    else:
        return {}    
    

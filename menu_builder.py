from django.core.urlresolvers import reverse
from settings import TOP_MENU_OPTIONS

#-------------------------------------------------------------------------------

def menu_option_names_to_titles(menu_option_infos):
    """Build a dictionary mapping menu option names to titles."""
    
    return dict((menu_option_info[0], menu_option_info[1])
        for menu_option_info in menu_option_infos)

#-------------------------------------------------------------------------------

def menu_option_names(menu_option_infos):
    """Return a sequence of just the menu option names."""
    return [
        menu_option_info[0]
        for menu_option_info in menu_option_infos]

#-------------------------------------------------------------------------------

def menu_option_view_or_report_classes(menu_option_info):
    # Each menu option info will be of this format:
    #     (name, title, report_class_sequence or view_name)
    return menu_option_info[2]

#-------------------------------------------------------------------------------

def report_classes_for_menu_option(menu, option_name):
    menu_option_info = find_menu_option_info(
        TOP_MENU_OPTIONS[menu]["menu_options"], option_name)
    return menu_option_view_or_report_classes(menu_option_info)

#-------------------------------------------------------------------------------

def build_top_menu_options_next_prevs():
    "Get a dictionary with all the menu options nexts and previous."
    top_menu_options_nexts_prevs = {}
    for top_menu_name, top_menu_info in TOP_MENU_OPTIONS.items():
        options = menu_option_names(
            top_menu_info["menu_options"])

        for index, option in enumerate(options):
            prev_option = (options[index-1] if index-1 >= 0 else "")
            next_option = (options[index+1] if index+1 < len(options) else "")
            top_menu_options_nexts_prevs[option] = {
                "next": next_option,
                "prev": prev_option}

    return top_menu_options_nexts_prevs

#-------------------------------------------------------------------------------

def find_menu_option_info(menu_option_infos, option_name):
    return [menu_option_info for menu_option_info in menu_option_infos
        if menu_option_info[0] == option_name][0]


 
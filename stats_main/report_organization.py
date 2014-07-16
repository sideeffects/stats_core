from django.core.urlresolvers import reverse

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


REPORT_MODULES =(
    'houdini_stats.reports.houdini',
    'houdini_licenses.reports.downloads',
    'houdini_licenses.reports.apprentice',
    'houdini_surveys.reports.surveys',
    'houdini_forum.reports.sidefx_website',
    'orbolt.reports.orbolt_reports'
)

top_menu_options = OrderedDict([
    ("houdini", {
        "menu_url_prefix": "houdini",
        "menu_name": "Houdini",
        "menu_options": [
            ("downloads", "Houdini Downloads", [
                "HoudiniDownloadsOverTime",
                "CommercialVsApprenticeDownloadsInPercentages" 
            ]),
            ("usage", "Usage", [
                "NewMachinesOverTime",
                "MachinesActivelySendingStats",
                "AvgNumConnectionsFromSameMachine"
            ]),
            ("uptime", "Session Information", [
                "AverageSessionLength",
                "AverageUsageByMachine"
            ]),
            ("crashes", "Crashes",[
                "NumCrashesOverTime",
                "NumOfMachinesSendingCrashesOverTime",
                "AvgNumCrashesFromSameMachine",
                "CrashesByOS",
                "CrashesByProduct"
            ]),
            ("tools_usage", "Shelf & Tab menu Tools", [
                "MostPopularTools",
                "MostPopularToolsShelf",
                "MostPopularToolsViewer",
                "MostPopularToolsNetwork"
            ]),
            ("versions_and_builds", "Versions and builds",[
                "VersionsAndBuilds",
                "VersionsAndBuildsApprentice",
                "VersionsAndBuildsCommercial"              
            ]),
        ],
        "groups": ['staff', 'r&d'],
    }),
    ("apprentice", {
        "menu_url_prefix": "apprentice",
        "menu_name": "Apprentice",
        "menu_options": [
            ("apprentice_activations", "Apprentice Activations",[
                "ApprenticeActivationsVsDownloads",
                "ApprenticeActivationsAndReactivationsPercentages",
                "PercentagesApprenticeNewActivationsFromApprenticeDownloads"
            ]),
            ("apprentice_hd", "Apprentice HD",[
                "ApprenticeHdLicensesOverTime",
                "ApprenticeHdCumulativeLicensesOverTime"
            ]),
            ("apprentice_heatmap", "Apprentice Activations Heatmap",[
                "ApprenticeActivationsHeatmap"
            ]),
        ],
        "groups":['staff', 'r&d'],
    }),
    ("surveys", {
        "menu_url_prefix": "surveys",
        "menu_name": "Surveys",
        "menu_options": [
            ("sidefx_labs", "labs.sidefx.com survey",[
                "BreakdownMayaUnityCounts",
                "BreakdownMayaUnityOverTime"
            ]),
            ("apprentice_followup","Apprentice survey",[
                "PercentageUsersWhoRepliedApprenticeSurvey",
                "ApprenticeFollowUpSurvey"
             ]),
        ],
        "groups":['staff', 'r&d'],
    }),
    ("sidefx.com", {
        "menu_url_prefix": "sidefx.com",
        "menu_name": "Sidefx.com",
        "menu_options": [
            ("login_registration", "Login & Registration",[
                "NewUserRegistrationsOverTime",
                "BreakdownRegistrationsMethods"
            ]),
        ],
        "groups":['staff', 'r&d'],
    }),
                                
   ("orbolt", {
        "menu_url_prefix": "orbolt",
        "menu_name": "Orbolt",
        "menu_options": [
            ("overview", "Overview",[
                "RevenueOverTime",
                "PurchasesOverTime",
                "NewUploadsOverTime",
                "NewVersionsOfExistingAssets",
                "NewUsersOverTime",
                "OSAndBrowserCombinations",
                "PercentageLicensesByCommercialAndApprentice"
            ]),
            ("licenses", "Licenses",[
                "LicensesOverTime",
                "PercentagesLicensesAssetNotDownloaded",
                "LicensesOverTimeByOs",
                "PercentagesLicensesAssetNotDownloadedByOs",
                "LicensesOverTimeMacOs",
                "PercentagesLicensesAssetNotDownloadedMacOs",
                "LicensesOverTimeWindows",
                "PercentagesLicensesAssetNotDownloadedWindows",
                "LicensesOverTimeLinux",
                "PercentagesLicensesAssetNotDownloadedLinux"
            ]),            
            ("licenses_heatmap", "Licenses Heatmap",[
                "AssetLicensesHeatmap"
            ]),
            ("top_assets", "Top Assets",[
                "TopDownloadedAssets",
                "TopViewedAssets",
                "TopPaidAssets",
                "TopGrossingAssets"
            ]),
            ("trials", "Trials",[
                "TrialLicensesOverview",
                "TrialLicensesForPaidAssets",
                "TrialLicensesUpgrades"                
            ]),             
        ],
        "groups":['staff', 'r&d'],
    }),                             
])

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
        top_menu_options[menu]["menu_options"], option_name)
    return menu_option_view_or_report_classes(menu_option_info)

#-------------------------------------------------------------------------------

def build_top_menu_options_next_prevs():
    "Get a dictionary with all the menu options nexts and previous."
    top_menu_options_nexts_prevs = {}
    for top_menu_name, top_menu_info in top_menu_options.items():
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


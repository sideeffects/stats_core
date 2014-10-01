import settings
import os
import tarfile
import glob

source_file_name = "source.tar"

def exclude_file(x):
    return (os.path.basename(x) in (".git", ".gitignore") or
        (os.path.splitext(x)[1] == ".pyc"))
    
# Stats core release dirs and files
current_directory = os.path.basename(settings._this_dir)
release_dirs_and_files = ["templates", "googlecharts", "stats_main", "bin",
                          "backups", "Makefile", 
                          "wsgi-script/django.wsgi"] + glob.glob("*.py")

# Opening tar file
tar = tarfile.open(source_file_name, 'w:') 

# Add the directories and files from stats-core to the tar ball 
for dir_or_file in release_dirs_and_files:
    tar.add(dir_or_file, arcname = current_directory + "/" + dir_or_file,
            exclude = exclude_file)

# Add extension apps to the tar file
for extension_relative_dir in settings.STATS_EXTENSIONS:
    extension_dir = os.path.normpath(
        os.path.join(settings._this_dir, extension_relative_dir))
    tar.add(extension_dir, 
            arcname = os.path.basename(extension_dir),
            exclude = exclude_file)

# Closing tar file 
tar.close()
    
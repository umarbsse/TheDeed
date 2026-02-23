import os
import configparser
def get_config_val(variable_name):
    file_path='config.ini'
    """
    Searches for a variable name across all sections in an INI file.
    Returns the value if found, otherwise returns an empty string.
    """
    # Check if the file exists first to avoid errors
    if not os.path.exists(file_path):
        return ''

    config = configparser.ConfigParser()
    config.read(file_path)

    # Iterate through all sections to find the key
    for section in config.sections():
        if variable_name in config[section]:
            return config[section][variable_name]

    # Return empty string if not found in any section
    return ''
class dds9m_config(object):
    '''
    configuration file for arduino switch client
    info is the configuration dictionary in the form
    {channel_name: (port, display_location, inverted)), }
    '''
    info = {'Channel 0': ('Channel 0', 0),
            'Channel 1': ('Channel 1', 1),
	        'Channel 2': ('Channel 2', 2),
	        'Channel 3': ('Channel 3', 3),
            }

    ip = 'localhost'
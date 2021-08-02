defaults = [
    dict(
        key='GuestPasswordLength',
        value='9',
        doc='Number of characters of the guest password. Default: 9.',
        validator=r'^(\d+)$'
    ),
    dict(
        key='GuestPasswordUpdateInterval',
        value='86400',
        doc='Number of seconds before refreshing the guest password. Default: 86400.',
        validator=r'^(\d+)$'
    ),
    dict(
        key='ClearpassDeviceExpireDate',
        value='09/04/+4',
        doc='The date at which the a device on Clearpass will expire, if it is the first device registered by the account.\n'
            'Format: mm/dd/yyyy\n'
            'However, each part of the date can be replaced by a +value or -value. Eg: "-1/05/+4" means "the 5th day 4 years minus 1 month from the first registration date."\n'
            'Default: 09/04/+4',
        validator=r'^(0[1-9]|1[012]|[+-]\d+?)/(0[1-9]|[12][0-9]|3[01]|[+-]\d+?)/(\d{4}|[+-]\d+?)$'
    ),
    dict(
        key='ClearpassExpireAction',
        value='4',
        doc='Value is from the do_expire field in https://www.arubanetworks.com/techdocs/ClearPass/CPGuest_UG_HTML_6.5/Content/Reference/GuestManagerStandardFields.htm\n'
            'Default: 4',
        validator=r'^([0-4])$'
    ),
    dict(
        key='LoginIPRestriction',
        value='192.168.0.0/16',
        doc='IPv4 CIDR block notation of which IPs should be allowed to access the site. Otherwise an error is displayed. Default: 192.168.0.0/16',
        validator=r'^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)/([0-9]|[12][0-9]|3[0-2])$'
    ),
    dict(
        key='RatelimitSecondsBetweenAttemptsPerIP',
        value='1',
        doc='Time in seconds between successive login attempts, based on IP address. Default: 1',
        validator=r'^(\d+)$'
    ),
    dict(
        key='RatelimitPasswordPerHourLimit',
        value='5',
        doc='Incorrect password attempts allowed per hour until rate limited. Default: 5',
        validator=r'^(\d+)$'
    ),
    dict(
        key='RatelimitModificationsUntilNotNewUser',
        value='3',
        doc='MAC address modifications allowed to account until the user is no longer considered a new user.\n'
            'After a user is no longer considered a new user, more rate limit restrictions will apply. Default: 3',
        validator=r'^(\d+)$'
    ),
    dict(
        key='RatelimitModificationsPerHourAfterNotNewUser',
        value='5',
        doc='Allowed modifications per hour until after the user is no longer considered new.\n'
            'Keep in mind that "RatelimitUniqueMacAddressEveryHours" is also in effect. Default: 5',
        validator=r'^(\d+)$'
    ),
    dict(
        key='RatelimitUniqueMacAddressEveryHours',
        value='18',
        doc='Number of hours until a MAC address already seen can re-register after the user is no longer considered new.\n'
            'Keep in mind that RatelimitModificationsPerHourAfterNotNewUser is also in effect. Default: 18',
        validator=r'^(\d+)$'
    ),
]

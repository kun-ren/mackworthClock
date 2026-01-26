import enum

class SessionType(enum.Enum):
    PRACTICE = 'practice'
    FORMAL = 'formal'

FLICKER_OFFSET = 4

class Triggers(enum.Enum):
    ONSET = 1
    TARGET_TRIAL_NO_FLICKER = 2
    SUCCESS_RESPONSE_NO_FLICKER = 3    #offset = 5
    FAILED_RESPONSE_NO_FLICKER = 4 #  if no response is recevied within the response time, a mark will be insert into event stream after RT
    MISTAKEN_RESPONSE_NO_FLICKER = 5
    NONE_TARGET_TRIAL_NO_FLICKER = 6
    TARGET_TRIAL_FLICKER = 7
    SUCCESS_RESPONSE_FLICKER = 8
    FAILED_RESPONSE_FLICKER = 9
    MISTAKEN_RESPONSE_FLICKER = 10
    NONE_TARGET_TRIAL_FLICKER = 11
    END = 12
    MISTAKING_RESPONSE = 13
    RSEO_START = 14
    RSEO_END = 15
    RSEC_START = 16
    RSEC_END = 17


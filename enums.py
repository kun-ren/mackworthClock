import enum

class SessionType(enum.Enum):
    PRACTICE = 'practice'
    FORMAL = 'formal'

FLICKER_OFFSET = 4

class Triggers(enum.Enum):
    ONSET = 1
    TARGET_TRIAL_NO_FLICKER = 2
    SUCCESS_RESPONSE_NO_FLICKER = 3    #offset = 4
    FAILED_RESPONSE_NO_FLICKER = 4 #  if no response is recevied within the response time, a mark will be insert into event stream after RT
    NONE_TARGET_TRIAL_NO_FLICKER = 5
    TARGET_TRIAL_FLICKER = 6
    SUCCESS_RESPONSE_FLICKER = 7
    FAILED_RESPONSE_FLICKER = 8
    NONE_TARGET_TRIAL_FLICKER = 9
    END = 10
    MISTAKING_RESPONSE=11
    RSEO_START =12
    RSEO_END = 13
    RSEC_START = 14
    RSEC_END = 15


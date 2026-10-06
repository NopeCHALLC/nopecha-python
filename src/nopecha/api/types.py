import typing
from enum import IntEnum


class ErrorCode(IntEnum):
    Unknown = 9
    InvalidRequest = 10
    Ratelimited = 11
    BannedIp = 12
    NoJob = 13
    IncompleteJob = 14
    InvalidKey = 15
    NoCredit = 16
    UpdateRequired = 17
    UnavailableFeature = 18


class JobQueuedResponse(typing.TypedDict):
    data: str


class ErrorResponse(typing.TypedDict):
    error: typing.Union[ErrorCode, int]
    message: str


class Proxy(typing.TypedDict):
    type: typing.Literal["http", "https", "socks4", "socks5"]
    host: str
    port: int
    login: typing.Optional[str]
    password: typing.Optional[str]


class ImageRecognitionRequest(typing.TypedDict):
    type: typing.Literal["funcaptcha", "recaptcha"]
    task: str
    image_data: typing.List[str]


class TextCaptchaRecognitionRequest(typing.TypedDict):
    type: typing.Literal["textcaptcha"]
    image_data: typing.Tuple[str]


class AudioRecognitionRequest(typing.TypedDict):
    type: typing.Literal["awscaptcha"]
    audio_data: typing.Tuple[str]


RecognitionRequest = typing.Union[
    ImageRecognitionRequest,
    TextCaptchaRecognitionRequest,
    AudioRecognitionRequest,
]


class ImageRecognitionResponse(typing.TypedDict):
    data: typing.List[str]


RecognitionResponse = typing.Union[ImageRecognitionResponse,]


class GeneralTokenRequest(typing.TypedDict):
    type: typing.Literal["recaptcha2", "recaptcha3"]
    sitekey: str
    url: str
    enterprise: typing.Optional[bool]  # only for recaptcha
    data: typing.Optional[typing.Dict[str, typing.Any]]
    proxy: typing.Optional[Proxy]
    useragent: typing.Optional[str]


class TurnstileTokenRequest(typing.TypedDict):
    type: typing.Literal["turnstile"]
    sitekey: str
    url: str
    data: typing.Optional[typing.Dict[str, typing.Any]]
    proxy: typing.Optional[Proxy]
    useragent: typing.Optional[str]


TokenRequest = typing.Union[GeneralTokenRequest, TurnstileTokenRequest]


class TokenResponse(typing.TypedDict):
    data: str


class StatusResponse(typing.TypedDict):
    plan: str
    status: str
    credit: int
    quota: int
    duration: int
    lastreset: int
    ttl: int
    subscribed: bool
    current_period_start: int
    current_period_end: int

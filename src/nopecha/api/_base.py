import typing
from abc import ABC, abstractmethod
from logging import getLogger
from urllib.parse import urlencode

from .types import (
    AudioRecognitionRequest,
    ErrorCode,
    GeneralTokenRequest,
    HCaptchaAreaSelectRequest,
    HCaptchaAreaSelectResponse,
    HCaptchaMultipleChoiceRequest,
    ImageRecognitionRequest,
    Proxy,
    RecognitionRequest,
    RecognitionResponse,
    StatusResponse,
    TokenRequest,
    TokenResponse,
    TurnstileTokenRequest,
)
from ._throttle import exp_throttle, linear_throttle, sleeper, async_sleeper
from ._validate import validate_image
from ._key import is_free_key

logger = getLogger(__name__)
_error_message = (
    "Server did not {} after {} attempts. "
    "Server may be overloaded (https://nopecha.com/discord). "
    "Alternatively try increasing the {}_max_attempts parameter (or set to 0 for unlimited retries)."
)


class UniformResponse(typing.NamedTuple):
    status_code: int
    body: typing.Optional[dict]


class APIClientMixin:
    key: str
    post_max_attempts: int = 10
    get_max_attempts: int = 120
    host = "https://api.nopecha.com"

    def __init__(
        self, key: str, *, post_max_attempts: int = 10, get_max_attempts: int = 120
    ):
        self.key = key
        self.post_max_attempts = post_max_attempts
        self.get_max_attempts = get_max_attempts

    def _should_retry(self, response: UniformResponse) -> bool:
        # automatically retry on 5xx errors and 429
        if response.status_code >= 500:
            logger.debug(f"Server returned {response.status_code}, retrying")
            return True
        elif response.status_code == 429:
            logger.debug("Server is ratelimiting us, retrying")
            return True
        elif response.body is None:
            logger.debug("Server returned no data, retrying")
            return True
        return False

    def _get_headers(self) -> dict:
        return {
            "user-agent": self._get_useragent(),
            "authorization": f"Bearer {self.key}",
        }

    def _get_useragent(self) -> str:
        try:
            import pkg_resources

            package_version = pkg_resources.get_distribution("nopecha").version
        except:
            package_version = "unknown"

        try:
            import platform

            system = platform.platform()
            python_version = (
                platform.python_implementation() + "/" + platform.python_version()
            )
        except:
            system = "unknown"
            python_version = "unknown"

        signficant_dependencies = ["requests", "httpx", "aiohttp"]
        versions = []
        for dependency in signficant_dependencies:
            try:
                import pkg_resources

                version = pkg_resources.get_distribution(dependency).version
                versions.append(f"{dependency}/{version}")
            except:
                pass

        return f"NopeCHA-Python/{package_version} ({python_version}; {type(self).__name__}; {system}) {' '.join(versions)}".strip()


class APIClient(ABC, APIClientMixin):
    @abstractmethod
    def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        raise NotImplementedError

    def _request(self, endpoint: str, body: typing.Any) -> typing.Any:
        body["key"] = self.key
        job_id = self._request_post(endpoint, body)

        get_endpoint = endpoint + "?" + urlencode({"key": self.key, "id": job_id})
        return self._request_get(get_endpoint)

    def _request_post(self, endpoint: str, body: typing.Any) -> str:
        for _ in sleeper(exp_throttle(max_attempts=self.post_max_attempts)):
            job_request = self._request_raw("POST", endpoint, body)
            if self._should_retry(job_request):
                continue
            assert job_request.body is not None
            if "data" in job_request.body:
                return job_request.body["data"]
            elif "error" in job_request.body:
                raise RuntimeError(f"Server returned error: {job_request.body}")

        raise RuntimeError(
            _error_message.format("accept job", self.post_max_attempts, "post")
        )

    def _request_get(self, endpoint: str) -> typing.Any:
        for _ in sleeper(linear_throttle(max_attempts=self.get_max_attempts)):
            job_request = self._request_raw("GET", endpoint)
            if self._should_retry(job_request):
                continue
            assert job_request.body is not None
            if "data" in job_request.body:
                return job_request.body
            elif "error" in job_request.body:
                if job_request.body["error"] == ErrorCode.IncompleteJob:
                    continue
                raise RuntimeError(f"Server returned error: {job_request.body}")

        raise RuntimeError(
            _error_message.format("solve job", self.get_max_attempts, "get")
        )

    def recognize_raw(self, body: RecognitionRequest) -> RecognitionResponse:
        return self._request(f"{self.host}/", body)

    def solve_raw(self, body: TokenRequest) -> TokenResponse:
        # this is also enforced server-side, so dont even bother (youll get loads of 502s)
        if is_free_key(self.key):
            raise RuntimeError(
                "You are using a free key, which cannot use the token API."
            )
        return self._request(f"{self.host}/token/", body)

    def status(self) -> StatusResponse:
        url = f"{self.host}/status/?" + urlencode({"key": self.key})
        for _ in sleeper(linear_throttle(max_attempts=self.get_max_attempts)):
            status_request = self._request_raw("GET", url)
            if self._should_retry(status_request):
                continue
            assert status_request.body is not None
            return typing.cast(StatusResponse, status_request.body)

        raise RuntimeError(
            _error_message.format("get status", self.get_max_attempts, "get")
        )

    def recognize_hcaptcha(
        self, task: str, images: typing.List[str]
    ) -> RecognitionResponse:
        for image in images:
            validate_image(image)

        body: ImageRecognitionRequest = {
            "type": "hcaptcha",
            "task": task,
            "image_data": images,
        }
        return typing.cast(RecognitionResponse, self.recognize_raw(body))

    def recognize_hcaptcha_area_select(
        self,
        task: str,
        image: str,
        image_examples: typing.Optional[typing.List[str]] = None,
    ) -> HCaptchaAreaSelectResponse:
        validate_image(image)
        if image_examples is not None:
            for image_example in image_examples:
                validate_image(image_example)

        body: HCaptchaAreaSelectRequest = {
            "type": "hcaptcha_area_select",
            "task": task,
            "image_data": (image,),
            "image_examples": image_examples,
        }
        return typing.cast(HCaptchaAreaSelectResponse, self.recognize_raw(body))

    def recognize_hcaptcha_multiple_choice(
        self,
        task: str,
        image: str,
        choices: typing.List[str],
        image_choices: typing.Optional[typing.List[str]] = None,
    ) -> HCaptchaMultipleChoiceRequest:
        validate_image(image)
        if image_choices is not None:
            for image_choice in image_choices:
                validate_image(image_choice)

        body: HCaptchaMultipleChoiceRequest = {
            "type": "hcaptcha_multiple_choice",
            "task": task,
            "image_data": (image,),
            "choices": choices,
            "image_choices": image_choices,
        }
        return typing.cast(HCaptchaMultipleChoiceRequest, self.recognize_raw(body))

    def recognize_recaptcha(
        self, task: str, images: typing.List[str]
    ) -> RecognitionResponse:
        for image in images:
            validate_image(image)

        if not 9 >= len(images) >= 1:
            raise ValueError("recaptcha requires 1-9 images")

        body: ImageRecognitionRequest = {
            "type": "recaptcha",
            "task": task,
            "image_data": images,
        }
        return typing.cast(RecognitionResponse, self.recognize_raw(body))

    def recognize_funcaptcha(self, task: str, image: str) -> RecognitionResponse:
        validate_image(image)

        body: ImageRecognitionRequest = {
            "type": "funcaptcha",
            "task": task,
            "image_data": [image],
        }
        return typing.cast(RecognitionResponse, self.recognize_raw(body))

    def recognize_awscaptcha(self, audio: str) -> RecognitionResponse:
        validate_image(audio)

        body: AudioRecognitionRequest = {
            "type": "awscaptcha",
            "audio_data": (audio,),
        }
        return typing.cast(RecognitionResponse, self.recognize_raw(body))

    def solve_hcaptcha(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        rqdata: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and rqdata is not None:
            logger.warning(
                "you are setting rqdata for non-enterprise hcaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise hcaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "hcaptcha",
            "sitekey": sitekey,
            "url": url,
            "enterprise": enterprise,
            "proxy": proxy,
            "data": {"rqdata": rqdata} if rqdata is not None else None,
            "useragent": useragent,
        }
        return typing.cast(TokenResponse, self.solve_raw(body))

    def solve_recaptcha_v2(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        sdata: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and sdata is not None:
            logger.warning(
                "you are setting sdata for non-enterprise recaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise recaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "recaptcha2",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {"s": sdata} if sdata is not None else None,
            "enterprise": enterprise,
        }
        return typing.cast(TokenResponse, self.solve_raw(body))

    def solve_recaptcha_v3(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and action is not None:
            logger.warning(
                "you are setting action for non-enterprise recaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise recaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "recaptcha3",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {"action": action} if action is not None else None,
            "enterprise": enterprise,
        }
        return typing.cast(TokenResponse, self.solve_raw(body))

    def solve_cloudflare_turnstile(
        self,
        sitekey: str,
        url: str,
        *,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
        cdata: typing.Optional[str] = None,
        challenge_page_data: typing.Optional[str] = None,
    ) -> TokenResponse:
        body: TurnstileTokenRequest = {
            "type": "turnstile",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {
                "action": action,
                "cdata": cdata,
                "chlPageData": challenge_page_data,
            },
        }
        return typing.cast(TokenResponse, self.solve_raw(body))


class AsyncAPIClient(APIClientMixin):
    async def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        raise NotImplementedError

    async def _request(self, endpoint: str, body: typing.Any) -> typing.Any:
        body["key"] = self.key
        job_id = await self._request_post(endpoint, body)

        get_endpoint = endpoint + "?" + urlencode({"key": self.key, "id": job_id})
        return await self._request_get(get_endpoint)

    async def _request_post(self, endpoint: str, body: typing.Any) -> str:
        async for _ in async_sleeper(exp_throttle(max_attempts=self.post_max_attempts)):
            job_request = await self._request_raw("POST", endpoint, body)
            if self._should_retry(job_request):
                continue
            assert job_request.body is not None
            if "data" in job_request.body:
                return job_request.body["data"]
            elif "error" in job_request.body:
                raise RuntimeError(f"Server returned error: {job_request.body}")

        raise RuntimeError(
            _error_message.format("accept job", self.post_max_attempts, "post")
        )

    async def _request_get(self, endpoint: str) -> typing.Any:
        async for _ in async_sleeper(
            linear_throttle(max_attempts=self.get_max_attempts)
        ):
            job_request = await self._request_raw("GET", endpoint)
            if self._should_retry(job_request):
                continue
            assert job_request.body is not None
            if "data" in job_request.body:
                return job_request.body
            elif "error" in job_request.body:
                if job_request.body["error"] == ErrorCode.IncompleteJob:
                    continue
                raise RuntimeError(f"Server returned error: {job_request.body}")

        raise RuntimeError(
            _error_message.format("solve job", self.get_max_attempts, "get")
        )

    async def recognize_raw(self, body: RecognitionRequest) -> RecognitionResponse:
        return await self._request("/", body)

    async def solve_raw(self, body: TokenRequest) -> TokenResponse:
        return await self._request("/token/", body)

    async def status(self) -> StatusResponse:
        url = f"{self.host}/status/?" + urlencode({"key": self.key})
        async for _ in async_sleeper(
            linear_throttle(max_attempts=self.get_max_attempts)
        ):
            status_request = await self._request_raw("GET", url)
            if self._should_retry(status_request):
                continue
            assert status_request.body is not None
            return typing.cast(StatusResponse, status_request.body)

        raise RuntimeError(
            _error_message.format("get status", self.get_max_attempts, "get")
        )

    async def recognize_hcaptcha(
        self, task: str, images: typing.List[str]
    ) -> RecognitionResponse:
        for image in images:
            validate_image(image)

        body: ImageRecognitionRequest = {
            "type": "hcaptcha",
            "task": task,
            "image_data": images,
        }
        return typing.cast(RecognitionResponse, await self.recognize_raw(body))

    async def recognize_hcaptcha_area_select(
        self,
        task: str,
        image: str,
        image_examples: typing.Optional[typing.List[str]] = None,
    ) -> HCaptchaAreaSelectResponse:
        validate_image(image)
        if image_examples is not None:
            for image_example in image_examples:
                validate_image(image_example)

        body: HCaptchaAreaSelectRequest = {
            "type": "hcaptcha_area_select",
            "task": task,
            "image_data": (image,),
            "image_examples": image_examples,
        }
        return typing.cast(HCaptchaAreaSelectResponse, await self.recognize_raw(body))

    async def recognize_hcaptcha_multiple_choice(
        self,
        task: str,
        image: str,
        choices: typing.List[str],
        image_choices: typing.Optional[typing.List[str]] = None,
    ) -> HCaptchaMultipleChoiceRequest:
        validate_image(image)
        if image_choices is not None:
            for image_choice in image_choices:
                validate_image(image_choice)

        body: HCaptchaMultipleChoiceRequest = {
            "type": "hcaptcha_multiple_choice",
            "task": task,
            "image_data": (image,),
            "choices": choices,
            "image_choices": image_choices,
        }
        return typing.cast(
            HCaptchaMultipleChoiceRequest, await self.recognize_raw(body)
        )

    async def recognize_recaptcha(
        self, task: str, images: typing.List[str]
    ) -> RecognitionResponse:
        for image in images:
            validate_image(image)

        if not 9 >= len(images) >= 1:
            raise ValueError("recaptcha requires 1-9 images")

        body: ImageRecognitionRequest = {
            "type": "recaptcha",
            "task": task,
            "image_data": images,
        }
        return typing.cast(RecognitionResponse, await self.recognize_raw(body))

    async def recognize_funcaptcha(self, task: str, image: str) -> RecognitionResponse:
        validate_image(image)

        body: ImageRecognitionRequest = {
            "type": "funcaptcha",
            "task": task,
            "image_data": [image],
        }
        return typing.cast(RecognitionResponse, await self.recognize_raw(body))

    async def recognize_awscaptcha(self, audio: str) -> RecognitionResponse:
        validate_image(audio)

        body: AudioRecognitionRequest = {
            "type": "awscaptcha",
            "audio_data": (audio,),
        }
        return typing.cast(RecognitionResponse, await self.recognize_raw(body))

    async def solve_hcaptcha(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        rqdata: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and rqdata is not None:
            logger.warning(
                "you are setting rqdata for non-enterprise hcaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise hcaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "hcaptcha",
            "sitekey": sitekey,
            "url": url,
            "enterprise": enterprise,
            "proxy": proxy,
            "data": {"rqdata": rqdata} if rqdata is not None else None,
            "useragent": useragent,
        }
        return typing.cast(TokenResponse, await self.solve_raw(body))

    async def solve_recaptcha_v2(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        sdata: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and sdata is not None:
            logger.warning(
                "you are setting sdata for non-enterprise recaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise recaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "recaptcha2",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {"s": sdata} if sdata is not None else None,
            "enterprise": enterprise,
        }
        return typing.cast(TokenResponse, await self.solve_raw(body))

    async def solve_recaptcha_v3(
        self,
        sitekey: str,
        url: str,
        *,
        enterprise: bool = False,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
    ) -> TokenResponse:
        if not enterprise and action is not None:
            logger.warning(
                "you are setting action for non-enterprise recaptcha, this makes no sense"
            )
        elif enterprise and proxy is None:
            logger.warning(
                "you are using enterprise recaptcha without a proxy, probably won't work"
            )

        body: GeneralTokenRequest = {
            "type": "recaptcha3",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {"action": action} if action is not None else None,
            "enterprise": enterprise,
        }
        return typing.cast(TokenResponse, await self.solve_raw(body))

    async def solve_cloudflare_turnstile(
        self,
        sitekey: str,
        url: str,
        *,
        proxy: typing.Optional[Proxy] = None,
        useragent: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
        cdata: typing.Optional[str] = None,
        challenge_page_data: typing.Optional[str] = None,
    ) -> TokenResponse:
        body: TurnstileTokenRequest = {
            "type": "turnstile",
            "sitekey": sitekey,
            "url": url,
            "proxy": proxy,
            "useragent": useragent,
            "data": {
                "action": action,
                "cdata": cdata,
                "chlPageData": challenge_page_data,
            },
        }
        return typing.cast(TokenResponse, await self.solve_raw(body))

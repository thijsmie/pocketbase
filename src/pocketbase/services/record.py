from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast
from urllib.parse import quote

from pocketbase.models.dtos import AuthMethods, AuthResult, Oauth2Payload, OTPResult, Record
from pocketbase.models.options import CommonOptions, SendOptions
from pocketbase.services.base import Service
from pocketbase.services.crud import CrudService
from pocketbase.services.realtime import Callback
from pocketbase.utils.types import BodyDict

if TYPE_CHECKING:
    from pocketbase.client import PocketBase, PocketBaseInners


class RecordService(CrudService[Record]):
    """Service for managing records in a specific collection.

    This service provides CRUD operations and real-time subscriptions for records
    in a particular collection. It inherits all standard CRUD methods from CrudService.
    """

    __base_sub_path__: str

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners", collection: str) -> None:
        super().__init__(pocketbase, inners)
        self._collection = collection
        self.__base_sub_path__ = f"/api/collections/{quote(collection)}/records"
        self._auth = RecordAuthService(pocketbase, inners, collection)

    @property
    def auth(self) -> "RecordAuthService":
        """Access authentication operations for this collection.

        Returns:
            RecordAuthService for authentication operations like login, signup, etc.
        """
        return self._auth

    async def subscribe(
        self,
        callback: Callback,
        record_id: str,
        options: CommonOptions | None = None,
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribes to a specific record identified by `record_id`.

        Args:
            callback: Function to be called when updates occur for the record.
            record_id: The ID of the record to subscribe to.
            options: Additional options for the subscription (optional).

        Raises:
            ValueError: If `record_id` is empty or None.
        """

        if not record_id:
            raise ValueError("Invalid record_id: cannot be empty or None")

        return await self._pb.realtime.subscribe(f"{self._collection}/{record_id}", callback, options)

    async def subscribe_all(
        self, callback: Callback, options: CommonOptions | None = None
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribes to all records in the current collection.

        Args:
            callback: Function to be called when updates occur for any record.
            options: Additional options for the subscription (optional).

        Returns:
            A function to unsubscribe from all records.
        """

        return await self._pb.realtime.subscribe(self._collection, callback, options)


class RecordAuthService(Service):
    """Service for handling authentication operations on a specific collection.

    This service provides methods for user authentication including password-based login,
    OAuth2, OTP (One-Time Password), and other authentication features.
    """

    def __init__(self, pocketbase: "PocketBase", inners: "PocketBaseInners", collection: str) -> None:
        super().__init__(pocketbase, inners)
        self.__base_sub_path__ = f"/api/collections/{quote(collection)}"

    async def methods(self, options: CommonOptions | None = None) -> AuthMethods:
        """Get available authentication methods for this collection.

        Args:
            options: Additional request parameters

        Returns:
            AuthMethods object containing available authentication options

        Example:
            ```python
            methods = await pb.collection('users').auth.methods()
            if methods['password']['enabled']:
                # Password authentication is available
                pass
            ```
        """
        send_options: SendOptions = {"method": "GET"}

        if options:
            send_options.update(options)

        return await self._send("/auth-methods", send_options)  # type: ignore

    async def with_password(
        self,
        username_or_email: str,
        password: str,
        identity_field: str | None = None,
        options: CommonOptions | None = None,
    ) -> AuthResult:
        """Authenticate using username/email and password.

        Args:
            username_or_email: The username or email address
            password: The password
            identity_field: Specific identity field to use (optional)
            options: Additional request parameters

        Returns:
            AuthResult containing the authentication token and user record

        Example:
            ```python
            result = await pb.collection('users').auth.with_password(
                'user@example.com',
                'password123'
            )
            print(f"Token: {result['token']}")
            print(f"User: {result['record']}")
            ```
        """
        body = {"identity": username_or_email, "password": password}

        if identity_field:
            body["identityField"] = identity_field

        send_options: SendOptions = {"method": "POST", "body": body}  # type: ignore

        if options:
            send_options.update(options)

        result: AuthResult = await self._send("/auth-with-password", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

    async def with_oauth2(self, payload: Oauth2Payload, options: CommonOptions | None = None) -> AuthResult:
        """Authenticate using OAuth2.

        Args:
            payload: OAuth2 authentication payload containing provider, code, etc.
            options: Additional request parameters

        Returns:
            AuthResult containing the authentication token and user record

        Example:
            ```python
            result = await pb.collection('users').auth.with_oauth2({
                'provider': 'google',
                'code': 'oauth_code',
                'codeVerifier': 'verifier',
                'redirectUrl': 'http://localhost:3000/callback'
            })
            ```
        """
        send_options: SendOptions = {"method": "POST", "body": cast(BodyDict, payload)}

        if options:
            send_options.update(options)

        result: AuthResult = await self._send("/auth-with-oauth2", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

    async def with_otp(self, otp_id: str, password: str, options: CommonOptions | None = None) -> AuthResult:
        """Authenticate using a One-Time Password (OTP).

        Args:
            otp_id: The OTP identifier received from request_otp()
            password: The OTP password/code
            options: Additional request parameters

        Returns:
            AuthResult containing the authentication token and user record

        Example:
            ```python
            # First request an OTP
            otp_result = await pb.collection('users').auth.request_otp('user@example.com')

            # Then authenticate with the OTP
            result = await pb.collection('users').auth.with_otp(
                otp_result['otpId'],
                'received_otp_code'
            )
            ```
        """
        send_options: SendOptions = {"method": "POST", "body": {"otpId": otp_id, "password": password}}

        if options:
            send_options.update(options)

        result: AuthResult = await self._send("/auth-with-otp", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

    async def request_otp(self, email: str, option: CommonOptions | None = None) -> OTPResult:
        """Request a One-Time Password to be sent to the specified email.

        Args:
            email: The email address to send the OTP to
            option: Additional request parameters

        Returns:
            OTPResult containing the OTP identifier

        Example:
            ```python
            otp_result = await pb.collection('users').auth.request_otp('user@example.com')
            # User will receive an email with OTP code
            # Use otp_result['otpId'] with with_otp() method
            ```
        """
        send_options: SendOptions = {"method": "POST", "body": {"email": email}}

        if option:
            send_options.update(option)

        return await self._send("/request-otp", send_options)  # type: ignore

    async def refresh(self, options: CommonOptions | None = None) -> AuthResult:
        """Refresh the current authentication token.

        Args:
            options: Additional request parameters

        Returns:
            AuthResult with the new authentication token and user record

        Example:
            ```python
            # Refresh the current session
            result = await pb.collection('users').auth.refresh()
            ```
        """
        send_options: SendOptions = {"method": "POST"}

        if options:
            send_options.update(options)

        self._in.auth.set_is_refreshing(True)
        result: AuthResult = await self._send("/auth-refresh", send_options)  # type: ignore
        self._in.auth.set_is_refreshing(False)
        self._in.auth.set_user(result)
        return result

    async def impersonate(
        self, record_id: str, duration: int | None = None, options: CommonOptions | None = None
    ) -> AuthResult:
        """Impersonate another user (admin only).

        Args:
            record_id: The ID of the user record to impersonate
            duration: How long the impersonation should last (in seconds)
            options: Additional request parameters

        Returns:
            AuthResult with the impersonation token and target user record

        Note:
            This method is typically only available to admin users.

        Example:
            ```python
            # Impersonate user for 1 hour (3600 seconds)
            result = await pb.collection('users').auth.impersonate(
                'USER_ID',
                duration=3600
            )
            ```
        """
        body = {}

        if duration:
            body["duration"] = duration

        send_options: SendOptions = {"method": "POST", "body": body}  # type: ignore

        if options:
            send_options.update(options)

        result: AuthResult = await self._send(f"/impersonate/{record_id}", send_options)  # type: ignore
        self._in.auth.set_user(result)
        return result

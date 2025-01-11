from typing import Optional
from netmiko import ConnectHandler, BaseConnection
from fastapi import HTTPException

class SessionManager:
    def __init__(self):
        self._session: Optional[BaseConnection] = None

    def create_session(self, host: str, username: str, password: str) -> BaseConnection:
        if self._session:
            self.close_session()
        
        self._session = ConnectHandler(
            host=host,
            username=username,
            password=password,
            device_type="cisco_ios"
        )
        return self._session

    def get_session(self) -> BaseConnection:
        if not self._session:
            raise HTTPException(status_code=400, detail="No active session")
        return self._session

    def close_session(self) -> None:
        if self._session:
            try:
                # Don't send logout command as it can hang
                self._session.disconnect()
            finally:
                self._session = None

from datetime import UTC, datetime, timedelta
import logging
from typing import Dict

import jwt
from fastapi import HTTPException
from siwe.siwe import ISO8601Datetime, SiweMessage, VersionEnum, generate_nonce
from web3 import Web3

from backend_api.backend.config import Settings
from backend_api.schemas.auth import VerifyModel

logger = logging.getLogger(__name__)


def create_jwt(data: dict, settings: Settings) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_access_token_expires_in
    )  # expires in 1 minute

    token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return token


def decode_jwt(token: str, settings: Settings) -> Dict:
    try:
        decoded = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_siwe_message(wallet_address: str, statement="Sign in with Ethereum") -> SiweMessage:
    return SiweMessage(
        domain="example.com",
        address=Web3.to_checksum_address(wallet_address),
        statement=statement,
        uri="http://localhost:8000",
        version=VersionEnum.one,
        chain_id=1,
        nonce=generate_nonce(),
        issued_at=ISO8601Datetime.from_datetime(datetime.now(UTC)),
    )


def verify_siwe_message(message: SiweMessage, signature: str) -> VerifyModel:
    try:
        message.verify(signature)
    except Exception as error:
        logger.error(f"Error verify siwe message: {error=}")
        raise HTTPException(status_code=400, detail=str(error))
    return VerifyModel(message=message, address=message.address, signature=signature)

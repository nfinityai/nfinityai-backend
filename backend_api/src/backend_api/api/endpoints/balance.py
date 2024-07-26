from fastapi import APIRouter, Depends

from backend_api.models.balance import CurrencyToPayEnum
from backend_api.schemas.balance import (
    BalanceModel as BalanceModelSchema,
)
from backend_api.schemas.balance import (
    BalancePopupCurrenciesListModel,
)
from backend_api.schemas.balance import (
    BalancePopupModel as BalancePopupModelSchema,
)
from backend_api.schemas.balance import (
    CreateBalancePopupModel as CreateBalancePopupSchema,
)
from backend_api.schemas.users import User as UserSchema
from backend_api.services.auth import get_current_user
from backend_api.services.balance import BalanceService, get_balance_service
from backend_api.services.balance_popup import (
    BalancePopupService,
    get_balance_popup_service,
)
from backend_api.services.coingecko import (
    CoingeckoService,
    TokenToCoinIDEnum,
    get_coingecko_service,
)

router = APIRouter()


@router.get("/balance", response_model=BalanceModelSchema)
async def get_balance(
    current_user: UserSchema = Depends(get_current_user),
    balance_service: BalanceService = Depends(get_balance_service),
):
    balance = await balance_service.get_balance(current_user.id)
    return BalanceModelSchema(**balance.model_dump())


@router.post(
    "/balance/popup/currencies", response_model=BalancePopupCurrenciesListModel
)
async def get_available_currencies_to_pay(
    current_user: UserSchema = Depends(get_current_user),
):
    return BalancePopupCurrenciesListModel()


@router.post("/balance/popup", response_model=BalancePopupModelSchema)
async def create_popup_balance(
    coin_id: CurrencyToPayEnum,
    current_user: UserSchema = Depends(get_current_user),
    balance_popup_service: BalancePopupService = Depends(get_balance_popup_service),
    coingecko_service: CoingeckoService = Depends(get_coingecko_service),
):
    price_usd = await coingecko_service.get_price(
        TokenToCoinIDEnum.from_currency_to_pay(coin_id)
    )

    return await balance_popup_service.create_balance_popup(
        CreateBalancePopupSchema(
            user_id=current_user.id, price_usd=price_usd, currency_to_pay=coin_id
        )
    )


@router.get("/balance/popup/{balance_popup_id}", response_model=BalancePopupModelSchema)
async def get_popup_balance(
    balance_popup_id: int,
    current_user: UserSchema = Depends(get_current_user),
    balance_popup_service: BalancePopupService = Depends(get_balance_popup_service),
):
    return await balance_popup_service.get_balance_popup(balance_popup_id)

from datetime import datetime
from backend_api.backend.session import get_session
from backend_api.models.balance import TransactionType
from backend_api.services.balance_popup import BalancePopupService
from backend_api.backend.tasks import scheduler
from backend_api.schemas.balance import (
    CreateTransaction as CreateTransactionSchema,
    UpdateBalancePopupModel as UpdateBalancePopupSchema,
)
from backend_api.services.web3 import get_web3_event_service
from backend_api.services.users import get_user_service
from backend_api.services.transaction import get_transaction_service
from backend_api.services.balance import get_balance_service


@scheduler.scheduled_job("interval", seconds=30, next_run_time=datetime.now())
async def update_balance_popups():
    async for session in get_session():
        service = BalancePopupService(session)
        event_service = await get_web3_event_service(session)
        user_service = await get_user_service(session)
        balance_service = await get_balance_service(session)
        transaction_service = await get_transaction_service(session, balance_service)
        balance_popups = await service.get_unfinished_balance_popups()
        events = await event_service.get_deposit_events_since(datetime.now())

        for popup in balance_popups:
            user = await user_service.get_user_by_id(popup.user_id)
            for event in events:
                if event.data['from'] == user.wallet_address:
                    updated = await service.update_balance_popup(
                        UpdateBalancePopupSchema(**popup.model_dump())
                    )
                    await transaction_service.create_transaction(
                        CreateTransactionSchema(
                            user_id=user.id,
                            amount=event.data['amount'] * updated.price_usd,
                            type=TransactionType.CREDIT,
                        )
                    )

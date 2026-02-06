from pydantic import BaseModel


class StatisticsResponseDto(BaseModel):
    total_transactions: int
    platform_profit: int

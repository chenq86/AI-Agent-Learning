from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random, os
from utils.logger_handler import logger
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
rag = RagSummarizeService()
user_ids=["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010"]
month_arr=["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12"]
external_data = {}

@tool(description="Retrieve reference material from the vector store")
def rag_summarize(query:str) -> str:
    return rag.rag_summarize(query)


@tool(description="Get weather for the specified city and return it as a message string")
def get_weather(city:str) ->str:
    return f"Weather in {city}: sunny, temperature 26 degrees Celsius, humidity 50%, southerly wind force 1, AQI 21, and a very low chance of rain over the next 6 hours"


@tool(description="Get the user city name as a plain string")
def get_user_location() -> str:
    return random.choice(["Shenzhen","Hefei","Hangzhou"])


@tool(description="Get the user ID as a plain string")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="Get the current month as a plain string")
def get_current_month() -> str:
    return random.choice(month_arr)


def generate_external_data():
    """
    {
        "user_id": {
            "month" : {"Profile": xxx, "Efficiency": xxx, ...}
            "month" : {"Profile": xxx, "Efficiency": xxx, ...}
            "month" : {"Profile": xxx, "Efficiency": xxx, ...}
            ...
        }
        "user_id": {
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    ...
        }
        "user_id": {
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    "month" : {"Profile": xxx, "Efficiency": xxx, ...}
                    ...
        }
        ...
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"External data file {external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")
                user_id: str = arr[0].replace('"',"")
                feature: str = arr[1].replace('"',"")
                efficiency: str = arr[2].replace('"',"")
                consumables: str = arr[3].replace('"',"")
                comparison: str = arr[4].replace('"',"")
                time: str = arr[5].replace('"',"")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "Profile": feature,
                    "Efficiency": efficiency,
                    "Consumables": consumables,
                    "Comparison": comparison,
                }


        
@tool(description="Get user usage records for the specified month from an external system as a plain string; return an empty string if no record is found")
def fetch_external_data(user_id: str, month:str) -> str:
    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]No usage record found for user {user_id} in {month}")


@tool(description="No input arguments or return value; trigger middleware to inject report-generation context for subsequent prompt switching")
def fill_context_for_report():
    return "fill_context_for_report has been called"


if __name__ == "__main__":
    print(fetch_external_data("1001", "2025-01"))
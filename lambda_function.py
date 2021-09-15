import os
import pytz
import boto3
import requests
from dateutil import parser

def lambda_handler(event, context):
    # 変数
    ACCOUNTID = os.environ['accountId']
    WEBHOOK_URL = os.environ['WebhookURL']
    BUDGET_NAME = os.environ['budgetName']

    # AWSから料金や予算を取得
    client = boto3.client('budgets')
    responce = client.describe_budget(
            AccountId=ACCOUNTID,
            BudgetName=BUDGET_NAME
    )

    # 代入
    budget = float(responce['Budget']['BudgetLimit']['Amount']) # 予算
    cost = float(responce['Budget']['CalculatedSpend']['ActualSpend']['Amount']) # 現在までの料金
    predicted = float(responce['Budget']['CalculatedSpend']['ForecastedSpend']['Amount']) # 今月の予測料金

    # 日付
    utcdate = responce['ResponseMetadata']['HTTPHeaders']['date']
    jst_date = parser.parse(utcdate).astimezone(pytz.timezone('Asia/Tokyo'))
    date = jst_date.strftime('%Y-%m-%d')

    # 投稿メッセージ
    content = (
        f"元ソルジャー1stのクラウドだ。\n"
        f"あんたがAWSをいくら使おうと興味ないね\n"
        f"[日付]: {date}\n"
        f"[料金]: ${cost}\n"
        f"[予測]: ${predicted}\n"
        f"[予算]: ${budget}"
    )

    # Webhook
    data = {
        'username': 'クラウド',
        "avatar_url": 'https://www.jp.square-enix.com/ffvii_remake/fankit/_img/snsicon/ICON_CLOUD.jpg',
        "content": content
    }

    # POST
    try:
        requests.post(WEBHOOK_URL, data)
    except requests.exceptions.RequestException as e:
        print(e)

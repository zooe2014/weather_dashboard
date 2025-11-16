import requests
import streamlit as st
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------
# 1️⃣ API 設定
# ----------------------------
API_KEY = "CWA-73BC5918-9700-4C6F-9AEE-53D9D5093EA2"
URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"

# ----------------------------
# 2️⃣ 下載資料（修正 SSL 問題）
# ----------------------------
params = {"Authorization": API_KEY}

session = requests.Session()
session.verify = False
session.trust_env = False
response = session.get(URL, params=params)

data = response.json()


stations = data["records"]["Station"]  # 取測站資料

# ----------------------------
# 3️⃣ 建立 DataFrame 並展開巢狀欄位
# ----------------------------
df = pd.DataFrame(stations)

# 展開巢狀欄位
df['CountyName'] = df['GeoInfo'].apply(lambda x: x['CountyName'])
df['StationName'] = df['StationName']
df['DateTime'] = df['ObsTime'].apply(lambda x: x['DateTime'])
df['AirTemperature'] = df['WeatherElement'].apply(lambda x: float(x['AirTemperature']))
df['RelativeHumidity'] = df['WeatherElement'].apply(lambda x: float(x['RelativeHumidity']))
df['Precipitation'] = df['WeatherElement'].apply(lambda x: float(x['Now']['Precipitation']))

# 轉換時間型別
df['DateTime'] = pd.to_datetime(df['DateTime'])

# 保留必要欄位
df = df[['StationName', 'CountyName', 'AirTemperature', 'RelativeHumidity', 'Precipitation', 'DateTime']]

# ----------------------------
# 4️⃣ Streamlit Dashboard
# ----------------------------
st.set_page_config(page_title="🌤️ 台灣即時天氣 Dashboard", layout="wide")
st.title("🌤️ 台灣即時天氣監控 Dashboard")

# 下拉選縣市 + 全部縣市選項
counties = df["CountyName"].unique().tolist()
counties.sort()  # 按字母排序
counties.insert(0, "全部縣市")  # 第一個選項是全部
selected_county = st.selectbox("選擇縣市", counties)

# 篩選資料
if selected_county == "全部縣市":
    filtered_df = df
else:
    filtered_df = df[df["CountyName"] == selected_county]

# 顯示表格
st.subheader(f"{selected_county} 測站天氣資訊")
st.dataframe(filtered_df)

# 氣溫折線圖
st.subheader(f"{selected_county} 氣溫分布 (°C)")
st.line_chart(filtered_df.set_index('DateTime')['AirTemperature'])

# 濕度折線圖
st.subheader(f"{selected_county} 濕度分布 (%)")
st.line_chart(filtered_df.set_index('DateTime')['RelativeHumidity'])

# 降雨量折線圖
st.subheader(f"{selected_county} 降雨量分布 (mm)")
st.line_chart(filtered_df.set_index('DateTime')['Precipitation'])

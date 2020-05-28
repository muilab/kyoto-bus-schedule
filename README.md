# 京都市バス時刻表データ

京都市オープンデータポータルサイト掲載の[京都市バスの時刻表データセット](https://data.city.kyoto.lg.jp/node/14553)からデータをパースし、JSON形式に整形したデータと、パーサーのスクリプトです。  

バス停留所情報の一部は[京都市バス時刻表](http://www2.city.kyoto.lg.jp/kotsu/busdia/bustime.htm)ページのデータを参照しています。  

## 使い方

[京都市バスの時刻表データセット](https://data.city.kyoto.lg.jp/node/14553)より最新のデータセットのzipをダウンロード、展開し、展開したフォルダーのパスを指定してスクリプトを実行してください。

```bash
python kyoto_bus_schedule_parser.py <フォルダーパス>
```

実行後、```./json```フォルダー内にパースされたJSONファイルが生成されます。

### 整形データ

* busstop.json : バス停留所情報のデータです  

停留所の情報と、停留所から発車する各系統別の路線情報が含まれます。  
系統別情報の```id```プロパティを参照し、時刻表データのJSONを参照してください。  

```json
[
    {
        "id": "003",
        "name": "河原町三条",
        "yomi": "かわらまちさんじょう",
        "en": "Kawaramachi Sanjo",
        "address": {
            "name": "京都府京都市中京区大黒町",
            "lat": "35.0087710000",
            "lng": "135.7690040000",
            "elev": "40.4"
        },
        "lines": [ // 路線系統情報
            {
                "id": "003311",
                "line": "3号系統",
                "name": "河原町三条",
                "destination": "四条河原町･松尾橋",
                "destination_en": "Matsuobashi Via Shijo Kawaramachi"
            },
```

このデータでは、河原町三条停留所から四条河原町・松尾橋行きの時刻表データは```003311.json```を参照すれば良いことがわかります。  

* 時刻表データ

各停留所から発車する系統別の時刻データです。  
平日（weekday)、土曜日（saturday）、休日（holiday）ごとに発車時刻が含まれます。  
特別な注釈はそれぞれの```note```プロパティを参照してください。  

```json
{
    "id": "003311",
    "bkmk": "kmtb-b003311",
    "name": "河原町三条 発 3号系統  四条河原町･松尾橋行き",
    "busstop": "河原町三条",
    "line": "3号系統",
    "destination": "四条河原町･松尾橋行き",
    "notes": {
        "()": "京都外大前までです。For kyoto Gaidai-mae"
    },
    "weekday": [
        {
            "t": "07:03",
            "note": " "
        },
        {
            "t": "07:09",
            "note": " "
        },
        {
            "t": "09:18",
            "note": "京都外大前までです。For kyoto Gaidai-mae"
        },
    "saturday" : [
        // ...
    ],
    "holiday" : [
        // ...
    ]
}
```

## 環境

* python3.7.6

## ライセンス

* [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)  
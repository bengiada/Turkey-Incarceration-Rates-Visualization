from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

#An interactive Dash app of maps and plots of every crime type in Turkish cities

app = Dash(__name__)
server = app.server

#from https://github.com/alpers/Turkey-Maps-GeoJSON
with open('tr-cities-utf8.json', 'r', encoding="utf-8-sig") as f:
    distros_dict = json.load(f)

df = pd.read_csv("2007-2020TurkeyCrimeData.csv")

crimes = { #all of the crime types
    "All (Toplam)": "All",
    "Murder (Öldürme)": "1. (Öldürme)",
    "Injury (Yaralama)": "2. (Yaralama)",
    "Sexual Crimes (Cinsel Suçlar)": "3. (Cinsel Suçlar)",
    "Threatening (Tehdit)": "4. (Tehdit)",
    "Depriving someone of their liberty (Kişiyi Hürriyetinden Yoksun Kılma)": "5. (Kişiyi Hürriyetinden Yoksun Kılma)",
    "Defamation (Hakaret)": "7. (Hakaret)",
    "Theft (Hırsızlık)": "8. (Hırsızlık)",
    "Looting (Yağma/Gasp)": "9. (Yağma (Gasp))",
    "Property Damage (Mala Zarar Verme)": "10. (Mala Zarar Verme)",
    "Traffic Offenses (Trafik Suçları)": "12. (Trafik Suçları)",
    "Maltreatment (Kötü Muamele)": "14. (Kötü Muamele)",
    "Forgery (Sahtecilik)": "18. (Sahtecilik)",
    "Fraud (Dolandırıcılık)": "26. (Dolandırıcılık)",
    "Opposition to Check Laws (Çek Kanunlarına Muhalefet)": "30. (Çek Kanunlarına Muhalefet)",
    "Manufacturing and Trading Drugs and/or Stimulants (Uyuşturucu Veya Uyarıcı Madde İmal Ve Ticareti)": "31. (Uyuşturucu Veya Uyarıcı Madde İmal Ve Ticareti)",
    "Using and Buying Drugs and/or Stimulants (Uyuşturucu  Veya Uyarıcı Madde Kullanma, Satın Alma)": "32. (Uyuşturucu  Veya Uyarıcı Madde Kullanma, Satın Alma)",
    "Embezzlement (Zimmet)": "33. (Zimmet)",
    "Bribery (Rüşvet)": "34. (Rüşvet)",
    "Smuggling (Kaçakçılık)": "35. (Kaçakçılık)",
    "Forest Crimes (Orman Suçları)": "36. (Orman Suçları)",
    "Crimes Related to Firearms and Knives (Ateşli Silahlar Ve Bıçaklar İle İlgili Suçlar)": "37. (Ateşli Silahlar Ve Bıçaklar İle İlgili Suçlar)",
    "Opposition to Foreclosure and Bankruptcy (İcra İflas Kanununa Muhalefet)": "38. (İcra İflas Kanununa Muhalefet)",
    "Opposition to Military Penal Code (Askeri Ceza Kanununa Muhalefet)": "39. (Askeri Ceza Kanununa Muhalefet)",
    "Resisting an Officer (Görevi Yaptırmamak İçin Direnme)": "40. (Görevi Yaptırmamak İçin Direnme)",
    "Violation of the Family Protection Measures (Ailenin Korunması Tedbirine Aykırılık)": "41. (Ailenin Korunması Tedbirine Aykırılık)",
    "Other (Diğer)": "98. (Diğer)",
    "Unknown (Bilinmeyen)": "99. (Bilinmeyen)",
}


app.layout = html.Div(
    [
        html.Br(),
        dcc.RadioItems(
            ['Maps', 'Plots'],
            'Maps',
            id='demo-radioitems0',
            inline=True
        ),
        html.Br(),
        dcc.Dropdown(list(crimes.keys()), 'All (Toplam)', id='demo-dropdown', placeholder="Select a crime type",
                     clearable=False),
        html.Br(),
        dcc.RadioItems(
            ['Rate per 100,000', 'Total', 'National Difference'],
            'Rate per 100,000',
            id='demo-radioitems',
            inline=True
        ),
        html.Br(),
        html.Div(id='dd-output-container'),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input('demo-radioitems0', 'value'),
    Input('demo-dropdown', 'value'),
    Input('demo-radioitems', 'value')
)

def display_graph(type,value, type_value):
    crimetype = "Suç türü:" + crimes[value]
    ab = df.loc[df['Crime Type'] == crimetype]
    color = "Viridis"

    if type == 'Maps':
        lowerlimit = 0

        if value == "All (Toplam)":
            if type_value == 'Total':
                parameter = 'data'
                title_value = "Total Incarcerations"
            elif type_value == 'Rate per 100,000':
                parameter = "Rate per 100,000"
                title_value = "Rate of Incarcerations per 100,000"
            else:
                parameter = 'Difference'
                title_value = "National Difference"
                lowerlimit = ab[parameter].mean() - 5 * ab[parameter].std()
                color = "PRGn"
        else:
            if type_value == 'Total':
                parameter = 'data'
                title_value = 'Total ' + value + " Incarcerations"
            elif type_value == 'Rate per 100,000':
                parameter = "Rate per 100,000"
                title_value = "Rate of " + value + " Incarcerations per 100,000"
            else:
                parameter = 'Difference'
                title_value = "National Difference of " + value
                lowerlimit = ab[parameter].mean() - 5 * ab[parameter].std()
                color = "PRGn"

        fig = px.choropleth_mapbox(ab, geojson=distros_dict, locations='id', color=parameter,
                                   color_continuous_scale=color,
                                   range_color=(lowerlimit, ab[parameter].mean() + 5 * ab[parameter].std()),
                                   mapbox_style="carto-positron",
                                   zoom=5.1, center={"lat": 38.9597594, "lon": 34.9249653},
                                   opacity=0.6,
                                   hover_data=["Name", "data", "Population", "Rate per 100,000"],
                                   animation_frame='year',
                                   title=title_value,
                                   labels={"Rate per 100,000": 'Rate', "data": "Total", "year": "Year"}
                                   )
        fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0}, width=1300, height=600, )
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 600

    else:
        if type_value == 'Total':
            type_value = 'data'
        elif type_value == "National Difference":
            type_value = "Difference"


        fig = px.line(ab, x="year", y=type_value, color="Crime Type", line_group="id", hover_data=["Name",'Population','data'])
        fig.update_layout(showlegend=False,) #title = "Rate over Time")

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

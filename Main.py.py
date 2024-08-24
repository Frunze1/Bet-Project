import requests
import json
import pandas as pd

class Bookmaker:
    def __init__(self, title):
        self.title = title

class Game(Bookmaker):
    def __init__(self, title=None, home_team=None, away_team=None, home_odds=None, away_odds=None, draw_odds=None, total_over=None, total_under=None, spreads_home=None, spreads_away=None):
        super().__init__(title)
        self.home_team = home_team
        self.away_team = away_team
        self.home_odds = home_odds
        self.away_odds = away_odds
        self.draw_odds = draw_odds
        self.total_over = total_over
        self.total_under = total_under
        self.spreads_home = spreads_home
        self.spreads_away = spreads_away

    # Метод для получения данных через открытый API с использованием ключей
    def get_data_from_api(self, url, api_keys):
        for api_key in api_keys:
            response = requests.get(url.format(api_key=api_key))
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ключ {api_key} недействителен. Пробуем следующий ключ...")
        print("Запросы закончились.")
        return None

    # Метод для получения всех видов спорта на сайте
    def get_sports(self, api_keys):
        url = "https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
        return self.get_data_from_api(url, api_keys)

    # Метод для получения матчей для данного вида спорта
    def get_events(self, api_keys, sport_key):
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={{api_key}}&regions=eu&markets=h2h,spreads,totals&dateFormat=iso&oddsFormat=decimal"
        return self.get_data_from_api(url, api_keys)

    # Метод для получения данных из JSON файла и создания списка матчей
    def process_events_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)

        matches = []
        for match in data:
            home_team = match['home_team']
            away_team = match['away_team']
            
            for bookmaker in match['bookmakers']:
                bookmaker_name = bookmaker['title']
                home_odds = None
                away_odds = None
                draw_odds = None
                total_over = None
                total_under = None
                spreads_home = None
                spreads_away = None 

                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                home_odds = outcome['price']
                            elif outcome['name'] == away_team:
                                away_odds = outcome['price']
                            elif outcome['name'] == 'Draw':
                                draw_odds = outcome['price']
                    elif market['key'] == 'spreads':
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                spreads_home = outcome['price']
                            elif outcome['name'] == away_team:
                                spreads_away = outcome['price']
                    elif market['key'] == 'totals':
                        for outcome in market['outcomes']:
                            if outcome['name'] == "Over":
                                total_over = outcome['price']
                            elif outcome['name'] == "Under":
                                total_under = outcome['price']
                
                matches.append(Game(bookmaker_name, home_team, away_team, home_odds, away_odds, draw_odds, total_over, total_under , spreads_home, spreads_away))
        
        return matches


    # Метод для сохранения данных в файл Excel
    def save_to_excel(self, matches, filename):
        data = []
        
        for match in matches:
            match_data = [
                match.home_team,
                match.away_team,
                match.title,
                match.home_odds,
                match.away_odds,
                match.draw_odds,
                match.total_over,
                match.total_under,
                match.spreads_home,
                match.spreads_away
            ]
            data.append(match_data)
        
        df = pd.DataFrame(data, columns=['Home Team', 'Away Team', 'Bookmaker', 'Home Winner', 'Away Winner', 'Draw', 'Total_OVER', 'Total_UNDER', 'Spreads_home', 'Spreads_away'])
        
        df.to_excel(filename, index=False)
        print(f"Данные успешно сохранены в файл {filename}")



api_keys = [
    "ac85ca67c2dedeb83cea877bdea770ed", "ccaed2355683bb06e9b5bf27cce61a09",
    "92ab2f52aba04b62b0a08b4607b8b0c7", "b56f8b94e93fbdfa3e75b3b85318df0c",
    "896af85c9074852ac3e25ce3d952c410", "d33ad133095f3c9dfa05dba6b00be426",
    "82e9e31ba8c12bd928b2fafd587e13c8", "07aa20ca8fa1c1deef262e53a7fb3479",
    "987181f91fe04f73324448ffe3b68549", "509088de56ffb51d618ac99601ab741d",
    "61c7fb851d9b8c85b274c668a22260fb", "7f213f2948aa42e114bc90378e0038bc",
    "73931da2f3283819e2f980efdc34a629", "bae40ba662b1962623f39105073439f9",
    "a14fbc16df4fc3e66c3e4e3ccee8ba81", "e40eaca749a1502a0233cf3c20d53af6",
    "8f8ee34c9bdb791ecb219b3cc6e8802f", "2e7e69dfd1d359aa3484d74c09e45fe5",
    "d560afe77ba940ca75c6be843466fdf3", "4ea275c91c664e374dd81364f1a611fc",
    "83fdd43c8d723bdc8380dc0218cc2139", "e274d85cda643710e7afbefb80e82492",
]
sport_key = "soccer_epl"

match_instance = Game()

sports = match_instance.get_sports(api_keys)
if sports:
    with open("sports.json", "w") as file:
        json.dump(sports, file, indent=4)
    print("Данные успешно сохранены в файл sports.json")

events = match_instance.get_events(api_keys, sport_key)
if events:
    with open("events.json", "w") as file:
        json.dump(events, file, indent=4)
    print("Данные успешно сохранены в файл events.json")

matches = match_instance.process_events_json("events.json")
match_instance.save_to_excel(matches, 'C:/Users/arfru/OneDrive/Desktop/Project/matches_odds.xlsx')



# Загружаем Excel файл
file_matches = 'C:/Users/arfru/OneDrive/Desktop/Project/matches_odds.xlsx'
df = pd.read_excel(file_matches)

# Ищем максимальные коэффициенты для каждого исхода для каждого матча
max_odds = df.groupby(['Home Team', 'Away Team']).agg(Max_Home_Winner=('Home Winner', 'max',), Max_Away_Winner=('Away Winner', 'max'), Max_Draw=('Draw', 'max'))
max_odds = max_odds.reset_index()
# Добавляем колонку, чтобы проверить, возможно ли получить прибыль, сделав ставки на все три исхода
max_odds['Profit_Possible'] = (1 / max_odds['Max_Home_Winner'] + 1 / max_odds['Max_Away_Winner'] + 1 / max_odds['Max_Draw']) < 1

# Задаем общую сумму ставки на все исходы напрмер 1000 рублей. От того сколько мы выберем матчей будет зависить сколько мы от этого получим 
total_stake = 1000

# Рассчитываем размеры ставок на каждый исход матча
max_odds['Stake_Home'] = (1 / max_odds['Max_Home_Winner'] / (1 / max_odds['Max_Home_Winner'] + 1 / max_odds['Max_Away_Winner'] + 1 / max_odds['Max_Draw'])) * total_stake
max_odds['Stake_Away'] = (1 / max_odds['Max_Away_Winner'] / (1 / max_odds['Max_Home_Winner'] + 1 / max_odds['Max_Away_Winner'] + 1 / max_odds['Max_Draw'])) * total_stake
max_odds['Stake_Draw'] = (1 / max_odds['Max_Draw'] / (1 / max_odds['Max_Home_Winner'] + 1 / max_odds['Max_Away_Winner'] + 1 / max_odds['Max_Draw'])) * total_stake

# Сохранить результаты в новый Excel файл
max_odds.to_excel('C:/Users/arfru/OneDrive/Desktop/Project/max_odds_results.xlsx', index=False)
print("Данные успешно сохранены в файл 'C:/Users/arfru/OneDrive/Desktop/Project/max_odds_results.xlsx' ")




















































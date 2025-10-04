import requests
from bs4 import BeautifulSoup
import csv

def get_player_details(soup):
    try:
        p_name = soup.select_one("h1:nth-child(4)").text if soup.select_one("h1:nth-child(4)") else ""
        p_name_kana = soup.select_one("rt").text.replace("（", "").replace("）", "").replace("'", "''") if soup.select_one("rt") else p_name
        p_position = soup.select_one(".bb-profile__position").text
        p_uni_number = soup.select_one(".bb-profile__number").text

        others = [item.text for item in soup.select(".bb-profile__text")]

        birth_place, born_date, height, weight, blood_type, pitch_bat = others[:6]
        pitching = pitch_bat[0]
        batting = pitch_bat[3]

        born_date = born_date.split("（")[0].replace("年", "/").replace("月", "/").replace("日", "")
        height = height.replace("cm", "")
        weight = weight.replace("kg", "")

        profile_titles = [item.text for item in soup.select(".bb-profile__title")]

        draft_year, draft_rank, pro_year, career_, major_title = "", "", "", "", ""
        if len(profile_titles) == 10:
            draft_year, draft_rank = others[6].split("年")
            draft_rank = draft_rank.replace("（", "").replace("）", "")
            pro_year, career_, major_title = others[7:10]
        elif len(profile_titles) == 9 and profile_titles[7] == "プロ通算年":
            draft_year, draft_rank = others[6].split("年")
            draft_rank = draft_rank.replace("（", "").replace("）", "")
            pro_year, career_ = others[7:9]
        elif len(profile_titles) == 9 and profile_titles[7] == "経歴":
            pro_year, career_, major_title = others[6:9]
        elif len(profile_titles) == 8:
            pro_year, career_ = others[6:8]

        koshien_f = 1 if "（甲）" in career_ else 0

        draft_year = draft_year.strip()
        draft_rank = draft_rank.strip()
        pro_year = pro_year.replace("年", "").strip()
        career_ = career_.strip()
        major_title = major_title.strip()

        return p_name, p_name_kana, p_position, p_uni_number, birth_place, born_date, height, weight, blood_type, pitching, batting, draft_year, draft_rank, pro_year, career_, koshien_f, major_title
    except Exception as e:
        print(f"Error extracting player details: {e}")
        return ["" for _ in range(17)]  # Return empty strings for each field on failure

def get_player_data(player_id):
    try:
        player_url = f"https://baseball.yahoo.co.jp/npb/player/{player_id}/top"
        res = requests.get(player_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        return [player_id] + list(get_player_details(soup))
    except requests.RequestException as e:
        print(f"Network error for player ID {player_id}: {e}")
        return None  # Return None if there's an error

def save_to_csv(player_data_list):
    try:
        filename = "players_data.csv"
        with open(filename, "w", newline="", encoding='utf8') as f:
            writer = csv.writer(f)
            # Write the header
            writer.writerow([
                "Player ID", "Name", "Name (Kana)", "Position", "Uniform Number", "Birth Place", "Born Date",
                "Height", "Weight", "Blood Type", "Pitching", "Batting", "Draft Year", "Draft Rank",
                "Pro Year", "Career", "Koshien Flag", "Major Title"
            ])
            # Write player data
            for player_data in player_data_list:
                writer.writerow(player_data)
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

if __name__ == "__main__":
    player_data_list = []
    for player_id in range(980000, 2500000):
        player_data = get_player_data(player_id)
        if player_data and player_data[1]:  # Check if player_data is valid and has a name
            print(f"Adding data for player ID {player_id}")
            player_data_list.append(player_data)

    if player_data_list:
        save_to_csv(player_data_list)
        print("Data saved to players_data.csv")
    else:
        print("No valid player data found.")

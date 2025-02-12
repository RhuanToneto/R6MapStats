import os
import asyncio
import json
import sys
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from siegeapi import Auth
from typing import Optional

CACHE_DIRECTORY = "cache"
CREDENTIALS_CACHE_PATH = os.path.join(CACHE_DIRECTORY, "credentials.json")
PLAYERS_CACHE_PATH = os.path.join(CACHE_DIRECTORY, "players.json")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_key():
    return os.urandom(32)

def save_key(key):
    with open(os.path.join(CACHE_DIRECTORY, "secret.key"), "wb") as key_file:
        key_file.write(key)

def load_key():
    with open(os.path.join(CACHE_DIRECTORY, "secret.key"), "rb") as key_file:
        return key_file.read()

if not os.path.exists(os.path.join(CACHE_DIRECTORY, "secret.key")):
    key = generate_key()
    os.makedirs(CACHE_DIRECTORY, exist_ok=True)
    save_key(key)
else:
    key = load_key()

def encrypt(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt(data, key):
    data = base64.b64decode(data)
    iv = data[:16]
    encrypted_data = data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data

async def save_credentials(email, password):
    credentials = {"email": email, "password": password}
    encrypted_credentials = encrypt(json.dumps(credentials).encode(), key)
    with open(CREDENTIALS_CACHE_PATH, "w") as file:
        file.write(encrypted_credentials)

async def load_credentials():
    if os.path.exists(CREDENTIALS_CACHE_PATH):
        with open(CREDENTIALS_CACHE_PATH, "r") as file:
            encrypted_credentials = file.read()
            decrypted_credentials = decrypt(encrypted_credentials, key)
            return json.loads(decrypted_credentials)
    return None

async def login():
    while True:
        try:
            print()
            credentials = await load_credentials()
            if credentials:
                while True:
                    use_cached_login = input("Deseja usar o mesmo login anterior? (s/n): ").lower()
                    if use_cached_login in ['s', 'n']:
                        break
                    else:
                        print("Opção inválida. Digite 's' para sim ou 'n' para não.\n")
                if use_cached_login == 's':
                    email = credentials["email"]
                    password = credentials["password"]
                else:
                    email = input("Digite seu e-mail: ")
                    password = input("Digite sua senha: ")
            else:
                email = input("Digite seu e-mail: ")
                password = input("Digite sua senha: ")

            auth = Auth(email, password)
            await auth.connect()
            print("Login feito com sucesso!\n")

            save_credentials_task = save_credentials(email, password)
            await save_credentials_task

            return auth
        except Exception as e:
            if "Email format is invalid" in str(e):
                print("\nFalha no login: Email não encontrado!\n")
            elif "Invalid credentials" in str(e):
                print("\nFalha no login: Senha incorreta!\n")
            else:
                print(f"\nFalha no login: {e}\n")

async def save_players(players):
    with open(PLAYERS_CACHE_PATH, "w") as file:
        for player in players:
            file.write(json.dumps(player) + '\n')

async def load_players():
    players = []
    try:
        if os.path.exists(PLAYERS_CACHE_PATH):
            with open(PLAYERS_CACHE_PATH, "r") as file:
                for line in file:
                    players.append(json.loads(line.strip()))
    except Exception as e:
        print(f"Erro ao carregar jogadores: {e}")
    return players

async def get_player_name(auth: Auth, uid: str) -> Optional[str]:
    try:
        player = await auth.get_player(uid=uid)
        return player.name
    except Exception as e:
        if "HTTP 404" in str(e):
            return None
        print(f"Erro ao obter o nome do jogador: {e}")
        return None

def print_squad(players):
    print("\nQUAIS JOGADORES ESTÃO NO ESQUADRÃO?")
    for i, player in enumerate(players, 1):
        print(f"{i:2d} - {player['name']}")
    print()

async def get_selected_players(players):
    while True:
        try:
            print_squad(players)
            input_str = input("Insira os números dos jogadores separados por espaço: ").strip()
            if not input_str:
                print("Você precisa selecionar pelo menos um jogador.")
                continue
            selected_indices = [int(index) - 1 for index in input_str.split()]
            selected_players = []
            for index in selected_indices:
                if 0 <= index < len(players):
                    selected_players.append(players[index]["name"])
                else:
                    raise ValueError("Erro! Verifique os números dos jogadores disponíveis e tente novamente.\n")
            return selected_players
        except ValueError as ve:
            print(f"Erro: {ve}")

def print_selected_squad(selected_players, start_date, end_date, start_date_formatted, end_date_formatted):
    print()
    print(f"ESQUADRÃO: {', '.join(selected_players)}")
    
    date_difference = relativedelta(end_date, start_date)
    
    months = date_difference.months
    
    period_text = f"Período: {months} {'Mês' if months == 1 else 'Meses'}"

    print(f"INTERVALO DE DADOS: {start_date_formatted} - {end_date_formatted} ({period_text})")
    print()

def print_map_stats(sorted_map_stats):
    print("\nTAXAS DE VITÓRIAS:")
    for map_name, stats in sorted_map_stats:
        map_name = map_name.replace(" V2", "")  
        if stats["total_matches"] == 0:
            print(f"{map_name:>20} : Dados Insuficientes")
        elif stats["total_wins"] == 0 or stats["total_wins"] == stats["total_matches"]:
            print(f"{map_name:>20} : Dados Imprecisos")
        else:
            win_rate = (stats["total_wins"] / stats["total_matches"]) * 100
            win_rate_str = f"{win_rate:.1f}%"
            print(f"{map_name:>20} : {win_rate_str}")
    print()

def print_additional_stats(map_stats):
    print("\nESTATÍSTICAS ATAQUE E DEFESA:")
    map_kd = {}
    for map_name, stats in map_stats.items():
        map_name = map_name.replace(" V2", "") 
        if stats['death'] != 0: 
            kd = round(stats['kills'] / stats['death'], 2)
            rounds_with_kost = float(f"{stats['rounds_with_kost']:.1f}")
            if rounds_with_kost.is_integer():
                rounds_with_kost = int(rounds_with_kost)
            map_kd[map_name] = (kd, rounds_with_kost)
    sorted_maps = sorted(map_kd.items(), key=lambda x: x[1][0], reverse=True)
    for map_name, (kd, rounds_with_kost) in sorted_maps:
        print(f"{map_name:>20} : KD: {kd:.2f}, KOST: {rounds_with_kost}%")
    print()

def print_attacker_stats(map_stats_attacker):
    print("\nESTATÍSTICAS ATAQUE:")
    map_kd = {}
    for map_name, stats in map_stats_attacker.items():
        map_name = map_name.replace(" V2", "") 
        if stats['death'] != 0: 
            kd = round(stats['kills'] / stats['death'], 2)
            rounds_with_kost = float(f"{stats['rounds_with_kost']:.1f}")
            if rounds_with_kost.is_integer():
                rounds_with_kost = int(rounds_with_kost)
            map_kd[map_name] = (kd, rounds_with_kost)
    sorted_maps = sorted(map_kd.items(), key=lambda x: x[1][0], reverse=True)
    for map_name, (kd, rounds_with_kost) in sorted_maps:
        print(f"{map_name:>20} : KD: {kd:.2f}, KOST: {rounds_with_kost}%")
    print()

def print_defender_stats(map_stats_defender):
    print("\nESTATÍSTICAS DEFESA:")
    map_kd = {}
    for map_name, stats in map_stats_defender.items():
        map_name = map_name.replace(" V2", "") 
        if stats['death'] != 0: 
            kd = round(stats['kills'] / stats['death'], 2)
            rounds_with_kost = float(f"{stats['rounds_with_kost']:.1f}")
            if rounds_with_kost.is_integer():
                rounds_with_kost = int(rounds_with_kost)
            map_kd[map_name] = (kd, rounds_with_kost)
    sorted_maps = sorted(map_kd.items(), key=lambda x: x[1][0], reverse=True)
    for map_name, (kd, rounds_with_kost) in sorted_maps:
        print(f"{map_name:>20} : KD: {kd:.2f}, KOST: {rounds_with_kost}%")
    print()        

def print_rating_stats(map_stats):
    print("\nDESEMPENHO GERAL:")
    
    stat_weights = {
        "rounds_with_an_ace": 25,
        "rounds_with_clutch": 25,
        "rounds_with_multi_kill": 20,
        "kills_per_round": 15,
        "rounds_with_kost": 9,
        "rounds_with_opening_kill": 6
    }

    performances = []

    for map_name, stats in map_stats.items():
        total_performance = 0
        
        for stat_name, value in stats.items():
            if stat_name in stat_weights:
                total_performance += value * stat_weights[stat_name]
        
        performances.append((map_name, total_performance))
    
    performances.sort(key=lambda x: x[1], reverse=True)

    max_score = max(performances, key=lambda x: x[1])[1]
    min_score = min(performances, key=lambda x: x[1])[1]

    for map_name, score in performances:
        normalized_score = ((score - min_score) / (max_score - min_score)) * 100
        map_name = map_name.replace(" V2", "")
        print(f"{map_name:>20} : {normalized_score:.1f}")

async def main():
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)

    auth = await login()
    players = await load_players()
    if players:
        print("Jogadores carregados:", ", ".join(player["name"] for player in players))  

    try:
        players_loaded = bool(players)  

        while True: # I WAS THERE WHEN RAINBOW BEGAN. I’LL BE THERE WHEN IT ENDS.
            num_players = len(players)
            all_uids = {player["uid"]: player["name"] for player in players}

            if not players_loaded or len(players) == 0:
                print("Não há jogadores carregados. Adicione pelo menos um jogador!\n")
                while True:
                    uid = input("\nInsira o UID de um jogador: ")
                    player_name = await get_player_name(auth, uid)

                    if player_name:
                        print(f"Jogador '{player_name}' encontrado!\n")
                        players.append({"name": player_name, "uid": uid})
                        await save_players(players)
                        
                        while True:  
                            add_more = input("Deseja adicionar mais jogadores? (s/n): ").lower()
                            if add_more in ['s', 'n']:
                                break
                            else:
                                print("Opção inválida. Digite 's' para sim ou 'n' para não.\n")
                        
                        if add_more == 'n':  
                            break
                    else:
                        print("Nenhum jogador encontrado, tente novamente!\n")
            else:
                while True:
                    same_players_option = input("Deseja usar os mesmos jogadores? (s/add/clear): ").lower()
                    if same_players_option in ['s', 'add', 'clear']:
                        break
                    else:
                        print("Opção inválida. Digite 's' para sim, 'add' para adicionar jogadores ou 'clear' para limpar a lista de jogadores.\n")

                if same_players_option == 'add':
                    while True:
                        uid = input("\nInsira o UID de um jogador: ")
                        player_name = await get_player_name(auth, uid)

                        if player_name:
                            if uid in all_uids:
                                print(f"O jogador '{all_uids[uid]}' já tinha sido encontrado anteriormente!\n")
                                add_more = input("Deseja adicionar mais um jogador? (s/n): ")
                                if add_more.lower() != 's':
                                    if num_players == 0:
                                        print("\nVocê precisa adicionar pelo menos um jogador!\n")
                                        continue
                                    break
                            else:
                                print(f"Jogador '{player_name}' encontrado!\n")
                                players.append({"name": player_name, "uid": uid})
                                all_uids[uid] = player_name
                                num_players += 1

                                add_more = input("Deseja adicionar mais um jogador? (s/n): ")
                                if add_more.lower() != 's':
                                    if num_players == 0:
                                        print("\nVocê precisa adicionar pelo menos um jogador!\n")
                                        continue
                                    break
                        else:
                            print("Nenhum jogador encontrado, tente novamente!\n")

                    await save_players(players)
                    players_loaded = True  

                elif same_players_option == 'clear': 
                    players = []
                    await save_players(players)
                    print("Jogadores apagados!\n")
                    continue  

                elif same_players_option == 's':
                    if not players_loaded or len(players) == 0:  
                        print("Não há jogadores carregados. Adicione pelo menos um jogador!\n")
                        continue

            selected_players = await get_selected_players(players)

            while True:
                period_choice = input("\nEscolha o período das estatísticas: 1 Mês, 2 Meses, 3 Meses (1/2/3): ").strip()
                if period_choice in ['1', '2', '3']:
                    print("Processando...", flush=True)
                    break
                else:
                    print("Opção inválida. Escolha entre 1, 2 ou 3.\n")

            months = int(period_choice)
            end_date = datetime.now()  
            start_date = end_date - relativedelta(months=months)  
            
            end_date_str = end_date.strftime("%Y%m%d")
            start_date_str = start_date.strftime("%Y%m%d")

            start_date_obj = datetime.strptime(start_date_str, "%Y%m%d")
            end_date_obj = datetime.strptime(end_date_str, "%Y%m%d")

            start_date_formatted = start_date_obj.strftime("%d/%m/%Y")
            end_date_formatted = end_date_obj.strftime("%d/%m/%Y")

            map_stats = defaultdict(lambda: {
                "total_matches": 0,
                "total_wins": 0,
                "kills": 0,
                "death": 0,
                "rounds_with_kost": 0,
                "rounds_with_an_ace": 0,  
                "rounds_with_multi_kill": 0,
                "rounds_with_clutch": 0,
                "rounds_with_opening_kill": 0,
                "kills_per_round": 0,
            })

            map_stats_attacker = defaultdict(lambda: {"total_matches": 0, "total_wins": 0, "kills": 0, "death": 0, "rounds_with_kost": 0})
            map_stats_defender = defaultdict(lambda: {"total_matches": 0, "total_wins": 0, "kills": 0, "death": 0, "rounds_with_kost": 0})

            for player_name in selected_players:
                player_data = next((p for p in players if p["name"] == player_name), None)
                if player_data:
                    player = await auth.get_player(uid=player_data["uid"])
                    player.set_timespan_dates(start_date_str, end_date_str)

                    await player.load_maps()

                    for map in player.maps.ranked.all:
                        map_stats[map.map_name]["total_matches"] += map.matches_played
                        map_stats[map.map_name]["total_wins"] += map.matches_won
                        map_stats[map.map_name]["kills"] += map.kills
                        map_stats[map.map_name]["death"] += map.death
                        map_stats[map.map_name]["rounds_with_kost"] += map.rounds_with_kost
                        map_stats[map.map_name]["rounds_with_an_ace"] += map.rounds_with_an_ace 
                        map_stats[map.map_name]["rounds_with_multi_kill"] += map.rounds_with_multi_kill
                        map_stats[map.map_name]["rounds_with_clutch"] += map.rounds_with_clutch
                        map_stats[map.map_name]["rounds_with_opening_kill"] += map.rounds_with_opening_kill
                        map_stats[map.map_name]["kills_per_round"] += map.kills_per_round

                    for map in player.maps.ranked.attacker:
                        map_stats_attacker[map.map_name]["total_matches"] += map.matches_played
                        map_stats_attacker[map.map_name]["total_wins"] += map.matches_won
                        map_stats_attacker[map.map_name]["kills"] += map.kills
                        map_stats_attacker[map.map_name]["death"] += map.death
                        map_stats_attacker[map.map_name]["rounds_with_kost"] += map.rounds_with_kost

                    for map in player.maps.ranked.defender:
                        map_stats_defender[map.map_name]["total_matches"] += map.matches_played
                        map_stats_defender[map.map_name]["total_wins"] += map.matches_won
                        map_stats_defender[map.map_name]["kills"] += map.kills
                        map_stats_defender[map.map_name]["death"] += map.death
                        map_stats_defender[map.map_name]["rounds_with_kost"] += map.rounds_with_kost                           

            num_selected_players = len(selected_players)
            for map_name, stats in map_stats.items():       
                for key in stats:
                    stats[key] /= num_selected_players 

            num_selected_players = len(selected_players)
            for map_name, stats in map_stats_attacker.items():       
                for key in stats:
                    stats[key] /= num_selected_players

            num_selected_players = len(selected_players)
            for map_name, stats in map_stats_defender.items():       
                for key in stats:
                    stats[key] /= num_selected_players

            for player_name in selected_players:
                player_data = next((p for p in players if p["name"] == player_name), None)
                if player_data:
                    player = await auth.get_player(uid=player_data["uid"])
                    player.set_timespan_dates(start_date_str, end_date_str)

                    await player.load_maps()

                    for map in player.maps.ranked.all:
                        if hasattr(map, 'matches_played') and hasattr(map, 'matches_won') and hasattr(map, 'kills') and hasattr(map, 'death') and hasattr(map, 'rounds_with_kost'):
                            if map.matches_played == 0 or map.matches_won == 0 or map.matches_won == map.matches_played:
                                map_stats[map.map_name]["total_matches"] -= map.matches_played / num_selected_players
                                map_stats[map.map_name]["total_wins"] -= map.matches_won / num_selected_players
                                map_stats[map.map_name]["kills"] -= map.kills / num_selected_players
                                map_stats[map.map_name]["death"] -= map.death / num_selected_players
                                map_stats[map.map_name]["rounds_with_kost"] -= map.rounds_with_kost / num_selected_players       

                    for map in player.maps.ranked.attacker:
                        if hasattr(map, 'matches_played') and hasattr(map, 'matches_won') and hasattr(map, 'kills') and hasattr(map, 'death') and hasattr(map, 'rounds_with_kost'):
                            if map.matches_played == 0 or map.matches_won == 0 or map.matches_won == map.matches_played:
                                map_stats_attacker[map.map_name]["total_matches"] -= map.matches_played / num_selected_players
                                map_stats_attacker[map.map_name]["total_wins"] -= map.matches_won / num_selected_players
                                map_stats_attacker[map.map_name]["kills"] -= map.kills / num_selected_players
                                map_stats_attacker[map.map_name]["death"] -= map.death / num_selected_players
                                map_stats_attacker[map.map_name]["rounds_with_kost"] -= map.rounds_with_kost / num_selected_players

                    for map in player.maps.ranked.defender:
                        if hasattr(map, 'matches_played') and hasattr(map, 'matches_won') and hasattr(map, 'kills') and hasattr(map, 'death') and hasattr(map, 'rounds_with_kost'):
                            if map.matches_played == 0 or map.matches_won == 0 or map.matches_won == map.matches_played:
                                map_stats_defender[map.map_name]["total_matches"] -= map.matches_played / num_selected_players
                                map_stats_defender[map.map_name]["total_wins"] -= map.matches_won / num_selected_players
                                map_stats_defender[map.map_name]["kills"] -= map.kills / num_selected_players
                                map_stats_defender[map.map_name]["death"] -= map.death / num_selected_players
                                map_stats_defender[map.map_name]["rounds_with_kost"] -= map.rounds_with_kost / num_selected_players                                            

            print_selected_squad(selected_players, start_date, end_date, start_date_formatted, end_date_formatted)

            sorted_map_stats = sorted(map_stats.items(), key=lambda x: (x[1]["total_wins"] / x[1]["total_matches"]) if x[1]["total_matches"] != 0 else 0, reverse=True)      

            print_map_stats(sorted_map_stats)
            
            print_additional_stats(map_stats)
            
            print_attacker_stats(map_stats_attacker)
            
            print_defender_stats(map_stats_defender)

            print_rating_stats(map_stats)

            while True:
                resposta = input("\nDeseja repetir? (s/n): ")
                if resposta.lower() in ['s', 'n']:
                    break
                else:
                    print("Opção inválida. Digite 's' para sim ou 'n' para não.\n")
            if resposta.lower() != 's':
                break

            clear_console()
    finally:
        await auth.close()

    input("Pressione Enter para sair...")  

if __name__ == "__main__":
    asyncio.run(main())


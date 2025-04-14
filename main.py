from final_parser.browser import setup_driver, login_phase
from final_parser.profile_parser import parse_profile
from final_parser.writer import save_single_profile_to_excel

if __name__ == "__main__":
    driver = setup_driver()
    login_phase(driver)

    username = input("Введите username для анализа: ").strip()
    profile_data = parse_profile(driver, username)

    print("\n📋 Данные профиля:")
    for k, v in profile_data.items():
        print(f"{k}: {v}")

    save_single_profile_to_excel(profile_data)

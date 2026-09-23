import os
from database import toggle_verified_by_tag

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("=" * 55)
    print("   CORVOX ADMIN — Управление галочками")
    print("=" * 55)
    print("  Введите @тег пользователя, чтобы выдать/убрать")
    print("  галочку подтверждения.")
    print("")
    print("  Пример:  @dima")
    print("  Выход:   exit  или  q")
    print("=" * 55)
    print()

def main():
    print_header()
    
    while True:
        try:
            user_input = input("@тег > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break
        
        if user_input.lower() in ('exit', 'q', 'quit', ''):
            print("Выход.")
            break
        
        tag = user_input.lstrip('@').strip()
        
        if not tag:
            print("Введите тег (например: @dima)\n")
            continue
        
        name, clean_tag, new_value = toggle_verified_by_tag(tag)
        
        if name is None:
            print(f"Пользователь с тегом @{tag} не найден.\n")
            continue
        
        if new_value == 1:
            print(f"Галочка ВЫДАНА: {name} (@{clean_tag})\n")
        else:
            print(f"Галочка СНЯТА: {name} (@{clean_tag})\n")

if __name__ == '__main__':
    main()
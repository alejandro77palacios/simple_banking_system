import random
import sqlite3


def test_luhn(card_number):
    card_number = [int(num) for num in card_number]
    for i in range(len(card_number)):
        if i % 2 == 0:
            card_number[i] = card_number[i] * 2
    for i in range(len(card_number)):
        if card_number[i] > 9:
            card_number[i] -= 9
    if sum(card_number) % 10 == 0:
        return True
    else:
        return False


def create_card_number():
    random_numbers = [str(random.randint(1, 9)) for _ in range(9)]
    start_card = '400000' + ''.join(random_numbers)
    for checksum in range(10):
        if test_luhn(start_card + str(checksum)):
            card_number = start_card + str(checksum)
            break
    return card_number


def create_pin():
    pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return pin


def create_account(connection, cursor):
    global id_count
    card_number = create_card_number()
    pin = create_pin()
    insert = 'INSERT INTO card VALUES ({}, {}, {}, {})'.format(id_count, card_number, pin, 0)
    cursor.execute(insert)
    connection.commit()
    id_count += 1
    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)
    print("")


def login(card_number, pin, connection, cursor):
    if test_luhn(card_number):
        cursor.execute(f'SELECT * FROM card WHERE number = {card_number}')
        user = cursor.fetchone()
        if len(user) > 0:
            if user[2] == pin:
                print("You have successfully logged in!\n")
                return True
            else:
                print("Wrong card number or PIN!\n")
                client_service(connection, cursor)
        else:
            print("Wrong card number or PIN!\n")
            client_service(connection, cursor)
    else:
        print("Wrong card number or PIN!\n")
        client_service(connection, cursor)


def check_account(card_number,  connection, cursor):
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    choice = int(input())
    if choice == 1:
        balance(card_number, cursor)
        check_account(card_number, connection, cursor)
    if choice == 2:
        add_income(card_number, connection, cursor)
        check_account(card_number, connection, cursor)
    if choice == 3:
        do_transfer(card_number, connection, cursor)
        check_account(card_number, connection, cursor)
    if choice == 4:
        close_account(card_number, connection, cursor)
        check_account(card_number, connection, cursor)
    if choice == 5:
        client_service(connection, cursor)
    if choice == 0:
        print("Bye!")


def balance(card_number, cursor):
    cursor.execute(f'SELECT balance FROM card WHERE number = {card_number}')
    my_balance = cursor.fetchone()[0]
    print("Balance:", my_balance)


def add_income(card_number, connection, cursor):
    extra = int(input("Enter income:\n"))
    query = f'UPDATE card SET balance = balance + {extra} WHERE number = {card_number}'
    cursor.execute(query)
    connection.commit()
    print("Income was added!\n")


def do_transfer(card_number, connection, cursor):
    print("Transfer")
    card_to_transfer = input("Enter card number:\n")
    if not test_luhn(card_to_transfer):
        print("Probably you made a mistake in the card number. Please try again!\n")
        return
    if card_to_transfer == card_number:
        print("You can't transfer money to the same account!\n")
        return
    cursor.execute(f'SELECT * FROM card WHERE number = {card_to_transfer}')
    other_user = cursor.fetchone()
    if other_user is None:
        print("Such a card does not exist.\n")
        return
    money_to_transfer = int(input("Enter how much money you want to transfer:\n"))
    cursor.execute(f'SELECT balance FROM card WHERE number = {card_number}')
    user_balance = cursor.fetchone()[0]
    if money_to_transfer > user_balance:
        print("Not enough money!\n")
        return
    take_money = f'UPDATE card SET balance = balance - {money_to_transfer} WHERE number = {card_number}'
    cursor.execute(take_money)
    connection.commit()
    give_money = f'UPDATE card SET balance = balance + {money_to_transfer} WHERE number = {card_to_transfer}'
    cursor.execute(give_money)
    connection.commit()
    print("Success!\n")


def close_account(card_number, connection, cursor):
    cursor.execute(f'DELETE FROM card WHERE number = {card_number}')
    connection.commit()
    print("The account has been closed!\n")


def client_service(connection, cursor):
    print("1. Create an account", "2. Log into account", "0. Exit", sep="\n")
    option = int(input())
    print()
    if option == 1:
        create_account(connection, cursor)
        client_service(connection, cursor)
    if option == 2:
        card_number = input("Enter your card number:\n")
        pin = input("Enter your PIN:\n")
        if login(card_number, pin, connection, cursor):
            check_account(card_number, connection, cursor)
    if option == 0:
        print("Bye!")


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()
id_count = 0
client_service(conn, cur)

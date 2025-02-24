# import datetime

# print(type(datetime.datetime.today()))
# hej = datetime.datetime(2012, 3, 23, 23, 24, 55)
# print(type(hej))
# hejsan = hej.weekday()

# print(type(hejsan))
# print(hejsan)


# # 2025-02-22 19:42:00.503611
# # 2025-02-22 19:42:05.680587

# txt = 2147000000

# print(format{f(txt))

import random
    # SALARY = "Salary"
    # TRANSFER = "Transfer" ?
    # DEPOSIT_CASH = "Deposit cash"
    
    # ATM_WITHDRAWL = "ATM withdrawal"
    # PAYMENT = "Payment"
    # BANK_WITHDRAWL = "Bank withdrawal"
positiva = ["Salary","Deposit cash", "Salary","Transfer", "Salary","Deposit cash", "Salary","Transfer", "Salary","Deposit cash","Transfer","Transfer", "Salary", "Salary", "Deposit cash", "Deposit cash","Transfer","Salary", "Deposit cash","Salary", "Deposit cash"]

transfer_check = [1600, 1800, 200, 1400, 200, 400, 1200, 400, 4200, 4100, 2000, 4000, 1000, 3000, 2000, 540, 145, 543, 678, 5000, 300 ]


for i in range(len(positiva)):
    if positiva[i] == "Transfer":
        print(f"positive{i+1} +{(transfer_check[i]-transfer_check[i-1])}") if transfer_check[i] > transfer_check[i-1] else print(f"negative{i+1}{(transfer_check[i]-transfer_check[i-1])}")
            
        
            
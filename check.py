from config import TOKEN

print(len(TOKEN))
print( TOKEN.count(":"))
print(TOKEN != TOKEN.strip() or " " in TOKEN)
print(TOKEN.split(":")[0].isdigit())
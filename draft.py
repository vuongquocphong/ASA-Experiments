# golden = []
# with open("demo_golden.txt", "r", encoding="utf-8") as f:
#     data = f.readlines()
#     for i in range(len(data)):
#         data[i] = data[i].strip()
#         first_part = ""
#         second_part = ""
#         for char in data[i]:
#             if char == "\t":
#                 second_part = data[i][data[i].index(char) + 1:]
#                 break
#             first_part += char
#         golden.append((first_part, second_part))

# with open("demo_src_chunks.txt", "w", encoding="utf-8") as f:
#     chunk_size = 30
#     i = 0
#     cur_par = ""
#     for j in range(len(golden)):
#         src, trg = golden[j]
#         chunk_size -= 1
#         cur_par += src + ""
#         if chunk_size <= 0:
#             f.write(F"# {i}\n")
#             f.write(cur_par + "\n")
#             chunk_size = 30
#             i += 1
#             cur_par = ""
#         if i == len(golden) - 1 and cur_par != "":
#             f.write(F"# {i}\n")
#             f.write(cur_par + "\n")

# with open("demo_tgt_chunks.txt", "w", encoding="utf-8") as f:
#     chunk_size = 30
#     i = 0
#     cur_par = ""
#     for j in range(len(golden)):
#         src, trg = golden[j]
#         chunk_size -= 1
#         cur_par += trg + " "
#         if chunk_size <= 0:
#             f.write(F"# {i}\n")
#             f.write(cur_par + "\n")
#             chunk_size = 30
#             i += 1
#             cur_par = ""
#         if i == len(golden) - 1 and cur_par != "":
#             f.write(F"# {i}\n")
#             f.write(cur_par + "\n")
pars = []
with open("test/translation_pars.txt", "r", encoding="utf-8") as f:
    pars = f.readlines()

with open("test/translation_pars_chunked.txt", "w", encoding="utf-8") as f:
    for i in range(len(pars)):
        f.write(f"# {i}\n")
        f.write(pars[i].strip() + "\n")

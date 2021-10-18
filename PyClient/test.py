import win32console

d = {"#05": "05", "#08": "08", "#01": "01"}

for k in sorted(d):
    print(k, d[k])

d = ("abc", 123)
s, n = d
print(s + str(n))

import random
import string


def main():
    gen_3chunks()

    pass


def gen_3chunks():
    with open('tests/inputs/3chunks.txt', 'wt') as f:
        for i  in range(0,4 * 100 * 16):
            rnd = random.choices(string.ascii_uppercase, k=1)
            f.write(rnd[0])

if __name__ == "__main__":
    main()
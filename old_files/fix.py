# read file and edit the line start with 'a' from a NUM NUM NUM to a NUM NUM 0 1 NUM


def fix_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # if the line starts with 'a', split the line with delimiter ' '
    # add '0' and '1' to the end right before the last element
    # join the line back with delimiter ' '
    # write the line back to the file
    with open(file_name, 'w') as file:
        for line in lines:
            if line.startswith('a'):
                line = line.split(' ')
                line.insert(-1, '0')
                line.insert(-1, '1')
                line = ' '.join(line)
            file.write(line)

fix_file('input.txt')
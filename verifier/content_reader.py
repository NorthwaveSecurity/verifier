import re

separator_regex = re.compile(r"^\[(\w+)\]$")


def join_value(value):
    return ''.join(value)


def read_content(content_file):
    content = {}
    current_key = 'output'
    current_value = []
    with open(content_file) as f:
        for line in f:
            match = separator_regex.match(line)
            if match:
                if current_key:
                    # New key encountered, write value to old key
                    content[current_key] = join_value(current_value)
                    current_value = []
                current_key = match.group(1)
                continue
            else:
                current_value.append(line)
    content[current_key] = join_value(current_value)
    return content


if __name__ == "__main__":
    content = read_content("content.txt")
    print(content)

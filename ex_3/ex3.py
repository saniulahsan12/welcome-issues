import json


def csv_to_json_parser(input_file, output_file):

    json_output = []
    csv_file = open(input_file, "r")

    # closures
    def is_blank(str):
        if str and str.strip():
            return False
        return True

    def split_row(input_str):
        return input_str.strip().split(',')
    # ends

    # header value spiltting. First value of the file
    header = split_row(next(csv_file))

    # reading each line of csv
    for row in csv_file:

        if is_blank(row):
            continue

        obj_vals = split_row(row)
        output_dict = {}
        for index in range(len(obj_vals)):
            if not is_blank(obj_vals[index].strip()):
                output_dict[header[index]] = obj_vals[index]
        json_output.append(output_dict)
    csv_file.close()

    # writing json file
    if len(json_output):
        with open(output_file, 'w') as json_file:
            json.dump(json_output, json_file)
        json_file.close()
    return json_output


if __name__ == "__main__":
    print(csv_to_json_parser('input.csv', 'output.json'))

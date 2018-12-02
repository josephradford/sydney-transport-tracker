import csv
import time

def parse_stop_times(data_dir):
    with open(data_dir + '/stop_times.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            line_count += 1
        print(f'Processed {line_count} lines.')


if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    data_dir = "data/20181202"
    parse_stop_times(data_dir)

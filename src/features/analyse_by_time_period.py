import os
from datetime import time, date
import sys
from transform_train_downloads import TransformTrainDownloads


def analyse_by_time_run(start_time, end_time, date_of_analysis):
    transform = TransformTrainDownloads(start_time, end_time, date_of_analysis)
    transform.transform()
    print("Transformed using new class")


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    from_time = time(7, 0, 0)
    to_time = time(9, 0, 0)
    analyse_by_time_run(from_time, to_time, date.today())

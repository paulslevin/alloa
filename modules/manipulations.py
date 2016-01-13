def csv_to_results(csv_file):
    opened_file = open(csv_file, "r")
    count, results = 0, []
    for line in opened_file.readlines():
        results.append([str(count), line.strip()])
        count += 1
    return results

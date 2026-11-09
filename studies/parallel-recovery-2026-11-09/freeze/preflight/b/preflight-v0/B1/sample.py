from sequence import assign_sequences

if __name__ == "__main__":
    events = [("job-7", "orchid"), ("job-8", "maple"), ("job-9", "orchid")]
    for row in assign_sequences(events):
        print(row)

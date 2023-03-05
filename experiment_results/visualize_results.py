import argparse
import csv
import matplotlib.pyplot as plt
from datetime import datetime


def parse_log_file(log_file):
    """
    Parses the internal clock and actual time values from a log file.
    Returns a list of tuples (actual_time, internal_clock).
    """
    print(log_file)
    log_entries = []
    with open(log_file, 'r') as f:
        reader = csv.reader(f, delimiter='-')
        for row in reader:
            actual_time_str = row[0].strip()
            internal_clock = int(row[3].strip())
            actual_time = datetime.strptime(actual_time_str, '%b %d %H:%M:%S')
            log_entries.append((actual_time, internal_clock))
    return log_entries


def plot_log_files(log_files, output_file=None, show_plot=False):
    """
    Plots the internal clock values relative to the actual time values for a list of log files.
    Uses different colors for each log file.
    """

    # extract clock rates form the first file
    legend = []
    with open(log_files[0], 'r') as f:
        legend += f.read().split("\n")
    print(legend)
    colors = ['blue', 'red', 'green', 'orange',
              'purple', 'brown', 'pink', "black"]
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))
    ax1.set_title('Internal Clock vs. Actual Time (scatter)')
    ax2.set_title('Internal Clock vs. Actual Time (line)')

    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_title('Internal Clock vs. Actual Time (line)')
    for i, log_file in enumerate(log_files[1:]):
        log_entries = parse_log_file(log_file)
        actual_times = [entry[0] for entry in log_entries]
        internal_clocks = [entry[1] for entry in log_entries]
        ax1.plot(actual_times, internal_clocks,
                 color=colors[i % len(colors)], label=legend[i])
        ax.plot(actual_times, internal_clocks,
                color=colors[i % len(colors)], label=legend[i])
        ax2.scatter(actual_times, internal_clocks,
                    color=colors[i % len(colors)], label=legend[i])

    ax.legend()
    ax1.legend()
    ax2.legend()
    ax.set_xlabel('Actual Time')
    ax1.set_xlabel('Actual Time')
    ax.set_ylabel('Internal Clock')
    ax2.set_ylabel('Internal Clock')
    if (show_plot):
        plt.show()
    result = ax.get_figure()
    if output_file is not None:
        result.savefig(output_file)
    else:
        result.savefig("result.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot internal clock values from log files.')
    parser.add_argument('log_files', nargs='+', help='List of log file names')
    parser.add_argument('-o', '--output', dest='output_file', default=None,
                        help='Output filename for the plot')
    parser.add_argument('-s', '--show', dest='show_plot', action='store_true',
                        help='Show plot')
    args = parser.parse_args()
    plot_log_files(args.log_files, output_file=args.output_file,
                   show_plot=args.show_plot)

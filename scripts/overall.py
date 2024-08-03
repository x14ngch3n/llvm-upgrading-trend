#!/usr/bin/env python3

import argparse
import shutil
import subprocess as sp
from os import path, makedirs
from matplotlib import pyplot as plt
from enum import Enum


class CompabilityType(Enum):
    Textual = 1
    API = 2
    Semantic = 3


IR_files = [
    # Semantic related files
    ("llvm/include/llvm/IR/Instructions.h", CompabilityType.Semantic),
    ("llvm/include/llvm/IR/InstrTypes.h", CompabilityType.Semantic),
    # API related files
    ("llvm/include/llvm/IR/IRBuilder.h", CompabilityType.API),
    ("llvm/lib/Bitcode/Reader/BitcodeReader.cpp", CompabilityType.API),
    ("llvm/lib/Bitcode/Writer/BitcodeWriter.cpp", CompabilityType.API),
    # Textual related files
    ("llvm/lib/AsmParser/LLParser.cpp", CompabilityType.Textual),
    ("llvm/lib/IR/AsmWriter.cpp", CompabilityType.Textual),
    ("llvm/include/llvm/IR/Instruction.def", CompabilityType.Textual),
]


def plot(compability_type: CompabilityType):
    filenames = [file[0] for file in IR_files if file[1] == compability_type]
    # get x-label
    with open("./data/tags.txt", "r") as f:
        tags = f.read().splitlines()
    x_label = [tag[8:] for tag in tags]
    x = list(range(len(x_label)))
    y = [0] * len(x)
    # read diff results from csv
    for filename in filenames:
        csv_path = path.join("./data", path.basename(filename) + ".csv")
        with open(csv_path, "r") as f:
            lines = f.read().splitlines()
            per_file_changes = [int(line.split(",")[4]) for line in lines]
            y[1:] = [sum(x) for x in zip(y[1:], per_file_changes)]
    # normalize and cumulate the y-axis
    for i in range(len(y) - 1):
        y[i + 1] += y[i]
    y = [y_i / y[-1] * 100 for y_i in y]
    # draw the plot
    plt.figure(figsize=(32, 24))
    plt.plot(x, y, marker="o", markersize=16, lw=4)
    plt.xticks(x, x_label, rotation=45, fontsize=20, ha="right", color="white")
    # emphasize major versions
    for i in range(len(x_label)):
        if x_label[i].endswith("0"):
            tick = plt.gca().get_xticklabels()[i]
            tick.set_fontsize(28)
            tick.set_color("black")
            plt.vlines(x[i], 0, y[i], linestyles="dashed", lw=3)
    plt.hlines = plt.gca().axhline(y=0, lw=3)
    plt.yticks([10 * t for t in range(11)], [str(10 * t) + "%" for t in range(11)], fontsize=28)
    plt.title(
        f"Cumulative pgrading trend of IR {compability_type.name} from {x_label[0]} to {x_label[-1]}",
        fontsize=40,
        pad=24,
    )
    plt.xlabel("LLVM main version", fontsize=36, labelpad=24)
    plt.ylabel("Cumulative LoC changed", fontsize=32, labelpad=24)
    plt.savefig(path.join("./figures", f"{compability_type.name}.png"))


def run(begin: str, end: str, repo_path: str):
    shutil.rmtree("./data", ignore_errors=True)
    makedirs("./data")
    # get LLVM tags at each run
    sp.run(["./scripts/tag.sh", repo_path])
    # incrementally compare between tags within given range and update tags.txt
    with open("./data/tags.txt", "r") as f:
        tags = f.read().splitlines()[::-1]
    tags = tags[tags.index(begin) : tags.index(end) + 1]
    with open("./data/tags.txt", "w") as f:
        f.write("\n".join(tags))
    # compare all files between tags
    for i in range(len(tags) - 1):
        for file in IR_files:
            sp.run(["./scripts/compare.sh", tags[i], tags[i + 1], file[0], repo_path])
    shutil.rmtree("./figures", ignore_errors=True)
    makedirs("./figures")
    plot(CompabilityType.Semantic)
    plot(CompabilityType.API)
    plot(CompabilityType.Textual)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overall script")
    parser.add_argument("--begin", type=str, help="first tracking tag", default="llvmorg-3.6.0")
    parser.add_argument("--end", type=str, help="last tracking tag", default="llvmorg-16.0.0")
    parser.add_argument("--repo_path", type=str, help="path to the LLVM repository", required=True)
    args = parser.parse_args()
    run(args.begin, args.end, args.repo_path)
